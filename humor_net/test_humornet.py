import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import caffe
import numpy as np
import argparse
import network_util
import os.path as osp

parser = argparse.ArgumentParser(description='Start new network test')
parser.add_argument('iteration', metavar='itt', type=int, nargs=1)
parser.add_argument('gpu_idx', metavar='gpu_indx', type=int, nargs=1)
parser.add_argument('batch_size', metavar='batch_size', type=int, nargs=1)
parser.add_argument('num_batches', metavar='num_batches', type=int, nargs=1)
parser.add_argument('net_prototxt_path', metavar='net_prototxt_path', type=str, nargs=1)
parser.add_argument('accuracy_file_path', metavar='accuracy_file_path', type=str, nargs=1)
args = parser.parse_args()

CURRENT_ITT = args.iteration[0]
GPU_IDX = args.gpu_idx[0]
BATCH_SIZE = args.batch_size[0]
NUM_BATCHES = args.num_batches[0]
PRETRAINED_MODEL = 'snapshots/snapshot_iter_' + str(CURRENT_ITT) + '.caffemodel'
NET_ARCH = args.net_prototxt_path[0]
ACCURACY_FILE = args.accuracy_file_path[0]
NUM_CLASSES = 6

#################
# SET UP CAFFE
#################
caffe.set_mode_gpu()
caffe.set_device(GPU_IDX)

######################
# RUN THE NETWORK
######################

# Initialize network
net = caffe.Net(NET_ARCH, PRETRAINED_MODEL, caffe.TEST)
print PRETRAINED_MODEL

gt = np.zeros((NUM_BATCHES*BATCH_SIZE, NUM_CLASSES), dtype=bool)
est = np.zeros((NUM_BATCHES*BATCH_SIZE, NUM_CLASSES), dtype=bool)
for t in range(NUM_BATCHES):
	if t % 100 == 0:
		print 'itt: {}'.format(t)
	net.forward()
	start_idx = t * BATCH_SIZE
	end_idx = (t+1) * BATCH_SIZE
	gt[start_idx : end_idx, :] = net.blobs['labels'].data > 0.5
	est[start_idx : end_idx, :] = net.blobs['att_probability'].data > 0.5


pr, re, f1, h_dist = network_util.check_accuracy(gt, est)
network_util.write_accuracy_to_file(ACCURACY_FILE, CURRENT_ITT, pr, re, f1, h_dist)
