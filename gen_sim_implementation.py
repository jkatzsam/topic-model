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

def word_topic_matrix(model):
	"""
	Input: 
		model: ldamodel
		word_num: number of top most probable words per topic
		topic_num: number of topics to inspect

	Output:
		word topic matrix
	"""
	topic_num = model.num_topics
	word_topics = model.show_topics(topics = topic_num, topn = -1)

	words_id = {}
	id_words = {}
	word_top = {}
	topics = collections.defaultdict(list)

	#counter for which topic we are on in loop
	top_counter = 0
	#dictionary of words and ids
	id2word = model.id2word.token2id
	all_word_num = len(id2word)
	word_top_mat = np.zeros((all_word_num, topic_num))

	for top in word_topics:
		for word_prob in top.split(" + "):
			word = word_prob.split("*")[1]
			prob = word_prob.split("*")[0]

			print "word: " + str(word)

			word_id = id2word[word]

			print "word_id: " + str(word_id)

			print "prob: " + str(prob)

			word_top_mat[word_id, top_counter] =  float(prob)
		top_counter += 1

	return word_top_mat

def comp_prob_top(word_top_mat):
	p_t = np.sum(word_top_mat, 0)
	return p_t / np.sum(p_t)

def comp_saliency(word_top_mat):
	"""
	Input:
		word_top_mat: term topic matrix

	Output:
		vector of the saliency of each word
	"""

	#compute p(w)
	p_w_unnormalized = np.sum(word_top_mat, 1) 

	p_w = p_w_unnormalized / np.sum(p_w_unnormalized)

	#compute distinctiveness of word
	p_t = comp_prob_top(word_top_mat)
	dist = np.sum(word_top_mat * np.log(np.divide(word_top_mat, p_t) + .0001), 1)

	return p_w * dist


def dist_from_uniform(word_top_mat):
	"""
	Input: 
		word_top_mat: term topic matrix

	Output:
		vector (length of number of topics) that is distance of 
		each topic distribution from the uniform distribution
	"""
	num_words, num_topics = word_top_mat.shape
	#create uniform probability matrix
	unif = np.repeat(np.array([float(1) / num_words]), num_words)

	#calculate kullback keibler divergence
	kullback = np.zeros((1, num_topics))
	for top in range(num_topics):
		kullback[0,top] = sp.stats.entropy(word_top_mat[:, top], unif)
	return kullback


def take_n_best_topics(n, word_top_mat):
	"""
	Input:
		n: number of indices to output
		word_top_mat: term topic matrix

	Output:
		returns the indices of best n topics
	"""
	scores = dist_from_uniform(word_top_mat)
	ranking = np.argsort(scores)
	best = ranking[0, -n:]
	return word_top_mat[:, best]

def take_n_best_words(n, word_top_mat):
	"""
	Input:
		n: number of indices to output
		word_top_mat: term topic matrix

	Output:
		returns the indices of best n words per topic
	"""
	ranking = np.argsort(word_top_mat, 0)
	best = ranking[-n:, :]

	#grab unique indices
	unique_best = np.unique(best)
	return word_top_mat[unique_best, :]



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


def create_topic_distr(model, num_topics, num_words, file_path):
	word_top_mat = word_topic_matrix(model)
	word_top_mat_best_tops = take_n_best_topics(num_topics, word_top_mat)
	word_top_mat_best = take_n_best_words(num_words, word_top_mat_best_tops)

	id_words = model1.id2word.__dict__['id2token']

	save_word_topic_distr(word_top_mat_best, id_words, file_path)




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

	#save results
	top_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/gen_sim_data/top_words.csv"

	create_topic_distr(model1, 30, 5, top_words_path)

	# #model
	# model2 = gensim.models.hdpmodel.HdpModel(corp, id2word=diction)

