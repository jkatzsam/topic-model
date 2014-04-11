#Julian Katz-Samuels
#February 21, 2014

"""
This file copies a subset of the data into a folder and 
gunzips each of the .tgz data files. It takes as an argument
the year that should be copied. 
"""
import os, sys
from shutil import copyfile
from subprocess import call

code_path = os.getcwd()
year = sys.argv[1]
nyt_path = "/Volumes/data/nyt_corpus/data/" + year + '/'
raw_path = "/Volumes/data/raw_data/" + year + '/'

#create year directory 
if not os.path.exists(raw_path):
    os.makedirs(raw_path)


for filename in os.listdir(nyt_path):
    copyfile(nyt_path + filename, raw_path + filename)
    os.chdir(raw_path)
    call(["tar", "xzvf", raw_path + filename])
    call(["rm", raw_path + filename])
    
os.chdir(code_path)