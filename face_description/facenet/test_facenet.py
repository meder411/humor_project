import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import caffe
import numpy as np


PRETRAINED_MODEL = ''
NET_ARCH = ''
TRAIN_GPU_IDX = 0


caffe.set_mode_gpu()
caffe.set_device(GPU_IDX)




# Initialize network
training_net = caffe.Net(NET_ARCH, PRETRAINED_MODEL)


class FaceNet(caffe.Net):
	def __init__(self, model_file, weights_file):
		caffe.Net.__init__(self, model_file, weights_file, caffe.TRAIN)
		self.batch_size = self.blobs[self.inputs[0]].num
