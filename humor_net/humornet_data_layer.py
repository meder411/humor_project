__author__= 'Marc Eder'
__date__ = 'October 27, 2016'

# Imports
import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import caffe
import numpy as np
import os.path as osp
import random
from PIL import Image

# Python data layer to for FaceNet
class HumorNetNetDataLayer(caffe.Layer):

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
		top[0].reshape(self._timesteps, self._batch_size, 4096) # FRAME DATA - timesteps, batch size, frame_data_vector length (VGG fc7)
		top[1].reshape(self._timesteps, self._batch_size, vocab_size + 1) # WORD VECTOR - timesteps, batch size, vocab size + 1
		top[2].reshape(self._timesteps, self._batch_size, pos_size) # POS TAGS - timesteps, batch size, pos tag size
		top[3].reshape(self._timesteps, self._batch_size, speaker_size) # SPEAKER VECTORS - timesteps, batch size, speaker size
		top[4].reshape(self._timesteps, self._batch_size) # CONTINUATION MARKERS - timesteps, batch_size
		top[5].reshape(self._timesteps, self._batch_size) # GT LABELS -timesteps, batch_size
		

	# Load data on forward pass
	def forward(self, bottom, top):
		for itt in range(self._batch_size):
			# Use the batch loader to load the next image.
			frame_vec, word_vec, pos_vec, speaker_vec, cont_label, gt_laugh = self._batch_loader.load_next_sequence()

			# Add data directly to the Caffe data layer
			top[0].data[:, itt, ...] = frame_vec
			top[1].data[:, itt, ...] = word_vec
			top[2].data[:, itt, ...] = pos_vec
			top[3].data[:, itt, ...] = speaker_vec
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
		self._srt_root = params['srt_root'] # Root directory of subtitle files
		self._frame_root = params['frame_root'] # Root directory of frame data files
		self._timesteps = params['timesteps'] # Number of timesteps in each sequence
		self._vocab_file = params['vocab_file'] # Path to vocab file
		self._speaker_file = params['speaker_file'] # Path to speaker file
		self._pos_file = params['pos_file'] # Path to POS file
		self._num_vocab = params['num_vocab'] # Size of vocabulary
		self._num_speakers = params['num_spekaers'] # Number of speakers
		self._num_pos = params['num_pos'] # Number of POS tags
		self._cur = 0 # Current sequence index

		# Initialize an augmenter for augmenting dataset
		self._augmenter = Augmenter()	

		# Load and process the data
		self._frame_vecs = np.zeros(self._timesteps, 1, 4096)
		self._word_vecs = np.zeros(self._timesteps, 1, self._num_vocab + 1)
		self._speaker_vecs = np.zeros(self._timesteps, 1, self._num_speakers)
		self._pos_vecs = np.zeros(self._timesteps, 1, self._num_pos)
		self._cont_sequences = np.zeros(self._timesteps, 1)
		self._gt_laughs = np.zeros(self._timesteps, 1)
		self.__load_data(self._srt_root, self._frame_root)


	 # Load the next image in a batch.
	def load_next_sequence(self):

		# If all data has been seen, change the order
		if self._cur == len(self._image_paths):
			self._cur = 0 # Reset image index
			self.__shuffle_lists() # Shuffle the data
		
		# Load a sequence
		frame_vec = np.asarray(self._frame_vecs[self._cur])
		word_vec = self._word_vecs[self._cur]
		speaker_vec = self._speaker_vecs[self._cur]
		pos_vec = self._pos_vecs[self._cur]
		cont_sequence = self._cont_sequences[self._cur]
		gt_laugh = self._gt_laughs[self._cur]

		# Pull corresponding ground truth and convert to numpy float32 type array
		label = np.asarray(self._labels[self._cur], dtype=np.float32)

		# Log a test run
		if self._phase is 'test':
			with open(osp.join('..', 'logs', 'test_GT_log.txt'), 'a') as f:
			    f.write(str(self._cur) + ' ' + self._image_paths[self._cur] + ' '.join(map(str, map(int, label))) + '\n')

		# Process image
		self._transformer.set_mean([np.mean(img[:,:,i]) for i in xrange(img.shape[2])])
		img = self._transformer.augment(img) # Perform data augmentation steps on image (random crops and random flips)

		# Increment image index
		self._cur += 1
		
		return self._transformer.preprocess(img), label, self._weights

	# Read the data from the file
	def __load_data(self, image_root, data_file, weights_file):
		with open(data_file, 'r') as f:
			label_names = f.readline()
			label_names = [lbl for lbl in label_names.strip('\n\r').split(' ')[2:]]
			data = f.readlines()
			data = [line.strip('\r\n').split(' ') for line in data]
			data =[[line[0], line[1], [float(x) >= 0.5 for x in line[2:]]] for line in data]
			self._labels = [line[2] for line in data]
			self._image_paths = [osp.join(image_root, line[0], line[0] + '_' + line[1] + '.jpg') for line in data]
	
	# Shuffle the data lists *together*
	def __shuffle_lists(self):
		# First shuffle the indices
		index_shuffle = range(len(self._image_paths))
		random.shuffle(index_shuffle)
		
		# Then reindex the lists
		self._image_paths = [self._image_paths[i] for i in index_shuffle]
		self._labels = [self._labels[i] for i in index_shuffle]

	# Resize an image so the smaller of height/width is 256
	# Requires img to be of type PIL.Image.Image
	def __resize(self, img):
		width, height = img.size
		if height > width:
			ratio = 256 / width # 256 from VGG paper
			return img.resize((256, ratio * height))
		else:
			ratio = 256 / height # 256 from VGG paper
			return img.resize((ratio * width, 256))


class Augmenter(object):

	def __init__(self, frame_variance, min_sent_len, max_sent_len):
		self._frame_variance = frame_variance
		self._min_sent_len = min_sent_len
		self._max_sent_len = max_sent_len 
