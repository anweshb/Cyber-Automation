from datetime import datetime
import time
import os
import zipfile
from zipfile import ZipFile
import subprocess
import argparse


#Setting up command line integration
parser = argparse.ArgumentParser()

parser.add_argument("-s","--SIZE_LIMIT", default = 2e+6, required = False, help = "Size limit in bytes", type = float)
parser.add_argument("-i", "--CHECK_INTERVAL", default = 120, required = False, help = "Check interval in seconds", type = int)

args = parser.parse_args()

SIZE_LIMIT = args.SIZE_LIMIT   ##In bytes
CHECK_INTERVAL = args.CHECK_INTERVAL ##In seconds

log_dir = "logs/"

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

    while True:
        
        time_label =  str(datetime.strftime(datetime.now(),"%H-%M-%S-%m-%d-%Y"))
        FILE_NAME= log_dir + 'logfile-' + time_label + ".log"
        ZIP_NAME =  FILE_NAME.replace('.log', '.zip')

        ## Creating an empty file
        
        with open(FILE_NAME, 'w') as fp:
            pass
        
        ## Starting hello_world.py
        p = subprocess.Popen(['python3.9', 'hello_world.py','-f', FILE_NAME])

        ## Checking size limit in intervals
        while not check_size(FILE_NAME, size_limit):
            # print("SLEEPING")
            time.sleep(check_interval)

        ## Ending hello_world.py execution
        p.terminate()
        # print(os.path.getsize(FILE_NAME))
        print("TERMINATED")

        ## Zipping the logfile then removing the original logfile
        zip_file = ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED)
        zip_file.write(FILE_NAME, arcname=os.path.basename(FILE_NAME))
        os.remove(FILE_NAME)
    



run(SIZE_LIMIT, CHECK_INTERVAL)




    







