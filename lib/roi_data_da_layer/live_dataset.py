# --------------------------------------------------------
# Live Dataset
# Written by Jerome Mutgeert
# --------------------------------------------------------

"""

"""

import time
import os

TARGET_DATA_PATH = "./TargetDataLoaderProcess/{}"
PYTHON3 = os.environ['PYTHON3'] #= "/home/jerome/anaconda3/envs/rl/bin/python"

# counter txt's interface:
def update_read(read):
    tempfile = TARGET_DATA_PATH.format("read_temp.txt")
    file = TARGET_DATA_PATH.format("read.txt")
    with open(tempfile,'w') as f:
        f.write(str(read))
        f.flush()
        os.fsync(f.fileno())
    # atomic:
    os.rename(tempfile,file)

def get_fetched():
    with open(TARGET_DATA_PATH.format("fetched.txt"),'r') as f:
        numstr = f.read()
    return int(numstr)

def target_file_streamer():
    
    num = 0
    fetched = 0
    read = 0
    
    # Trigger crash of possible previous running data loader process:
    update_read(read)
    time.sleep(.5)
    
    # Make sure we do not read from an old version of fetched.txt: write 0
    with open(TARGET_DATA_PATH.format("fetched.txt"),'w') as f:
        f.write(str(0))
        f.flush()
        os.fsync(f.fileno())
    
    # start data loader process:
    os.chdir(TARGET_DATA_PATH.format(""))
    os.system(" ".join([PYTHON3,"data_loader.py",'&']))
    os.chdir("..")
    
    while True:
        
        # Ensure the file 'target_<num>.jpg" is loaded:
        if not (fetched > num):
            fetched = get_fetched()
        while not (fetched > num):
            time.sleep(.05) #query with 20 Hz untill the file(s) is (are) loaded.
            fetched = get_fetched()
        
        filepath = TARGET_DATA_PATH.format("target_{}.jpg".format(num))
        yield filepath
        
        read += 1
        update_read(read)
        
        num += 1