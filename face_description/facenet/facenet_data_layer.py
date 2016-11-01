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
class FaceNetDataLayer(caffe.Layer):

	def setup(self, bottom, top):

		# Names of the data layers being fed the data
		self._top_names = ['data', 'label']
	
		# Parse layer parameters into Python dict
		params = eval(self.param_str)

		# Store input as class variables
		self._batch_size = params['batch_size']
	
		# Create a batch loader to load the images.
		self._batch_loader = BatchLoader(params)
	
		# Reshape tops
		top[0].reshape(self._batch_size, 3, 224, 224) # FaceNet's input is (batch_size x channels(3) x height(224) x width(224))
		top[1].reshape(self._batch_size, 19) # 19 channels because 19 attributes
	
	# Load data on forward pass
	def forward(self, bottom, top):
		for itt in range(self._batch_size):
			# Use the batch loader to load the next image.
			img, label = self._batch_loader.load_next_image()

			# Add data directly to the Caffe data layer
			top[0].data[itt, ...] = img
			top[1].data[itt, ...] = label

	# As this layer always has fixed input and output sizes (from being the data layer),
	# we can leave this unimplemented
	def reshape(self, bottom, top):
		pass

	# Nothing to backpropagate either
	def backward(self, top, propagate_down, bottom):
		pass


# A class to asynchronously load images to from the disk
class BatchLoader(object):

	# Initializer
	def __init__(self, params):
		self._batch_size = params['batch_size'] # Number of images to load into the network at a time
		self._phase = params['phase'].lower() # Are we training or testing the network
		self._image_root = params['image_root'] # Root director of images
		self._data = params['label_file'] # File containing GT labels
		self._cur = 0 # Current image index

		# Initialize a transformer for modifying images (e.g. augmentation, preprocessing)
		self._transformer = ImageTransformer()	
		self._transformer.set_scale(1/255) # Scale value to transform intensity ranges from [0,255] --> [0,1]

		# Initialize and load the data
		self._labels = []
		self._image_paths = []
		self.__load_data(self._image_root, self._data)

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
			with open(osp.join('test_GT_log.txt'), 'a') as f:
			    f. write(str(self._cur) + ' ' + self._image_paths[self._cur] + ' '.join(map(str, map(int, label))) + '\n')

		# Process image
		self._transformer.set_mean([np.mean(img[:,:,i]) for i in xrange(img.shape[2])])
		img = self._transformer.augment(img) # Perform data augmentation steps on image (random crops and random flips)

		# Increment image index
		self._cur += 1
		
		return self._transformer.preprocess(img), label

	# Read the data from the file
	def __load_data(self, image_root, data_file):
		with open(data_file, 'r') as f:
			label_names = f.readline()
			data = f.readlines()
			data = [line.strip('\r\n').split(' ') for line in data]
			data =[[line[0], line[1], [float(x) for x in line[2:]]] for line in data]
			self._labels = [line[2] for line in data]
			self._image_paths = [osp.join('..', 'frames', line[0], line[0] + '_' + line[1] + '.jpg') for line in data]

	# Shuffle the data lists *together*
	def __shuffle_lists():
		# First shuffle the indices
		index_shuffle = xrange(len(self._image_paths))
		shuffle(index_shuffle)
		
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
	

# Inspired by Caffe's SimpleTransformer
class ImageTransformer(object):
	
	def __init__(self):
		self._mean = np.array((128,128,128), dtype=np.float32)
		self._scale = 1.0
		self._crop_dims = [224,224]

	def set_mean(self, mean):
		self._mean = mean

	def set_scale(self, scale):
		self._scale = scale

	def set_crop_dims(self, dims):
		self._crop_dims = dims

	# Preprocess image according to VGG paper
	def preprocess(self, img):
		img = np.float32(img) # Convert image to 32-bit float type
		img -= self._mean # Centers intensity values at 0
		img *= self._scale # Scales intensity range
		img = np.transpose(img, (2,0,1)) # Swaps axes to [channels, height, width]
		img = img[:,:,::-1] # Changes RGB to BGR
		return img

	# Undo preprocessing
	def deprocess(self, img):
		img = img[:,:,::-1] # Change BGR back to RGB
		img = np.transpose(img, (1, 2, 0)) # Swaps axes back to [height, width, channels]
		img /= self._scale # Rescale to original intensity range
		img += self._mean # Shift intensity values back to original offset
		img = np.uint8(img) # Convert image back to 8-bit uint type
		return img

	# Augments data by taking random crops and randomly flipping across vertical
	def augment(self, img):
		img_dim = img.shape
		tlr = random.randrange(img_dim[0] - self._crop_dims[0])
		tlc = random.randrange(img_dim[1] - self._crop_dims[1])
		flip = random.randint(0,1) * 2 - 1
		img = img[:, ::flip, :]
		return img[tlr : tlr+self._crop_dims[0], tlc : tlc+self._crop_dims[1], :]
		

