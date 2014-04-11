#Julian Katz-Samuels
#February 22, 2014

"""
This file calls the other scripts passing main arguments
to them. 
"""

import argparse, os
from subprocess import call

#parse arguments
parser = argparse.ArgumentParser(description='Process year and a list of keywords')
parser.add_argument('year', metavar='year', type=str, nargs=1,
                   help='a year string between 1987 and 2007')
parser.add_argument('keywords', metavar='keywords', type=str, nargs='+',
                   help='A collection of keywords')

args = parser.parse_args()
year = args.year[0]
keywords = args.keywords

#home path
code_path = os.getcwd()

#copy files
copy_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/data_management/move_data"

os.chdir(copy_path)
call(["python", "move_data_v2.py", year])


#convert files
convert_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/data_management/convert_files"

os.chdir(convert_path)
call(["python", "convert_files_v8.py", year] + keywords)


#parse text files
parse_text_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/data_management/parse_text_files"

os.chdir(parse_text_path)
call(["python", "parse_text_files_v3.py", year])


#convert parsed text to json
convert_parsed_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/data_management/parsed_text_to_json"

os.chdir(convert_parsed_path)
call(["python", "parsed_text_to_json_v2.py", year])


#create_tuples
create_tuples_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/data_management/create_tuples"

os.chdir(create_tuples_path)
call(["python", "create_tuples_v3.py", year] + keywords)


#return to directory of this script
os.chdir(code_path)
