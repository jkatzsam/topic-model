#Julian Katz-Samuels
#February 22, 2014

"""
This file calls the other scripts passing main arguments
to them. 
"""

import argparse, os

#custom modules
import move_data, convert_files, parse_text_files, parsed_text_to_json, create_tuples


#parse arguments
parser = argparse.ArgumentParser(description='Process year and a list of keywords')
parser.add_argument('year', metavar='year', type=str, nargs=1,
                   help='a year string between 1987 and 2007')
parser.add_argument('keywords', metavar='keywords', type=str, nargs='+',
                   help='A collection of keywords')

args = parser.parse_args()
year = args.year[0]
keywords = args.keywords

#Perform analysis

#copy files
move_data.move_data(year)

#convert files
convert_files.convert_files(year, keywords)

#parse text files
parse_text_files.parse_text_files(year)

#convert parsed text to json
parsed_text_to_json.parsed_text_to_json(year)

#create_tuples
uni_keywords = map(unicode, keywords)
#grab data for tuples
article_data = create_tuples.create_tuples(year, uni_keywords)
#write data for tuples
create_tuples.write(article_data)

