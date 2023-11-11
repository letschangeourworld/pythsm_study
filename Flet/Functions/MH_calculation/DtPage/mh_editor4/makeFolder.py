
import os 

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    except OSError:
        print('Error: Creating directory. ' +  directory) 
    

###############


import os

path = './projects'

try:
    os.mkdir(path)
    print("Folder %s created!" % path)
except FileExistsError:
    print("Folder %s already exists" % path)
