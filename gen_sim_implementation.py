#Julian Katz-Samuels
#April 25th, 2014

"""
This file uses the gensim module to topic model 
a corpus. 
"""

#third party modules
import gensim, collections, csv

import numpy as np
import scipy as sp

#custom modules
from create_corpus_matrix import Corpus

#functions
def create_new_doc_rep(ls):
	"""
	Input:
		List of 2-d tuples where the first dimension
		is the word (string), and the second is the 
		doc_id (int). 

	Output:
		Returns dictionary of lists where each internal list
		has words from a particular document. 
	"""
	docs = collections.defaultdict(list)
	for elt in ls:
		word = elt[0]
		doc = elt[1]
		docs[doc].append(word)
	return docs


def write_rep(dic, file):
	"""
	Input:
		Dictionary with value as list and key as number.
		File to write

	Output:
		Return nothing

		Writes file where each line belongs to particular
		key in dictionary.
	"""
	with open(file, 'w') as outfile:
		for doc, words in dic.iteritems():
			for word in words:
				outfile.write(str(word) + ' ')
			outfile.write('\n')

#TODO: Maybe save corpus and dictionary, esp. if they take a while to make

#create dictionary
#TODO: think about how removing words here interacts with what I do in my other file

def create_corpus_dictionary(infile, outfile):
	dictionary = gensim.corpora.Dictionary(line.lower().split() for line in open(infile))
	# once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
	# dictionary.filter_tokens(once_ids) # remove stop words and words that appear only once
	dictionary.compactify() # remove gaps in id sequence after words that were removed
	dictionary.save(outfile)
	return dictionary


#create corpus
def create_corpus(dictionary, infile, outfile):
	corpus = [dictionary.doc2bow(text.split()) for text in open(infile)]
	gensim.corpora.MmCorpus.serialize(outfile, corpus) # store to disk, for later use

def load_dictionary(dict):
	return gensim.corpora.Dictionary.load(dict)

def load_corpora(corp):
	return gensim.corpora.MmCorpus(corp)

def word_topic_matrix(model, word_num = 10):
	"""
	Input: 
		model: ldamodel
		word_num: number of top most probable words per topic
		topic_num: number of topics to inspect

	Output:
		dictionary with (word, topic) tuple as key and probability as value 
		set with all the unique words
	"""
	topic_num = model.num_topics
	word_topics = model.show_topics(topics = topic_num, topn = word_num)
	
	#change topic_num to be the total number of topics
	if topic_num == -1:
		topic_num == len(word_topics)

	words_id = {}
	id_words = {}
	word_top = {}
	topics = collections.defaultdict(list)

	top_counter = 0
	word_id_counter = 0
	for top in word_topics:
		for word_prob in top.split(" + "):
			word = word_prob.split("*")[1]
			prob = word_prob.split("*")[0]

			word_top[(word, top_counter)] = float(prob)
			topics[top_counter].append(word)
			if word not in words_id:
				words_id[word] = word_id_counter
				id_words[word_id_counter] = word
				word_id_counter += 1
		top_counter += 1

	#create matrix
	#TODO: why are there some columns with less than 10 nonzero entries?
	all_word_num = len(words_id)
	word_top_mat = np.zeros((all_word_num, topic_num))
	for top in range(topic_num):
		words = topics[top]
		print len(words)
		for word in words:
			#grab probability of word in topic
			prob = word_top[(word, top)]
			#grab id for word
			word_id = words_id[word]
			#create slot for matrix
			word_top_mat[word_id, top] = prob
			# print "added to matrix"
	return word_top_mat, id_words

def save_word_topic_as_matrix(word_top_mat, id_words, file_path):
	"""
	Input:
		word_top_mat: matrix where rows are words, columns topics and entries probability
		word_collector: set with all the unique words
		file_path: location to save file
	"""
	with open(file_path, 'w') as ofile:
		writer = csv.writer(ofile)
		num_rows, num_cols = word_top_mat.shape

		#create header
		header = ["words"] + ["topic " + str(i) for i in range(num_cols)]
		writer.writerow(header)
		for row in range(num_rows):
			writer.writerow([id_words[row]] + word_top_mat[row,:].tolist())


def save_word_topic_distr(word_top_mat, id_words, file_path):
	"""
	Input:
		word_top_mat: matrix where rows are words, columns topics and entries probability
		word_collector: set with all the unique words
		file_path: location to save file
	"""
	with open(file_path, 'w') as ofile:
		writer = csv.writer(ofile)
		num_rows, num_cols = word_top_mat.shape

		#create header
		header = ["words", "topic", "probability"]
		writer.writerow(header)
		for row in range(num_rows):
			probs = word_top_mat[row,:].tolist()
			top_counter = 0
			for prob in probs:
				writer.writerow([id_words[row], top_counter, prob])
				top_counter += 1
			top_counter = 0




#Development Testing
if __name__ == "__main__":
	file_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Data/test_data/tuples_v1.csv"
	stop_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/common-english-words.csv"

	test = Corpus(file_path, stop_words_path)
	test.read_data()
	test.create_triples()

	tuples = [i[0:2] for i in test.triples]

	rep_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/gen_sim_data/documents_representation.txt"
	corpora_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/gen_sim_data/corpora.mm"
	dictionary_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/gen_sim_data/dictionary.dict"

	#create new representation
	new_rep = create_new_doc_rep(tuples)

	#save rep file
	write_rep(new_rep, rep_path)
	dic = create_corpus_dictionary(rep_path, dictionary_path)
	create_corpus(dic, rep_path, corpora_path)

	#load dictionary
	diction = load_dictionary(dictionary_path)

	#load corpora
	corp = load_corpora(corpora_path)

	#model
	model1 = gensim.models.ldamodel.LdaModel(corp, id2word=diction, num_topics=150)

	word_top_mat, id_words = word_topic_matrix(model1, word_num = 2)

	#save results
	top_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/gen_sim_data/top_words.csv"
	save_word_topic_distr(word_top_mat, id_words, top_words_path)

	# #model
	# model2 = gensim.models.hdpmodel.HdpModel(corp, id2word=diction)

