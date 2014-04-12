#Julian Katz-Samuels
#March 29th, 2013

"""
This file creates a matrix representation of 
corpus.
"""

#modules
import numpy as np
import csv, ast, collections

#helper functions
def containment(l1, l2):
	for elt in l1:
		if elt in l2:
			return True
	return False


class Corpus:
	
	def __init__(self, file, stop_words_file):
		self.file = file
		self.stop_words_file = stop_words_file
		self.data = []
		self.triples = []
		self.filtered_data = [] #TODO QUESTION: is this adding too much to class? 
		self.matrix = np.zeros((1,1))
		self.col_doc_map = {} #map from columns of matrix to document ids
		self.doc_col_map = {} #map from document ids to columns of matrix
		self.row_word_map = {} #map from rows of matrix to words
		self.word_row_map = {} #map from words to rows of matrix
		self.vocab_size = 0 #vocab size of corpus
		self.doc_size = 0 #number of documents in corpus
		self.syn_types = ['nsubj', 'agent', 'dobj', 'nsubjpass', 
						'iobj', 'prep_', 'appos', 'amod', 'nn']
		self.words_not_wanted = ["john", 
								"kerry", 
								"george", 
								"bush", 
								"edwards", 
								"dick", 
								"cheney",
								"mr.",
								"w.",
								"kittles"]

	def read_data(self):
		"""
		Read data from .csv file
		"""
		self.data = [] #make sure data field is empty
		with open(self.file, 'rb') as file:
			next(file)
			reader = csv.reader(file)
			for row in reader:
				self.data.append(row)
		with open(self.stop_words_file) as file:
			reader = csv.reader(file)
			for row in reader:
				self.words_not_wanted.extend(row)


	def create_triples(self):
		"""
		Only keep tuples of certain syntatic types; extract
		word that is not Kerry from data
		"""
		#counters for number of unique words and documents
		word_counter = collections.Counter()
		doc_counter = collections.Counter()
		for elt in self.data:
			tup, doc_id = ast.literal_eval(elt[3]), elt[7]
			#grab tuples of specific syntatic types
			if containment(self.syn_types, tup):
				#grab the word that is not among words I don't want
				#make into LOWERCASE string (from unicode)
				#make the doc_id an int to sort the list later
				word_1 = str(tup[1]).lower()
				word_2 = str(tup[2]).lower()
				if word_1 not in self.words_not_wanted:
					self.triples.append([(word_1, doc_id, 0)])
					word_counter[word_1] += 1
					doc_counter[doc_id] += 1
				if word_2 not in self.words_not_wanted:
					self.triples.append([(word_2, doc_id, 0)])
					word_counter[word_2] += 1
					doc_counter[doc_id] += 1
		self.vocab_size = len(word_counter)
		self.doc_size = len(doc_counter)












#Development Testing
if __name__ == "__main__":
	file_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Data/test_data/tuples_v1.csv"
	stop_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/common-english-words.csv"


	test = Corpus(file_path, stop_words_path)
	test.read_data()
	test.create_triples()

