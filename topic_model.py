#Julian Katz-Samuels
#March 29th, 2013

"""
This file uses Gibbs sampling to fit the topic
model to a matrix representation of the data.
"""

"""
Sources:
http://bcomposes.wordpress.com/2012/05/29/gibbs-sampler-for-toy-topic-model-example/

"""


"""
Extensions: 
-Figure out how to discard values of iterations before some 
point so that initial values do not contaminate results.

-figure out how to sample only certain values of the iterations
to deal with the problem of autocorrelation.

"""


"""
parameter settings:
alpha = 50 / K 
beta = 0.1
"""


#modules
import numpy as np
import scipy as sp
import csv, math

#custom_modules
from create_corpus_matrix import Corpus

#helper functions
def test_not_neg(a):
	if np.amin(a) >= 0:
		print("No problem here")
	else:
		print("problem with " + str(a))
		print(np.amin(a))

def save_data(data, header, outfile):
	with open(outfile, 'w') as outfile:
		writer = csv.writer(outfile, delimiter=',')
		writer.writerow(header)
		for line in data:
			writer.writerow(line)


#class
class TopicModel:

	def __init__(self, corpus, num_topics, beta):
		self.alpha = float(50) / num_topics #scalar
		self.beta = beta #scalar
		self.num_types = corpus.num_types
		self.num_docs = corpus.num_docs
		self.id_doc_map = corpus.id_doc_map #map from columns of matrix to document ids
		self.doc_id_map = corpus.doc_id_map #map from document ids to columns of matrix
		self.id_word_map = corpus.id_word_map #map from rows of matrix to words
		self.word_id_map = corpus.word_id_map #map from words to rows of matrix
		self.num_topics = num_topics
		self.data = corpus.triples_id #triples contain: token, document, topic assignment
		self.doc_top_count = np.zeros((self.num_docs, self.num_topics)) #the number of words assigned to topic k in document d
		self.word_top_count = np.zeros((self.num_types, self.num_topics)) #the number of times word w is assigned to topic k
		self.top_count = np.zeros((1, self.num_topics)) #the total number of times any word is assigned to topic k
		self.top_lag = np.zeros((1, self.num_topics)) #lag count for topic
		self.prob = np.zeros((1,num_topics)) #probability of topics
		self.doc_top_distr = np.zeros((self.num_docs, self.num_topics)) #doc topic distributions: estimated using counts from Gibbs sampler
		self.doc_top_lag = np.zeros((self.num_docs, self.num_topics)) #counts using lag and burn
		self.word_top_distr = np.zeros((self.num_types, self.num_topics)) #word number distributions
		self.word_top_lag = np.zeros((self.num_types, self.num_topics)) #word topic distributions: sampled from gibbs sampler using lag and burn
		self.log_likelihood = None #log_likelihood

		#randomly initialize word to topic assignments
		for i in range(len(self.data)):
			topic_assignment = np.random.random_integers(0, self.num_topics - 1)
			self.data[i][2] = topic_assignment

		#increment words_top_count, top_cont, doc_top_count
		for triple in self.data:
			word, doc, topic = triple
			self.word_top_count[word, topic] += 1 
			self.doc_top_count[doc, topic] += 1
			self.top_count[0, topic] += 1

	def words_in_doc(self, doc):
		"""
		return words in doc
		"""
		return np.nonzero(self.data[:, doc])[0].tolist()


	def docs_of_word(self, word):
		"""
		return docs that word appears in
		"""
		return np.nonzero(self.data[word, :])[0].tolist()


	def gibbs(self, num_iterations = 3000, burn = 750, lag = 50):
		"""
		input: 
			num_iterations: number of iterations to perform the algorithm
			burn: number of iterations to wail until collecting samples
			lag: number of iterations to wait between samples to lessen autocorrelation


		updates:
			the gibbs sampler
		"""
		iteration = 0
		lag_counter = 0
		while iteration < num_iterations:
			iteration += 1
			print("iteration " + str(iteration))
			for i in range(len(self.data)):
				word, doc, topic_old = self.data[i]
				#decrement
				#I shouldn't need this max thing, but can't figure out why I sometimes get -1. TODO: fix later. 
				self.doc_top_count[doc, topic_old] -= max(self.doc_top_count[doc, topic_old] - 1, 0) 
				self.word_top_count[word, topic_old] -= 1 
				self.top_count[0, topic_old] -= 1

				# calculate topic probabilities
				for k in range(self.num_topics):
					self.prob[0, k] = (float(self.doc_top_count[doc, k] + self.alpha) /  \
										(self.doc_top_count[doc, k] + \
											self.num_topics * self.alpha)) * \
									(float(self.word_top_count[word, k] + self.beta) / \
									(self.top_count[0, k] + self.beta * self.num_types))
				
				#get rid of zero values
				smoothed_prob = np.maximum(self.prob, np.zeros((1,self.num_topics)) + .000001)					

				#sample and assign a topic assignment for the word
				normalized_prob = smoothed_prob[0,:-1] / smoothed_prob.sum()
				topic_list = np.random.multinomial(1, normalized_prob.tolist(), 1) 
				topic_new = np.nonzero(topic_list)[1][0]
				self.data[i] = [word, doc, topic_new]

				if lag_counter >= lag:
					self.word_top_lag[word, topic_new] += 1
					self.doc_top_lag[doc, topic_new] += 1
					self.top_lag[0, topic_new] += 1

				#increment
				self.doc_top_count[doc, topic_new] += 1
				self.word_top_count[word, topic_new] += 1
				self.top_count[0, topic_new] += 1
			if iteration >= burn:
				lag_counter += 1


	def comp_word_top(self):
		"""
		compute the word_top_distr
		"""
		for topic in range(self.num_topics):
			for word in range(self.num_types):
				self.word_top_distr[word, topic] = \
									float(self.word_top_lag[word, topic] + self.beta) \
										/ (self.top_lag[0,topic] + self.beta * self.num_types)
				# print("word_topic distribution: " + str(self.word_top_distr[word, topic]))


	def comp_doc_top(self):
		"""
		compute the cod_top_distr
		"""
		for topic in range(self.num_topics):
			for doc in range(self.num_docs):
				self.doc_top_distr[doc, topic] = \
									float(self.doc_top_lag[doc, topic] + self.alpha) \
										/ (sum(self.doc_top_lag[doc, :]) + self.num_topics * self.alpha)
				print("document topic distribution: " + str(self.doc_top_distr[doc, topic]))


	def comp_likelihood(self):
		"""
		compute the likelihood p(W|t)

		note: Griffiths gives a way to approximate this quantity
		if I need to do this at some point.
		"""
		log_likelihood = 0
		for word in range(self.num_types):
			word_prob = 0
			for topic in range(self.num_topics):
				#probability of word given topic
				word_topic_prob = self.word_top_distr[word, topic]
				for doc in range(self.num_docs):
					topic_prob = self.doc_top_distr[doc, topic]
					word_prob += word_topic_prob * topic_prob
			log_likelihood += math.log1p(word_prob)
		self.log_likelihood = log_likelihood


	def save_data(self, out_path):
		doc_top_distr_list = self.doc_top_distr.tolist()
		with open(out_path + "_num_topics_" + str(self.num_topics) + "_docs.csv", 'w') as outfile:
			writer = csv.writer(outfile, delimiter=',')
			header = ["doc_id"]
			for top in range(self.num_topics):
				header.append("topic " + str(top + 1))
			writer.writerow(header)
			counter = 1
			for line in doc_top_distr_list:
				writer.writerow([counter] + line)
				counter += 1
		word_top_distr_list = self.word_top_distr.tolist()
		with open(out_path + "_num_topics_" + str(self.num_topics) + "_words.csv", 'w') as outfile:
			writer = csv.writer(outfile, delimiter=',')
			header = ["word"]
			for top in range(self.num_topics):
				header.append("topic " + str(top + 1))
			writer.writerow(header)
			counter = 1
			for line in doc_top_distr_list:
				writer.writerow([self.id_word_map[counter]] + line)
				counter += 1



##Functions
def select_model(topics_list, data_matrix, outpath, num_iterations = 3000, burn = 750, lag = 50):
	"""
	Input: 
		list of topic numbers to test
		data_matrix

	Returns:
		list of pairs (list) of topic number and log_likelihood value
	"""
	topic_likelihoods = []
	for topic_num in topics_list:
		print("topic number: " + str(topic_num))
		topic = TopicModel(data_matrix, topic_num, .5)
		topic.gibbs(num_iterations, burn, lag)
		topic.comp_word_top()
		topic.comp_doc_top()
		topic.comp_likelihood()
		topic.save_data(out_path + "topic_num_" + str(topic_num))
		topic_likelihoods.append([topic_num, topic.log_likelihood])
	return topic_likelihoods



##Development Testing
if __name__ == "__main__":
	file_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Data/test_data/tuples_v1.csv"
	out_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/topic_model_data/topic_model"
	stop_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/common-english-words.csv"

	test = Corpus(file_path, stop_words_path)
	test.read_data()
	test.create_triples()


	#object tests
	topic = TopicModel(test, 5, .5)
	topic.gibbs()
	topic.comp_word_top()
	topic.comp_doc_top()
	topic.comp_likelihood()
	print "The log-likelihood is " + str(topic.log_likelihood)
	print "Word topic variance: " + str(np.var(topic.word_top_distr, 0))
	print "Word topic mean: " + str(np.mean(topic.word_top_distr, 0))
	topic.save_data(out_path)

	#print out topic word distribution
	#and document topic distribution matrices
	# print "the document topic distribution matrix \n" + str(topic.doc_top_distr)
	# print "the word topic distribution matrix \n" + str(topic.word_top_distr)



	# #test count matrices
	# test_not_neg(topic.top_count)
	# test_not_neg(topic.doc_top_count) 
	# test_not_neg(topic.word_top_count)


	# #Test Initialization
	# test_init = TopicModel(test.matrix, 5, .1)

	# test_not_neg(test_init.top_count)
	# test_not_neg(test_init.doc_top_count) 
	# test_not_neg(test_init.word_top_count)

	# x = np.zeros((test_init.num_docs, test_init.num_topics))
	# for doc in range(test_init.num_docs):
	# 	doc_word_list = test_init.words_in_doc(doc)
	# 	for word in doc_word_list:
	# 		topic = test_init.word_top_assign[0, word]
	# 		x[doc, topic] += 1
	# if np.sum(x - test_init.doc_top_count) == 0:
	# 	print("initialization is not a problem")
	# else:
	# 	print('initialization is a problem')


	# #model selection tests
	# topics_to_check = map(int, np.linspace(2,14, 5))
	# model_select_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/topic_model_data/model_selection_data_v1"
	# model_select_data = select_model(topics_to_check, test, "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/topic_model_data/")
	# save_data(model_select_data, ["number of topics", "log_likelihood"], model_select_path)



