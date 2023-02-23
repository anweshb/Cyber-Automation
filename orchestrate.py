from datetime import datetime
import time
import os
import zipfile
from zipfile import ZipFile
import subprocess
import argparse
import psutil

#USER CONFIGURATIONS : 
default_size = 2e+6                 #default storage size (2MB)
default_check_interval = 5          #default time interval to sleep between size checks
default_config_file = "config.pmc"    #Default PROCMON configuration file
procmon_location = "C:/Users/tingwei/Desktop/ProcessMonitor/Procmon.exe"    #default procmon location

#Setting up command line integration
parser = argparse.ArgumentParser()

parser.add_argument("-s","--SIZE_LIMIT", default = default_size, required = False, help = "Size limit in bytes", type = float)
parser.add_argument("-i", "--CHECK_INTERVAL", default = default_check_interval, required = False, help = "Check interval in seconds", type = int)
parser.add_argument("-c", "--CONFIG_FILE", default = default_config_file, required = False, help = "Location to  .pmc file", type = str)
args = parser.parse_args()

SIZE_LIMIT = args.SIZE_LIMIT   ##In bytes
CHECK_INTERVAL = args.CHECK_INTERVAL ##In seconds
CONFIG_FILE = args.CONFIG_FILE

log_dir = "logs\\"

#Make logs folder, skip if it exists
try:
    os.mkdir(log_dir)
except FileExistsError:
    pass


def check_size(file :str , size_limit : int):

    ## Check if current size is greater than required
    if os.path.getsize(file) > size_limit:
        return True
    else:
        False



def run(size_limit, check_interval):

    try:
        while True:
            
            time_label =  str(datetime.strftime(datetime.now(),"%H-%M-%S-%m-%d-%Y"))
            PML_LOG = log_dir + 'logfile-' + time_label + ".pml"
            CSV_LOG = PML_LOG.replace('.pml','.csv')
            ZIP_NAME =  CSV_LOG.replace('.csv', '.zip')

            
            ## Starting run_procmon.ps1
            run_procmon = subprocess.Popen(['powershell.exe', '-File','run_procmon.ps1', procmon_location, CONFIG_FILE, PML_LOG])
            # time.sleep(15)

            ## Checking size limit in intervals
            while not check_size(PML_LOG, size_limit):
                # print("SLEEPING")
                time.sleep(check_interval)

            ## Stopping tracing on Procmon
            stop_trace = subprocess.Popen(['powershell.exe', '-File', 'stop_trace.ps1', procmon_location])
            print("TERMINATED")
            time.sleep(15)
            convert_pml_csv = subprocess.Popen(['powershell.exe', '-File', 'convert-pml-csv.ps1', procmon_location, PML_LOG, CSV_LOG])      
            convert_pml_csv.communicate()

            # time.sleep(10)

            ## Zipping the logfile then removing the original logfile
            zip_file = ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED)
            zip_file.write(CSV_LOG, arcname=os.path.basename(CSV_LOG))
            os.remove(PML_LOG)
            os.remove(CSV_LOG)
            break
    
    except KeyboardInterrupt:
        to_kill = ['Procmon.exe', 'Procmon64.exe']
        
        for proc in psutil.process_iter():
            if proc.name() in to_kill:
                proc.kill()


run(SIZE_LIMIT, CHECK_INTERVAL)




    







