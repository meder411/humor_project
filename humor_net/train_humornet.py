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
GPU_IDX = 0 # Set which GPU to use
NITER = 1000 # Number of test batches to run

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
solver = caffe.SGDSolver('humornet_solver.prototxt')) # Load solver from prototxt file
train_net = solver.net # Assign the network to train

# Run training
train_loss = np.zero(NITER)
for itt in xrange(NITER):
	solver.step(1) # 1 forward/backward passes
	train_loss[itt] = train_net.blocks['loss'].data
	if itt % 100 == 0:
		print train_loss[itt]
