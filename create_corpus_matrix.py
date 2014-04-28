#Julian Katz-Samuels
#March 29th, 2013

"""
This file creates a matrix representation of 
corpus.
"""

#modules
import numpy as np
import csv, ast, collections, dateutil.parser, datetime

#custom modules

#helper functions
def containment(l1, l2):
	for elt in l1:
		if elt in l2:
			return True
	return False

#classes
class Corpus:
	
	def __init__(self, file, stop_words_file, syntax_filter = "all"):
		"""
			input: 
				stop_words_file: .csv of stop words to filter out
				syntax_filter: string that specifies which syntatic category to
								use in making corpus:
									-'all' -> all syntatic types
									-'agent' -> specified by agent list
									-'patient' -> specifed by patient list
									-'attributes' -> specified by attributes list
		"""

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
		self.docid_date_map = {} #doc_id as key, date as value
		self.all_syn_types = ['nsubj', 'agent', 'dobj', 'nsubjpass', 
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
								"kittles",
								"%",
								"ms.",
								"f.",
								"mrs.",
								"a2",
								"a3",
								"a4",
								"a5",
								"a6",
								"a7",
								"a8",
								"a9",
								"a10",
								"a11",
								"a12"]
		self.agent = ['nsubj', 'agent']
		self.patient = ['dobj', 'nsubjpass', 
						'iobj', 'prep_']
		self.attributes = ['appos', 'amod', 'nn']

		#create list of syntatic types to accept
		if syntax_filter == "all":
			self.syntax_filter = self.all_syn_types
		elif syntax_filter == "agent":
			self.syntax_filter = self.agent
		elif syntax_filter == "patient":
			self.syntax_filter = self.patient
		elif syntax_filter == "attributes":
			self.syntax_filter = self.attributes
		else: 
			print "Not a valid syntax filter. \n Using all syntatic types."
			self.syntax_filter = self.all_syn_types


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


	def create_triples(self, lower_threshold = 2, upper_threshold = .60):
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
		doc_word_dict = collections.defaultdict(list)
		for elt in self.data:
			tup, doc_id = ast.literal_eval(elt[3]), elt[7]

			syntax_type = tup[0]
			word_1 = tup[1].encode('ascii','ignore').lower()
			word_2 = tup[2].encode('ascii','ignore').lower()

			if (word_1 not in self.words_not_wanted #check if word is not wanted and if it is a digit
			and not word_1.isdigit()):
				word_doc_list.append([word_1, doc_id, syntax_type])
				word_doc_dict[word_1].append(doc_id)
				doc_counter[doc_id] += 1
			if (word_2 not in self.words_not_wanted
			and not word_2.isdigit()):
				word_doc_list.append([word_2, doc_id, syntax_type])
				word_doc_dict[word_2].append(doc_id)
				doc_counter[doc_id] += 1

		#add to unwanted list if a word appears in fewer than 5 documents
		for word, docs in word_doc_dict.iteritems():
			idf = float(len(docs)) / len(doc_counter) #np.log(float(len(doc)) / len(doc_counter))
			print "idf: " + str(idf)
			print len(docs), word
			if len(docs) < lower_threshold or idf > upper_threshold:
				self.words_not_wanted.append(word)
				for doc in docs:
					doc_counter[doc] -= 1
					if doc_counter[doc] <= 0:
						del doc_counter[doc]

		print "True vocab size: " + str(len([i for i in map( len, word_doc_dict.values()) if i > 1]))

		#reset doc_counter	
		doc_counter = collections.Counter()

		for word, doc_id, syn_rel in word_doc_list:
			#grab tuples of specific syntatic types
			if (containment(self.syntax_filter, syn_rel) 
					and word not in self.words_not_wanted):
				print str(syn_rel)
				self.triples.append([word, doc_id, 0])
				word_counter[word] += 1
				doc_counter[doc_id] += 1

		#calculate number of types and documents
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


	def create_docid_date_map(self):
		self.date_docid_map = []
		for datum in self.data:
			doc, unparsed_date = datum[7], datum[12]
			date = dateutil.parser.parse(unparsed_date).date()
			day = date.timetuple().tm_yday
			if doc in self.doc_id_map:
				doc_id = self.doc_id_map[doc]
				self.docid_date_map[doc_id] = day



#Development Testing
if __name__ == "__main__":
	file_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Data/test_data/tuples_v1.csv"
	stop_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/common-english-words.csv"


	test = Corpus(file_path, stop_words_path, "attributes")
	test.read_data()
	test.create_triples()
	test.create_matrix()
	test.create_docid_date_map()
	

