import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import caffe
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser(description='Encode images with VGG16')
parser.add_argument('gpu_idx', metavar='gpu_indx', type=int, nargs=1)
parser.add_argument('prototxt', metavar='prototxt', type=str, nargs=1)
parser.add_argument('model', metavar='model', type=str, nargs=1)
parser.add_argument('img_root', metavar='img_root', type=str, nargs=1)
parser.add_argument('out_file', metavar='out_file', type=str, nargs=1)
parser.add_argument('layer', metavar='layer', type=str, nargs=1, default='fc7')
args = parser.parse_args()

GPU_IDX = args.gpu_idx[0]
PROTOTXT = args.prototxt[0]
PRETRAINED_MODEL = args.model[0]
IMG_ROOT = args.img_root[0]
OUTPUT_FILE = args.out_file[0]
FEATURE_LAYER = args.layer[0]

#################
# SET UP CAFFE
#################
caffe.set_mode_gpu()
caffe.set_device(GPU_IDX)

######################
# RUN THE NETWORK
######################

# Initialize network
net = caffe.Net(PROTOTXT, caffe.TEST, weights=PRETRAINED_MODEL)

# Determine number of image to test
num_imgs = len(os.listdir(IMG_ROOT))

# Run network to encode features and write them to file
with open(OUTPUT_FILE, 'w') as fout:
	for itt in xrange(num_imgs):
		net.forward()
		features = net.blobs[FEATURE_LAYER].data[0]
		fout.write(' '.join(map(str, features.tolist())) + '\n')
