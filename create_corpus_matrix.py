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
		self.triples_id = []
		self.id_doc_map = {} #map from columns of matrix to document ids
		self.doc_id_map = {} #map from document ids to columns of matrix
		self.id_word_map = {} #map from rows of matrix to words
		self.word_id_map = {} #map from words to rows of matrix
		self.num_types = 0 #vocab size of corpus
		self.num_docs = 0 #number of documents in corpus
		self.data_matrix = None
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


	def create_triples(self, threshold = 2):
		"""
		input:
			threshold is the number of articles a word needs
			to appear in for it to be included in the dataset

		Only keep tuples of certain syntatic types; extract
		word that is not Kerry from data

		Note: consider adding some stuff here to filter out some data.
		For example, if an article mentions Kerry once, maybe I should
		just not include it. Or, if there are words that occur very frequently
		or infrequently I should take them out. 
		"""
		#counters for number of unique words and documents
		word_counter = collections.Counter()
		doc_counter = collections.Counter()

		#list for word doc pairs
		word_doc_list = []
		#dict for counting number of documents a word appears in
		word_doc_dict = collections.defaultdict(list)
		for elt in self.data:
			tup, doc_id = ast.literal_eval(elt[3]), elt[7]

			syntax_type = tup[0]
			word_1 = tup[1].encode('ascii','ignore').lower()
			word_2 = tup[2].encode('ascii','ignore').lower()

			if word_1 not in self.words_not_wanted:
				word_doc_list.append([word_1, doc_id, syntax_type])
				word_doc_dict[word_1].append(doc_id)
			if word_2 not in self.words_not_wanted:
				word_doc_list.append([word_2, doc_id, syntax_type])
				word_doc_dict[word_2].append(doc_id)

		#add to unwanted list if a word appears in fewer than 5 documents
		for word, doc in word_doc_dict.iteritems():
			if len(doc) < threshold:
				self.words_not_wanted.append(word)

		print "True vocab size: " + str(len([i for i in map( len, word_doc_dict.values()) if i > 1]))

		for word, doc_id, syn_rel in word_doc_list:
			#grab tuples of specific syntatic types
			if (containment(self.syn_types, syn_rel) 
					and word not in self.words_not_wanted):
				self.triples.append([word, doc_id, 0])
				word_counter[word] += 1
				doc_counter[doc_id] += 1

		self.num_types = len(word_counter)
		self.num_docs = len(doc_counter)

		#create ids for data
		self.vocab_size = len(word_counter)
		self.doc_size = len(doc_counter)

		#create map
		words = word_counter.keys()
		docs = doc_counter.keys()

		incrementer = 0
		for doc in docs:
			self.id_doc_map[incrementer] = doc
			self.doc_id_map[doc] = incrementer
			incrementer += 1

		incrementer = 0
		for word in words:
			self.id_word_map[incrementer] = word
			self.word_id_map[word] = incrementer
			incrementer += 1

		for triple in self.triples:
			triple_id = [self.word_id_map[triple[0]], self.doc_id_map[triple[1]]] + [0]
			self.triples_id.append(triple_id)


	def create_matrix(self):
		self.matrix = np.zeros((self.vocab_size, self.doc_size))
		for word, doc, topic in self.triples_id:
			self.matrix[word, doc] += 1

	def word_variance(self):
		return np.var(self.matrix, 1)




#Development Testing
if __name__ == "__main__":
	file_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Data/test_data/tuples_v1.csv"
	stop_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/common-english-words.csv"


	test = Corpus(file_path, stop_words_path)
	test.read_data()
	test.create_triples()
	test.create_matrix()

