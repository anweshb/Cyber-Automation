from datetime import datetime
from hello_world import hello_world
import time
import os
from zipfile import ZipFile

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-s","--SIZE_LIMIT", default = 2e+6, required = False, help = "Size limit in bytes", type = float)
parser.add_argument("-i", "--CHECK_INTERVAL", default = 120, required = False, help = "Check interval in seconds", type = int)

args = parser.parse_args()

SIZE_LIMIT = args.SIZE_LIMIT   ##In bytes
CHECK_INTERVAL = args.CHECK_INTERVAL ##In seconds

log_dir = "logs/"

FILE_NAME= log_dir + 'Zipped-SCADA-traces-' + str(datetime.strftime(datetime.now(),"%m-%d-%Y") + ".log")
ZIP_NAME =  FILE_NAME.replace('.log', '.zip')



print("FILENAME:",FILE_NAME)


def check_size(file :str , size_limit : int):

    ## Check if current size is greater than required
    if os.path.getsize(file) > size_limit:
    
        return True
    
    else:
        False

def size_loop(file, size_limit, check_interval):

    ## Creating an empty file
    hello_world(file, make_new = True)

    while not check_size(file, size_limit):

        ## We only check file size every few seconds
        t_end = time.time() + check_interval
        
        while time.time() < t_end:
            hello_world(file)



size_loop(file = FILE_NAME, size_limit = SIZE_LIMIT, check_interval = CHECK_INTERVAL)

##Zipping the file
zip_file = ZipFile(ZIP_NAME, 'w')
zip_file.write(FILE_NAME, arcname=os.path.basename(FILE_NAME))
os.remove(FILE_NAME)





    



