__author__ = 'Marc Eder'
__date__ = 'November 26, 2016'

import sys
sys.path.append('/playpen/meder/libraries/caffe/python')
import os
import os.path as osp
import numpy as np
import caffe

###########################
# USER DEFINED VARIABLES
###########################
SNAPSHOTS_ROOT = 'snapshots'
GPU_IDX = 1 # Set which GPU to use
NITER = 100 # Number of batches to run

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
solver = caffe.SGDSolver('humornet_solver.prototxt') # Load solver from prototxt file
solver.net.copy_from('vgg16.caffemodel') # Initialize VGG weights
train_net = solver.net # Assign the network to train

# Run training
with open('humornet_training_log.txt', 'w') as f:
	train_loss = np.zeros(NITER)
	for itt in xrange(NITER):
		solver.step(100) # 1 forward/backward passes
		train_loss[itt] = train_net.blobs['loss'].data
		print train_loss[itt]
		f.write('{} {}'.format((itt+1)*100, train_loss[itt]))
