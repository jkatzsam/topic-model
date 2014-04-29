#Julian Katz-Samuels
#April 25th, 2014

"""
This file uses the gensim module to topic model 
a corpus. 
"""

#third party modules
import gensim, collections, csv, scipy.stats

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

def find_n_best_words(n, word_top_mat):
	"""
	Input:
		n: number of indices to output
		word_top_mat: term topic matrix

	Output:
		returns the indices of best n words per topic
	"""
	ranking = np.argsort(word_top_mat, 0)
	best = ranking[-n:, :]

	return np.unique(best)

def retain_n_best_words(best_indices, word_top_mat):
	"""
	Input:
		best_indices: indices of the words to retain
		word_top_mat: term topic matrix

	Output:
		returns the indices of best n words per topic
	"""
	return word_top_mat[best_indices, :]

def obtain_new_word_ids(indices, old_ids):
	"""
	Input:
		indices: indices of the words to retain
		model: the model generated from gensim

	Output:
		returns a dictionary from numbers (row number of matrix)
		to words (word that row corresponds to)
	"""
	#get correspondence between numbering and new ids
	new_ids = {}
	index_counter = 0
	if type(indices) is not list:
		for index in indices.tolist():
			new_ids[index_counter] = old_ids[index]
			index_counter += 1
		return new_ids
	elif type(indices) is list:
		for index in indices:
			new_ids[index_counter] = old_ids[index]
			index_counter += 1
	return new_ids


def order_words_vis(word_top_mat):
	
	num_words, num_topics = word_top_mat.shape
	ordered_words = []
	words_included = set()
	word_top_mat_t = word_top_mat.T.copy()
	new_nonzero_elements = []
	while len(ordered_words) < num_words and \
		(ordered_words == [] or new_nonzero_elements != old_nonzero_elements):

		# print "dimensions of matrix: " + str(word_top_mat_t.shape)

		old_nonzero_elements = new_nonzero_elements

		#calculate means ignoring 0s
		means = np.array([np.mean([x for x in s if x]) for s in word_top_mat_t])

		try:	
			topic = np.nanargmax(means)
		except:
			break


		# print "max mean: " + str(np.nanmax(means))
		# print "max topic: " + str(topic)
		# print "nonzero means: " + str(means[np.nonzero(means)[0]])

		#grab non_zero_elements and add if not already included
		new_nonzero_elements = np.nonzero(word_top_mat[:, topic])[0].tolist()
		elements_to_add = [x for x in new_nonzero_elements if x not in words_included]

		#update order of words and words already included lists
		ordered_words.extend(elements_to_add)
		words_included.update(elements_to_add)


		#delete words already counted from matrix
		word_top_mat_t[:, new_nonzero_elements] = np.zeros((num_topics, len(new_nonzero_elements)))

		# print "new matrix segment : " + str(word_top_mat_t[:, new_nonzero_elements])

		# print "condition 1: " + str(len(ordered_words) < num_words)
		# print new_nonzero_elements
		# print old_nonzero_elements
	if len(ordered_words) < num_words: 
		set_ordered_words = set(ordered_words)
		all_words = set(range(num_words))
		remain = all_words.difference(set_ordered_words)
		ordered_words.extend(list(remain))
		return ordered_words
	else:
		return ordered_words

def permuted_matrix(word_top_mat, ordering):
	num_words, num_topics = word_top_mat.shape

	#allocate space for new matrix
	new_matrix = np.zeros((num_words, num_topics))

	row_counter = 0
	for row in ordering:
		new_matrix[row_counter, :] = word_top_mat[row, :]
		row_counter += 1

	return new_matrix

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

	print "final matrix sum: " + str(np.sum(word_top_mat))

	word_top_mat_best_tops = take_n_best_topics(num_topics, word_top_mat)

	print "final matrix sum: " + str(np.sum(word_top_mat_best_tops))
	
	#grab indices of words to retain
	best_indices = find_n_best_words(num_words, word_top_mat_best_tops)

	#obtain new word_ids for downsized matrix
	model_ids = model.__dict__['id2word']
	new_ids = obtain_new_word_ids(best_indices, model_ids)

	print "new_ids: " + str(new_ids)

	#change matrix
	word_top_mat_best = retain_n_best_words(best_indices, word_top_mat_best_tops)

	print "final matrix sum: " + str(np.sum(word_top_mat_best))

	#find best ordering of words visualization
	vis_ordering = order_words_vis(word_top_mat_best)

	print "vis_ordering: " + str(vis_ordering)

	#permute matrix according to new order
	final_mat = permuted_matrix(word_top_mat_best, vis_ordering)

	#obtain new word_ids for visualization
	vis_ids = obtain_new_word_ids(vis_ordering, new_ids)

	# print "vis_ids: " + str(vis_ids) 

	#save data
	save_word_topic_distr(final_mat, vis_ids, file_path)

	print "final matrix sum: " + str(np.sum(final_mat))




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

	#create matrix for testing
	word_top_mat = word_topic_matrix(model1)

	#save results
	top_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/gen_sim_data/top_words.csv"

	create_topic_distr(model1, 15, 5, top_words_path)

	# #model
	# model2 = gensim.models.hdpmodel.HdpModel(corp, id2word=diction)

