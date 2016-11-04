__author__ = 'Marc Eder'
__date__ = 'October 28, 2016'

import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import os
import os.path as osp
import numpy as np
import caffe
import time
import network_util
import subprocess

###########################
# USER DEFINED VARIABLES
###########################
MODELS_ROOT = 'models' # Root of directory containing models
SNAPSHOTS_ROOT = 'snapshots'
LOGS_ROOT = '../logs' # Root of directory to put log files
GPU_IDX = 0 # Set which GPU to use
TRAIN_BS = 75 # Training batch size
TEST_BS = 30 # Testing batch size
NUM_TEST_BATCHES = 800 # Number of test batches to run

#################
# SET UP CAFFE
#################
# Initialize GPU mode
caffe.set_mode_gpu()
caffe.set_device(GPU_IDX)

# Initialize a new log file
accuracy_file = osp.join(LOGS_ROOT, 'training_accuracy' + '.txt')

######################
# TRAIN THE NETWORK
######################
# Load solver
solver = caffe.SGDSolver(osp.join(MODELS_ROOT, 'facenet_train_solver.prototxt')) # Load solver from prototxt file
train_net = solver.net # Assign the network to train
train_net.copy_from(osp.join(SNAPSHOTS_ROOT, 'snapshot_iter_0.caffemodel')) # Initialize the weights of the training network with VGG_FACE parameters

# Check the baseline accuracy (i.e. guess all 0's) on a separate GPU
print 'Checking baseline accuracy'
subprocess.Popen(['python', 'test_facenet.py', '0', '1', str(TEST_BS), str(NUM_TEST_BATCHES), osp.join(MODELS_ROOT, 'facenet_valid.prototxt'), accuracy_file])


# Run training for 20k iterations (20k batches * 75 images/batch = 1.5M training images processed)
# Test network on separate GPU every 500 iterations
for itt in xrange(40):
	solver.step(500) # 100 forward/backward passes
	print 'Evaluating accuracy'
	subprocess.Popen(['python', 'test_facenet.py', str((itt+1)*500), '1', str(TEST_BS), str(NUM_TEST_BATCHES), osp.join(MODELS_ROOT, 'facenet_valid.prototxt'), accuracy_file])
