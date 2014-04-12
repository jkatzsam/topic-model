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
import csv
import math

#custom_modules
from create_corpus_matrix_v1 import Corpus

#helper functions
def test_not_neg(a):
	if np.amin(a) >= 0:
		print("No problem here")
	else:
		print("problem with " + str(a))
		print(np.amin(a))

def save_data(data, outfile, header):
	with open(outfile, 'w') as outfile:
		writer = csv.writer(outfile, delimiter=',')
		writer.writerow(header)
		for line in data:
			writer.writerow(line)


#class
class TopicModel:

	def __init__(self, matrix, num_topics, beta):
		self.alpha = float(50) / num_topics #scalar
		self.beta = beta #scalar
		self.num_words, self.num_docs = matrix.shape
		self.num_topics = num_topics
		self.data = matrix #words by documents matrix
		self.doc_top_count = np.zeros((self.num_docs, self.num_topics)) #the number of words assigned to topic k in document d
		self.word_top_count = np.zeros((self.num_words, self.num_topics)) #the number of times word w is assigned to topic k
		self.top_count = np.zeros((1, self.num_topics)) #the total number of times any word is assigned to topic k
		self.prob = np.zeros((1,num_topics)) #probability of topics
		self.doc_top_distr = np.zeros((self.num_docs, self.num_topics)) #document topic distributions
		self.word_top_distr = np.zeros((self.num_words, self.num_topics)) #word number distributions
		self.log_likelihood = 0 #log_likelihood

		#Randomly initialize word to topic assignments
		self.word_top_assign = np.random.random_integers(0, self.num_topics-1,(1, self.num_words)) #current assignment for each of the N words in the corpus

		#increment words_top_count
		for word in range(self.num_words):
			topic = self.word_top_assign[0, word]
			self.word_top_count[word, topic] = sum(self.data[word, :])

		#increment doc_top_count
		for doc in range(self.num_docs):
			for top in range(self.num_topics):
				#make a matrix of 0 1s where 1 if it is the topic and 0 otherwise
				topic_vec = -abs(np.sign(self.word_top_assign-top)) + 1
				self.doc_top_count[doc, top] = np.dot(topic_vec, np.reshape(self.data[:, doc], (-1, 1)))

		#increment top_count
		self.top_count = np.matrix(np.sum(self.word_top_count, 0))

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

	def gibbs(self, num_iterations):
		"""
		input: 
			num_iterations

		updates:
			the gibbs sampler for a particular document
		"""
		iter = 0
		while iter < num_iterations:
			iter += 1
			print("iteration " + str(iter))
			for doc in range(self.num_docs):
				#only iterate through words in each document
				for word in self.words_in_doc(doc):
					topic_old = self.word_top_assign[0, word]
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
										(self.top_count[0, k] + self.beta * self.num_words))
					
					#get rid of zero values
					smoothed_prob = np.maximum(self.prob, np.zeros((1,self.num_topics)) + .000001)					

					#sample and assign a topic assignment for the word
					normalized_prob = smoothed_prob[0,:-1] / smoothed_prob.sum()
					topic_list = np.random.multinomial(1, normalized_prob.tolist(), 1) #maybe can vectorize the whole algorithm
					topic_new = np.nonzero(topic_list)[1][0]
					self.word_top_assign[0, word] = topic_new

					#increment
					self.doc_top_count[doc, topic_new] += 1
					self.word_top_count[word, topic_new] += 1
					self.top_count[0, topic_new] += 1

	def comp_word_top(self):
		"""
		compute the word_top_distr
		"""
		for topic in range(self.num_topics):
			for word in range(self.num_words):
				self.word_top_distr[word, topic] = \
									float(self.word_top_count[word, topic] + self.beta) \
										/ (self.top_count[0,topic] + self.beta * self.num_words)
				print("word_topic distribution: " + str(self.word_top_distr[word, topic]))

	def comp_doc_top(self):
		"""
		compute the cod_top_distr
		"""
		for topic in range(self.num_topics):
			for doc in range(self.num_docs):
				self.doc_top_distr[doc, topic] = \
									float(self.doc_top_count[doc, topic] + self.alpha) \
										/ (sum(self.doc_top_count[doc, :]) + self.num_topics * self.alpha)
				print("document topic distribution: " + str(self.doc_top_distr[doc, topic]))

	def comp_likelihood(self):
		"""
		compute the likelihood p(W|t)

		note: Griffiths gives a way to approximate this quantity
		if I need to do this at some point.
		"""
		log_likelihood = 0
		for word in range(self.num_words):
			word_prob = 0
			docs = self.docs_of_word(word)
			for topic in range(self.num_topics):
				#probability of word given topic
				word_topic_prob = self.word_top_distr[word, topic]
				for doc in docs:
					topic_prob = self.doc_top_distr[doc, topic]
					word_prob += word_topic_prob * topic_prob
			log_likelihood += math.log1p(word_prob)
		self.log_likelihood = log_likelihood


	def cross_validate(self):
		"""
		perform cross-validation
		"""

	def save_data(self, out_path):
		doc_top_distr_list = self.doc_top_distr.tolist()
		with open(out_path, 'w') as outfile:
			writer = csv.writer(outfile, delimiter=',')
			header = ["doc_id"]
			for top in range(self.num_topics):
				header.append("topic " + str(top + 1))
			writer.writerow(header)
			counter = 1
			for line in doc_top_distr_list:
				writer.writerow([counter] + line)
				counter += 1


##Functions
def select_model(topics_list, data_matrix):
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
		topic.gibbs(200)
		topic.comp_word_top()
		topic.comp_doc_top()
		topic.comp_likelihood()
		topic_likelihoods.append([topic_num, topic.log_likelihood])
	return topic_likelihoods



##Development Testing
if __name__ == "__main__":
	file_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Data/test_data/tuples_v1.csv"
	out_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/topic_model_data/topic_model_data_v1.csv"
	stop_words_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/common-english-words.csv"

	test = Corpus(file_path, stop_words_path)
	test.read_data()
	test.filter_data()
	test.create_matrix_data_map()
	test.create_matrix()


#object tests
# topic = TopicModel(test.matrix, 3, .5)
# topic.gibbs(100)
# topic.comp_word_top()
# topic.comp_doc_top()
# topic.comp_likelihood()
# print "The log-likelihood is " + str(topic.log_likelihood)
# topic.save_data(out_path)

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
	topics_to_check = map(lambda x: x + 2 , range(15))
	model_select_path = "/Users/jkatzsamuels/Desktop/Courses/Natural Language Processing/Project/Code/topic_model_data/model_selection_data_v1.csv"
	model_select_data = select_model(topics_to_check, test.matrix)
	save_data(model_select_data, model_select_path, ["number of topics", "log_likelihood"])



