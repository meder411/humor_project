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
		self._top_names = ['frame_data', 'word_data', 'speaker_vec', 'cont_sequence', 'gt_laugh']
	
		# Parse layer parameters into Python dict
		params = eval(self.param_str)

		# Store input as class variables
		self._batch_size = params['batch_size']

		# Get phase of network operation	
		self._phase = params['phase'].lower()

		# Create a batch loader to load the images.
		self._batch_loader = BatchLoader(params)
	
		# Reshape tops
		top[0].reshape(self._batch_size, 3, 224, 224) # FaceNet's input is (batch_size x channels(3) x height(224) x width(224))
		top[1].reshape(self._batch_size, 6) # 6 channels because 6 attributes

		if self._phase == 'train':
			top[2].reshape(self._batch_size, 6) # 6 channels because 6 weights
	
	# Load data on forward pass
	def forward(self, bottom, top):
		for itt in range(self._batch_size):
			# Use the batch loader to load the next image.
			img, label, weights = self._batch_loader.load_next_image()

			# Add data directly to the Caffe data layer
			top[0].data[itt, ...] = img
			top[1].data[itt, ...] = label

			if self._phase == 'train':
				top[2].data[itt, ...] = weights

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
		self._image_root = params['srt_root'] # Root directory of subtitle files
		self._cur = 0 # Current image index

		# Initialize a transformer for modifying images (e.g. augmentation, preprocessing)
		self._transformer = ImageTransformer()	
		self._transformer.set_scale(1/255) # Scale value to transform intensity ranges from [0,255] --> [0,1]

		# Initialize and load the data
		self._labels = []
		self._image_paths = []
		self._weights = []
		self.__load_data(self._image_root, self._data_file, self._weights_file)

		# Log the test runs
		if self._phase is 'test':
			with open(osp.join(self._log_root, self._experiment, self._architecture, 'test_GT_log.txt'), 'w') as f:
			    f. write('Iteration Image_Path Attribute_GT\n')

		print "BatchLoader initialized with {} images".format(len(self._image_paths))

	 # Load the next image in a batch.
	def load_next_image(self):

		# If all data has been seen, change the order
		if self._cur == len(self._image_paths):
			self._cur = 0 # Reset image index
			self.__shuffle_lists() # Shuffle the data
		
		# Load an image and resize so min(H,W) = 256
		image_file_name = self._image_paths[self._cur]
		img = np.asarray(self.__resize(Image.open(osp.join(self._image_root, image_file_name))))

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
		if weights_file:
			with open(weights_file, 'r') as f:
				f.readline()
				weights = f.readlines()
				weights = [line.strip('\n\r').split(' ') for line in weights]
				weights = {line[0] : float(line[2]) for line in weights}
				for lbl in label_names:
					self._weights.append(weights[lbl])
	
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
	
