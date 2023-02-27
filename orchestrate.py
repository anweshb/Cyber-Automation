from datetime import datetime
import time
import os
import zipfile
from zipfile import ZipFile
import subprocess
import argparse
import psutil
from pathlib import Path
import json


with open('config.json') as config_file:
    data = json.load(config_file)


#USER CONFIGURATIONS : 
default_size = data["size_limit"]                 #default storage size at which we wish to stop writing the log
default_check_interval = data["check_interval"]          #default time interval to sleep between size checks
default_config_file = data["procmon_config_file"]    #Default PROCMON configuration file
procmon_location = data["procmon_location"]    #default procmon location

#Setting up command line integration
parser = argparse.ArgumentParser()

parser.add_argument("-s","--SIZE_LIMIT", default = default_size, required = False, help = "Size limit in megabytes", type = float)
parser.add_argument("-i", "--CHECK_INTERVAL", default = default_check_interval, required = False, help = "Check interval in seconds", type = int)
parser.add_argument("-c", "--CONFIG_FILE", default = default_config_file, required = False, help = "Location to  .pmc file", type = str)
args = parser.parse_args()

SIZE_LIMIT = args.SIZE_LIMIT   ##In megabytes
CHECK_INTERVAL = args.CHECK_INTERVAL ##In seconds
CONFIG_FILE = args.CONFIG_FILE

log_dir = "logs\\"

#Make logs folder, skip if it exists
try:
    os.mkdir(log_dir)
except FileExistsError:
    pass

global user_terminate_action #This is to enable graceful or ungraceful shutdown of the program

user_terminate_action = 0

def check_size(file :str , size_limit : int):

    ## Check if current size is greater than required
    if os.path.getsize(file) > size_limit * 1_000_000:
        return True
    else:
        False


def poll_if_used_by_process(file_path):
    ## Function to wait until a file is stopped being used by ongoing processes
    while True:
                for proc in psutil.process_iter(['name','open_files']):
                    try:
                        for file in proc.open_files():
                            if file.path == file_path:
                                time.sleep(1)
                            else:
                                continue
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                        
                break


def is_procmon_running():
    for p in psutil.process_iter(['name']):
        if p.info['name'] in ['Procmon.exe', 'Procmon64.exe']:
            return True
    return False

def setup_and_trace():

    time_label =  str(datetime.strftime(datetime.now(),"%H-%M-%S-%m-%d-%Y"))
    CURRENT_PML_LOG = log_dir + 'logfile-' + time_label + ".pml"
    CURRENT_CSV_LOG = CURRENT_PML_LOG.replace('.pml','.csv')
    CURRENT_ZIP_NAME =  CURRENT_CSV_LOG.replace('.csv', '.zip')

    
    ## Starting run_procmon.ps1
    run_procmon = subprocess.Popen(['powershell.exe', '-File','run_procmon.ps1', procmon_location, CONFIG_FILE, CURRENT_PML_LOG])
    
    log_file = Path(CURRENT_PML_LOG)
    
    while not log_file.exists():    #This loop is used to verify that Procmon has started logging to the file
        time.sleep(1)
    
    return CURRENT_PML_LOG, CURRENT_CSV_LOG, CURRENT_ZIP_NAME

## This function watches the file size over Procmon tracing instance and when it reaches the size limit, it stops it 
def watch_and_stop(size_limit, check_interval, CURRENT_PML_LOG, CURRENT_CSV_LOG, CURRENT_ZIP_NAME):

    while not check_size(CURRENT_PML_LOG, size_limit):  #This loop checks if the log file has reached its limit
        time.sleep(check_interval)
         
    ## Stopping tracing on Procmon
    stop_trace = subprocess.Popen(['powershell.exe', '-File', 'stop_trace.ps1', procmon_location])
    stop_trace.communicate()    #Some weird inter-process communication, between Python and PowerShell

    while is_procmon_running():
        time.sleep(1)

    COMPLETED_PML_LOG = CURRENT_PML_LOG
    COMPLETED_CSV_LOG = CURRENT_CSV_LOG
    COMPLETED_ZIP_NAME = CURRENT_ZIP_NAME

    return COMPLETED_PML_LOG, COMPLETED_CSV_LOG, COMPLETED_ZIP_NAME


def convert_pml_to_csv_and_zip(PML_LOG, CSV_LOG, ZIP_NAME):
    convert_pml_csv = subprocess.Popen(['powershell.exe', '-File', 'convert-pml-csv.ps1', procmon_location, PML_LOG, CSV_LOG])      
    convert_pml_csv.communicate()
    
    ## Make sure Procmon is done converting .pml to CSV and has let go of the CSV log
    poll_if_used_by_process(CSV_LOG)
    
    ## Zipping the logfile then removing the original logfile
    zip_file = ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED)
    zip_file.write(CSV_LOG, arcname=os.path.basename(CSV_LOG))
    os.remove(PML_LOG)
    os.remove(CSV_LOG)


def run(size_limit, check_interval):

    try:
        procmon_instantiation_counter = 1
        print("Procmon instantiation counter:", procmon_instantiation_counter, str(datetime.strftime(datetime.now(),"%H-%M-%S-%m-%d-%Y")))
        #Start the first/current tracing
        current_pml_log, current_csv_log, current_zip_name = setup_and_trace()
        while True:
                
            completed_pml_log, completed_csv_log, completed_zip_name = watch_and_stop(size_limit, check_interval, current_pml_log, current_csv_log, current_zip_name)
            
            ##Starting the next tracing. We want to start tracing the next instance immediately after the first/current one finishes, i.e. before we start zipping its logs, to minimize missed logs/events
            current_pml_log, current_csv_log, current_zip_name = setup_and_trace()
            procmon_instantiation_counter += 1
            print("Procmon instantiation count:", procmon_instantiation_counter, str(datetime.strftime(datetime.now(),"%H-%M-%S-%m-%d-%Y")))

            ## Make sure Procmon is done using the completed pml log
            poll_if_used_by_process(completed_pml_log)
            
            ## Converted completed pml to csv and zip it
            convert_pml_to_csv_and_zip(completed_pml_log, completed_csv_log, completed_zip_name)
            

            #completed_pml_log, completed_csv_log, completed_zip_name = watch_and_stop(size_limit, check_interval, current_pml_log, current_csv_log, current_zip_name)

            if user_terminate_action > 0:
                break
    
    except KeyboardInterrupt:
        
        #global user_terminate_action

        user_terminate_action += 1
        print("Now gracefully shutting down SCADA Dynamic Analysis..... Wait a minute, or press Ctrl C again to shut down ungracefully")


        if user_terminate_action > 1:
            to_kill = ['Procmon.exe', 'Procmon64.exe']
        
            ## Shutdown procmon instances upon Keyboard Interrupt
            for proc in psutil.process_iter():
                if proc.name() in to_kill:
                    proc.kill()

        
        
        

run(SIZE_LIMIT, CHECK_INTERVAL)




    






