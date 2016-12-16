__author__= 'Marc Eder'
__date__ = 'October 27, 2016'

# Imports
import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import caffe
import numpy as np
import os
import os.path as osp
import random
import math
import string
import nltk
import sqlite3
from PIL import Image

# Python data layer to for FaceNet
class HumorNetDataLayer(caffe.Layer):

	def setup(self, bottom, top):

		# Names of the data layers being fed the data
		self._top_names = ['frame_data', 'word_data', 'pos_vec', 'speaker_vec', 'cont_sequence', 'gt_laugh']
	
		# Parse layer parameters into Python dict
		params = eval(self.param_str)

		# Store input as class variables
		self._batch_size = params['batch_size']
		self._timesteps = params['timesteps']

		# Create a batch loader to load the images.
		self._batch_loader = BatchLoader(params)
	
		# Reshape tops
		top[0].reshape(self._timesteps, self._batch_size, 4096) # FRAME_VECS - timesteps, batch size, 4096
		top[1].reshape(self._timesteps, self._batch_size) # WORD VECTOR - timesteps, batch size, (word is index of one-hot vector)
		top[2].reshape(self._timesteps, self._batch_size) # POS TAGS - timesteps, batch size, (pos is index of one-hot vector)
		top[3].reshape(self._timesteps, self._batch_size) # SPEAKER VECTORS - timesteps, batch size (speaker is index of one-hot vector)
		top[4].reshape(self._timesteps, self._batch_size) # CONTINUATION MARKERS - timesteps, batch_size
		top[5].reshape(self._timesteps, self._batch_size) # GT LABELS -timesteps, batch_size
		

	# Load data on forward pass
	def forward(self, bottom, top):
		for itt in range(self._batch_size):
			# Use the batch loader to load the next image.
			frame_vec, word_vec, pos_vec, speaker_vec, cont_label, gt_laugh = self._batch_loader.load_next_sequence()
			# Add data directly to the Caffe data layer
			top[0].data[:, itt, ...] = frame_vec
			top[1].data[:, itt] = word_vec
			top[2].data[:, itt] = pos_vec
			top[3].data[:, itt] = speaker_vec
			top[4].data[:, itt] = cont_label
			top[5].data[:, itt] = gt_laugh


	# As this layer always has fixed input and output sizes (from being the data layer),
	# we can leave this unimplemented
	def reshape(self, bottom, top):
		pass

	# Nothing to backpropagate either
	def backward(self, top, propagate_down, bottom):
		pass


# A class to load data to from the disk
class BatchLoader(object):

	# Initializer
	def __init__(self, params):
		self._batch_size = params['batch_size'] # Number of images to load into the network at a time
		self._text_root = params['text_root'] # Root directory of subtitle files
		self._frame_root = params['frame_root'] # Root directory of frame data files
		self._timesteps = params['timesteps'] # Number of timesteps in each sequence
		self._vocab_file = params['vocab_file'] # Path to vocab file
		self._speaker_file = params['speaker_file'] # Path to speaker file
		self._pos_file = params['pos_file'] # Path to POS file

		# Seed random number generator
		self._seed = 319874
		random.seed(self._seed)

		# Load vocabulary, speakers, POS
		self._episode_frames = dict()
		self._episode_laughs = dict()
		self._episode_speakers = dict()
		self._episode_words = dict()
		self._episode_pos = dict()
		self._vocabulary = dict()
		self._speakers = dict()
		self._pos = dict()

		self.__load_data()

		# Hard-coded values		
		self._min_seq_len = 3
		self._max_seq_len = 20
		self._num_vocab =  4640 # Size of vocabulary + 1
		self._num_speakers = 131 # Number of speakers + 1
		self._num_pos = 39 # Number of POS tags + 1

		# Connect to sqlite DB for vision features
		self._conn = sqlite3.connect('../scene_encoding/features.db', detect_types = sqlite3.PARSE_DECLTYPES)
		self._c = self._conn.cursor()


	 # Load the next sequence in a batch.
	def load_next_sequence(self):

		# Allocate space
		frame_vecs = np.zeros([self._timesteps, 4096])
		word_vecs = np.zeros(self._timesteps)
		speaker_vecs = np.zeros(self._timesteps)
		pos_vecs = np.zeros(self._timesteps)
		cont_sequences = np.zeros(self._timesteps)
		gt_laughs = np.zeros(self._timesteps)

		# Pick a random episode
		ep = random.choice(self._episode_frames.keys())

		frames = self._episode_frames[ep]
		words = self._episode_words[ep]
		pos = self._episode_pos[ep]
		speakers = self._episode_speakers[ep]
		laughs = self._episode_laughs[ep]

		# Pick a random sequence length
		length = random.randint(self._min_seq_len, self._max_seq_len)

		# Pick a random starting utterance	
		starting_idx = random.randint(0, len(words) - length - 1)

		# Go through each utterance in the subtitle sequence
		num_words = 0
		seq_idx = 0
		for i in xrange(starting_idx, starting_idx + length):
			utterance_size = len(words[i])
			if utterance_size > 0:
				# If adding utterance will overflow timesteps, break (TODO make this not a break statement)
				num_words += utterance_size
				if num_words > self._timesteps:
					break

				# Determine <utterance_size> equal frame blocks
				frame_start = frames[i][0]
				frame_end = frames[i][1]
				frame_step = math.floor(frame_start - frame_end / utterance_size)

				# Go through each word in utterance
				mult = 1
				for j in xrange(len(words[i])):
				
					# If speakers in known list, encode it as one-hot vector, otherwise make in UNK
					if speakers[i] in self._speakers:
						speaker_vecs[seq_idx] = speakers[i]
					else:
						speaker_vecs[seq_idx] = len(self._speakers)

					# If POS in known list, encode it as one-hot vector, otherwise make it UNK
					if pos[i][j] in self._pos:
						pos_vecs[seq_idx] = self._pos[pos[i][j]]
					else:
						pos_vecs[seq_idx] = len(self._pos)

					# If word in known list, encode it as one-hot vector, otherwise make it UNK
					if words[i][j] in self._vocabulary:
						word_vecs[seq_idx] = self._vocabulary[words[i][j]]
					else:
						word_vecs[seq_idx] = len(self._vocabulary)

					# If this is not the first word in a dialogue line, make continuation sequence a 1
					if i > 0:
						cont_sequences[seq_idx] = 1
					
					# Store ground truth laugh
					gt_laughs[seq_idx] = laughs[i]

					# Extract random frame from uniformly sized blocks according to size of utterance
					begin = frame_start + (mult - 1) * frame_step
					end = min(frame_start + mult * frame_step, frame_end)
					mult += 1
					rows = self._c.execute('SELECT feature FROM features WHERE episode = (?) AND frame_number >= (?) AND frame_number <= (?)',
						[ep, begin, end]).fetchall()
					if len(rows):
						idx = random.randrange(0, len(rows))
						frame_vecs[seq_idx, :] = np.frombuffer(rows[idx][0], np.float32)

					# Increment sequence counter
					seq_idx += 1
								
		return frame_vecs, word_vecs, pos_vecs, speaker_vecs, cont_sequences, gt_laughs

	# Read the data from the file
	def __load_data(self):
		with open(self._vocab_file, 'r') as f:
			self._vocabulary = {k : v for v, k in enumerate(f.readlines())}
		with open(self._speaker_file, 'r') as f:
			self._speakers = {k : v for v, k in enumerate(f.readlines())}
		with open(self._pos_file, 'r') as f:
			self._pos = {k : v for v, k in enumerate(f.readlines())}
		for ep in os.listdir(self._text_root):
			if ep.endswith('_laugh.txt'):
				with open(osp.join(self._text_root, ep), 'r') as f:
					lines = f.readlines()
					lines = [line.strip().split(',') for line in lines[1:]]
					self._episode_laughs[ep[:5]] = [int(line[2]) for line in lines]
					self._episode_frames[ep[:5]] = [[int(line[0]), int(line[1])] for line in lines]
			if ep.endswith('_words.txt'):
				with open(osp.join(self._text_root, ep), 'r') as f:
					lines = f.readlines()
					lines = [line.strip().split(',') for line in lines[1:]]
					self._episode_words[ep[:5]] = [line[2].split(' ') for line in lines]
			if ep.endswith('_pos.txt'):
				with open(osp.join(self._text_root, ep), 'r') as f:
					lines = f.readlines()
					lines = [line.strip().split(',') for line in lines[1:]]
					self._episode_pos[ep[:5]] = [line[2].split(' ') for line in lines]
			if ep.endswith('_speaker.txt'):
				with open(osp.join(self._text_root, ep), 'r') as f:
					lines = f.readlines()
					lines = [line.strip().split(',') for line in lines[1:]]
					self._episode_speakers[ep[:5]] = [line[2] for line in lines]
	def __to_one_hot(n, length):
		if n < length:
			vec = np.zeros(1, length)
			if n <= 0:
				return vec
			else:
				vec[n-1] = 1
				return vec
		else:
			print 'n must be < length'
