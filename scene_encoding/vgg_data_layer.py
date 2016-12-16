__author__= 'Marc Eder'
__date__ = 'November 28, 2016'

# Imports
import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import caffe
import numpy as np
import random
import math
import os
import os.path as osp
import sqlite3
from PIL import Image

# Adapter function to directly input NumPy ndarrays into Colmap database as Blobs 
def adapt_array(arr):
        return np.getbuffer(sqlite3.Binary(arr))

sqlite3.register_adapter(np.ndarray, adapt_array)

# Python data layer to for running VGG test network
class VGGDataLayer(caffe.Layer):

	def setup(self, bottom, top):

		# Names of the data layers being fed the data
		self._top_names = ['data']
	
		# Parse layer parameters into Python dict
		params = eval(self.param_str)

		# Create a batch loader to load the images.
		self._batch_loader = BatchLoader(params)
	
		# Reshape tops
		top[0].reshape(1, 3, 224, 224) # VGG's input is (batch_size x channels(3) x height(224) x width(224))
	
	# Load data on forward pass
	def forward(self, bottom, top):
		# Use the batch loader to load the next image.
		img = self._batch_loader.load_next_image()

		# Add data directly to the Caffe data layer
		top[0].data[0, ...] = img


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
		self._log_root = params['log_root'] # Path to log directory
		self._image_root = params['image_root'] # Root directory of image

		self._cur = 0 # Current image index

		# Initialize a transformer for modifying images (e.g. augmentation, preprocessing)
		self._transformer = ImageTransformer()	
		self._transformer.set_scale(1/255) # Scale value to transform intensity ranges from [0,255] --> [0,1]

		# Initializei and load the data paths
		try:
			os.remove('features.db')
		except OSError:
			pass

		conn = sqlite3.connect('features.db', detect_types=sqlite3.PARSE_DECLTYPES)
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS features (id INTEGER, episode TEXT, frame_number INTEGER, feature BLOB)')

#		self._image_paths = os.listdir(self._image_root)
		self._image_paths = []
		epdir = '/playpen/meder/projects/humor/dataset/subtitles/organized_data'
		framesdir = '/playpen/meder/projects/humor/dataset/video/frames/'
		itt = 1
		for ep in os.listdir(epdir):
			with open(osp.join(epdir, ep), 'r') as f:
				lines = f.readlines()
				lines = lines[1:]
				lines = [line.split(',') for line in  lines]
				lines = [[line[0], line[1], line[2], line[3], ','.join(line[4:])] for line in lines]
			for line in lines:
				s = int(line[0])
				e = int(line[1])
				min_num_frames = min(len(line[4].split(' ')), e-s)
				step = int(math.ceil((e-s) / min_num_frames))
				for div in xrange(s, e, step):
					indices = random.sample(xrange(div, div + step), min(step, 5))
					for idx in indices:
						path = (osp.join(framesdir, osp.splitext(ep)[0], '{}_{:05d}.jpg'.format(osp.splitext(ep)[0], idx)))
						self._image_paths.append(path)
						c.execute('INSERT INTO features VALUES (?, ?, ?, ?)', [itt, osp.splitext(ep)[0], idx, np.zeros(4096, dtype=np.float32)])
						itt += 1
		conn.commit()
		conn.close()

		# Log the runs
		with open(osp.join(self._log_root, 'image_log.txt'), 'w') as f:
		    f. write('Iteration Image\n')

		print "BatchLoader initialized with {} images".format(len(self._image_paths))
	
	# Load the next image in a batch.
	def load_next_image(self):

		# If all data has been seen return None
		if self._cur == len(self._image_paths):
			return None
	
		# Load an image and resize so min(H,W) = 256
		image_file_name = self._image_paths[self._cur]

		if osp.exists(osp.join(self._image_root, image_file_name)):
			img = np.asarray(self.__resize(Image.open(osp.join(self._image_root, image_file_name))))
		else:
			return np.zeros([3,224,224], dtype=np.float32)

		# Log a test run
		with open(osp.join(self._log_root, 'image_log.txt'), 'a') as f:
		    f.write(str(self._cur) + ' ' + self._image_paths[self._cur] + '\n')

		# Process image
		self._transformer.set_mean(np.array([103.939, 116.779, 123.68], np.float32)) # Numbers from VGG training
		img = self._transformer.crop(img) # Perform center cropping

		# Increment image index
		self._cur += 1
		
		return self._transformer.preprocess(img)

	
	# Resize an image so the smaller of height/width is 256
	# Requires img to be of type PIL.Image.Image
	def __resize(self, img):
		width, height = img.size
		if height > width:
			ratio = 256.0 / float(width) # 256 from VGG paper
			return img.resize((256, int(ratio * height)))
		else:
			ratio = 256.0 / float(height) # 256 from VGG paper
			return img.resize((int(ratio * width), 256))
	

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

	# 224x224 center crops
	def crop(self, img):
		img_dim = img.shape
		if img_dim[0] > self._crop_dims[0]:
			tlr = int(math.floor((img_dim[0] - self._crop_dims[0]) / 2))
		else:
			tlr = 0
		if img_dim[1] > self._crop_dims[1]:
			tlc = int(math.floor((img_dim[1] - self._crop_dims[1]) / 2))
		else:
			tlc = 0
		return img[tlr : tlr+self._crop_dims[0], tlc : tlc+self._crop_dims[1], :]

