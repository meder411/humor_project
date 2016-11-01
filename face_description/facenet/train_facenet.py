__author__ = 'Marc Eder'
__date__ = 'October 28, 2016'

import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import os
import os.path as osp
import numpy as np
import caffe

######################
# UTILITY FUNCTIONS
######################
# Sigmoid Function
def sigmoid(x):
	return 1 / (1 + np.exp(-x))

# Functions for measuring training accuracy
def hamming_distance(gt, est):
	return sum([1 for (g, e) in zip(gt, est) if g == e]) / float(len(gt))

# Calculate attribute detection accuracy
def check_att_accuracy(net, num_batches, batch_size):
	att_acc = 0.0
	for t in range(num_batches):
		net.forward()
		att_gts = net.blobs['labels'].data
		att_ests = sigmoid(net.blobs['att_scores'].data) > 0.5
		for gt, est in zip(att_gts, att_ests): #for each ground truth and estimated label vector
			att_acc += hamming_distance(gt, est)
	return att_acc / (num_batches * batch_size)

# Calculate attribute detection baseline accuracy (guess all 0's)
def check_baseline_accuracy(net, num_batches, batch_size):
	att_acc = 0.0
	for t in range(num_batches):
		net.forward()
		att_gts = net.blobs['labels'].data
		att_ests = np.zeros((batch_size, len(att_gts)))
		for gt, est in zip(att_gts, att_ests): #for each ground truth and estimated label vector
			att_acc += hamming_distance(gt, est)
	return att_acc / (num_batches * batch_size)

# Function to write accuracy to file
def write_accuracy_to_file(filename, itt, att_acc):
	with open(filename, 'a') as f:
		f.write(str(itt) + ' ' + str(att_acc) + '\n')


###########################
# USER DEFINED VARIABLES
###########################
MODELS_ROOT = 'models' # Root of directory containing models
LOGS_ROOT = '../logs' # Root of directory to put log files
GPU_IDX = 1 # Set which GPU to use
TRAIN_BS = 75 # Training batch size
TEST_BS = 1 # Testing batch size


#################
# SET UP CAFFE
#################
# Initialize GPU mode
caffe.set_mode_gpu()
caffe.set_device(GPU_IDX)


######################
# TRAIN THE NETWORK
######################
# Load solver
solver = caffe.SGDSolver(osp.join(MODELS_ROOT, 'facenet_train_solver.prototxt')) # Load solver from prototxt file
train_net = solver.net # Assign the network to train
train_net.copy_from(osp.join(MODELS_ROOT, 'VGG_FACE.caffemodel')) # Initialize the weights of the training network with VGG_FACE parameters
test_net = solver.test_nets[0] # Assign the network to test
test_net.share_with(train_net) # Link the weights of the training and testing networks

# Check the baseline accuracy
baseline_att_acc = check_baseline_accuracy(test_net, 50, TEST_BS)
print 'Baseline attribute accuracy:{0:.4f}'.format(baseline_att_acc)

# Initialize a new log file
accuracy_file = osp.join(LOGS_ROOT, 'training_accuracy.txt')
with open(accuracy_file, 'w') as f:
	f.write('Iteration Attribute_Accuracy\n')
	f.write('0 {0:.4f}\n'.format(baseline_att_acc))

# Run training for 10k iterations (i.e. 10k batches * 75 images/batch = 750k training images processed)
for itt in range(100):
	solver.step(100) # 100 forward/backward passes
	att_acc = check_att_accuracy(test_net, 50, TEST_BS) # Calculate accuracy
	write_accuracy_to_file(accuracy_file, (itt+1)*100, att_acc) # Log accuracy
	print 'itt:{:3d}'.format((itt + 1) * 100) # Print current iteration to console
	print 'attributes accuracy: ', att_acc # Print accuracy to console
