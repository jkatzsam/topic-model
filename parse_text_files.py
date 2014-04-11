#Julian Katz-Samuels
#February 14th, 2014


"""
This file uses the stanford parser to parse text and title files.
"""

import os, sys
from subprocess import call

"""
Development Notes:

"""

#Specify year to have certain files to parse. 
year = sys.argv[1]

##Go to the directory of the text files
text_path = "/Volumes/data/modified_data/" + year + "/text/"
parsed_path = "/Volumes/data/modified_data/" + year + "/parsed/"

#create parsed folder if it doesn't exist
if not os.path.exists(parsed_path):
	os.makedirs(parsed_path)

#home path
code_path = os.getcwd()

#switch to directory containing parser
os.chdir("/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/stanford-corenlp-full-2014-01-04")

##Create list of files to process
counter = 0
f = open("files_to_process.txt", "wb")
for filename in os.listdir(text_path):
	if filename == ".DS_Store":
		continue

	new_filename = int(filename[:7])
	if new_filename <= 1623010:
		continue

	counter += 1

	#write file containing files to parse
	f.write(text_path + filename + "\n")
	
	if counter >= 40:
		#close file
		f.close()
		
		#call parser
		call(["java", "-cp", "stanford-corenlp-3.3.1.jar:stanford-corenlp-3.3.1-models.jar:xom.jar:joda-time.jar:jollyday.jar:ejml-0.23.jar", \
			"-Xmx3g", "edu.stanford.nlp.pipeline.StanfordCoreNLP", "-filelist", "files_to_process.txt", "-outputDirectory", parsed_path])
		
		#reset counter and open new file
		counter = 0
		f = open("files_to_process.txt", "wb")

#process remaining files
if counter > 0:

	#close file
	f.close()
	
	#call parser
	call(["java", "-cp", "stanford-corenlp-3.3.1.jar:stanford-corenlp-3.3.1-models.jar:xom.jar:joda-time.jar:jollyday.jar:ejml-0.23.jar", \
		"-Xmx3g", "edu.stanford.nlp.pipeline.StanfordCoreNLP", "-filelist", "files_to_process.txt", "-outputDirectory", parsed_path])

#return to directory containing this file
os.chdir(code_path)
