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


	def filter_data(self):
		"""
		Only keep tuples of certain syntatic types; extract
		word that is not Kerry from data
		"""
		for elt in self.data:
			tup, doc_id = ast.literal_eval(elt[3]), elt[7]
			#grab tuples of specific syntatic types
			if containment(self.syn_types, tup):
				#grab the word that is not Kerry
				#make into LOWERCASE string (from unicode)
				#make the doc_id an int to sort the list later
				tup_1 = str(tup[1]).lower()
				tup_2 = str(tup[2]).lower()
				if tup_1 not in self.words_not_wanted:
					self.filtered_data.append([tup_1, int(doc_id)]) 
				if tup_2 not in self.words_not_wanted:
					self.filtered_data.append([tup_2, int(doc_id)])
		#sort filtered data list
		self.filtered_data.sort(key = lambda x: x[1])


	def create_matrix_data_map(self):
		"""
		COunts the number of distinct words, distinct
		articles and forms the matrix_data_map for the
		words and documents
		"""
		#count vocab and doc size
		word_counter = collections.Counter()
		doc_counter = collections.Counter()
		for word, doc_id in self.filtered_data:
			word_counter[word] += 1
			doc_counter[doc_id] += 1
		self.vocab_size = len(word_counter)
		self.doc_size = len(doc_counter)

		#create map
		words = word_counter.keys()
		docs = doc_counter.keys()

		incrementer = 0
		for doc in docs:
			self.col_doc_map[incrementer] = doc
			self.doc_col_map[doc] = incrementer
			incrementer += 1

		incrementer = 0
		for word in words:
			self.row_word_map[incrementer] = word
			self.word_row_map[word] = incrementer
			incrementer += 1


	def create_matrix(self):
		self.matrix = np.zeros((self.vocab_size, self.doc_size))
		for word, doc in self.filtered_data:
			row = self.word_row_map[word]
			col = self.doc_col_map[doc]
			self.matrix[row, col] = 1











#Development Testing
if __name__ == "__main__":
	file_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Data/test_data/tuples_v1.csv"
	stop_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/common-english-words.csv"


	test = Corpus(file_path, stop_words_path)
	test.read_data()
	test.filter_data()
	test.create_matrix_data_map()
	test.create_matrix()
