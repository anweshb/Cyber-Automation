from datetime import datetime
from hello_world import hello_world
from multiprocessing import Process
import time
import os
from zipfile import ZipFile


SIZE_LIMIT = 2e+6 ## In bytes
CHECK_INTERVAL = 120 ##In seconds

FILE_NAME= str(datetime.strftime(datetime.now(),"%H-%M-%S") + ".log")
ZIP_NAME = FILE_NAME.replace('.log', '.zip')



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
zip_file.write(FILE_NAME)
    





    



