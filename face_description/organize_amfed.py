__author__ = 'Marc Eder'
__date__ = 'October 26, 2016'

# Script that parses the AMFED database. Must be run after the MATLAB sample_video.m script

# Imports
import os
import os.path as osp
import numpy as np
import random

# Utility functions
def check_exists(fname):
	exist = osp.exists(fname)
	return exist

# Merge the labels into more general classes
# In each merger case, pick the max label value
# The order of the mergers matters, as they are assembled in the same
# order as the output_classes list hard-coded below
def merge_labels(labels, data, output_classes):

	# Initilize output array
	output_data = np.zeros((data.shape[0], len(output_classes)), dtype=np.float32)
	
	# Global 'expressive' label
	if 'Expressive' in labels:
		output_data[:,0] = data[:,labels.index('Expressive')]
	# Eyes		
	indices = [labels.index(AU) for AU in ['AU02','AU04','AU05'] if AU in labels]
	if indices:
		output_data[:,1] = np.amax(data[:,indices], axis=1)
	# Cheeks		
	indices = [labels.index(AU) for AU in ['Unilateral_LAU14', 'Unilateral_RAU14', 'AU14'] if AU in labels]
	if indices:
		output_data[:,2] = np.amax(data[:,indices], axis=1)
	# Head		
	indices = [labels.index(AU) for AU in ['AU57','AU58', 'Forward', 'Backward', '58', '57'] if AU in labels]
	if indices:
		output_data[:,3] = np.amax(data[:,indices], axis=1)
	# Mouth
	indices = [labels.index(AU) for AU in ['Smile', 'negAU12', 'AU18', 'AU15', 'Unilateral_LAU12', 'Unilateral_RAU12'] if AU in labels]
	if indices:
		output_data[:,4] = np.amax(data[:,indices], axis=1)
	# Chin	
	indices = [labels.index(AU) for AU in ['AU17', 'Au17', 'AU26', 'Au26'] if AU in labels]
	if indices:
		output_data[:,5] = np.amax(data[:,indices], axis=1)

	return output_data

# Paths
amfed_dir = '/playpen/meder/projects/humor/face_description/AMFED/AULabels'
f_weights = open('facenet/amfed_label_weights.txt', 'w')
f_train = open('facenet/amfed_train_labels.txt', 'w')
f_valid = open('facenet/amfed_valid_labels.txt', 'w')
f_test = open('facenet/amfed_test_labels.txt', 'w')

# Labels used as part of neural network
output_classes = ['Expressive', 'Eyes', 'Cheeks', 'Head', 'Mouth', 'Chin']

# Load vid-frame_number file
with open('number_of_frames.txt') as name_fn_file:
	fnumbers = name_fn_file.readlines()
	fnumbers = [line.strip('\r\n').split(' ') for line in fnumbers]
	fnumbers = {d[0] : float(d[1]) for d in fnumbers}

# Build a set of all frames sampled from the videos
existing_files = set()
for dir_name in os.listdir('frames'):
	for filename in os.listdir(osp.join('frames', dir_name)):
		existing_files.add(filename)
print 'Number of files: {}'.format(len(existing_files))	


# Output CNN files headers
cnn_output = 'Basename Frame'
for lbl in output_classes:
	cnn_output = cnn_output + ' ' + lbl
cnn_output = cnn_output + '\n'
f_train.write(cnn_output)
f_test.write(cnn_output)

# Unify data across videos
label_weights = {}
lines_written = 0
for f in os.listdir(amfed_dir):
	if f.endswith('.csv'):
		with open(osp.join(amfed_dir, f), 'r') as data_file:
			
			# Read this file's labels
			labels = data_file.readline().strip('\r\n').split(',')

			# Read and format data
			data = data_file.readlines()
			data = [line.strip('\r\n').split(',') for line in data]
			fdata = []
			for line in data:
				fdata.append([float(x) for x in line])
			fdata = np.array(fdata) / 100.0

			# Group labels into the desired output classes
			fdata = merge_labels(labels, fdata, output_classes)

			# Get video basename
			vid_basename = osp.splitext(f)[0][:-6]

			# Make sure there are frames sampled from this video
			row_num = 0
			time_idx = labels.index('Time')
			if vid_basename in fnumbers.keys():

				# Print each set of video labels to file
				for t in xrange(int(fnumbers[vid_basename])):
			
					# Set end time for each row of labels (i.e. when these labels no longer apply)
					if row_num < fdata.shape[0]-1:
						end_time = fdata[row_num+1, time_idx]
					else:
						end_time = fnumbers[vid_basename] * 0.04
					time = t * 0.04
					if time > end_time:
						row_num += 1

					# Make sure we're not overrunning the file
					if row_num < fdata.shape[0]:

						# Make sure this row has a corresponding video frame
						exists = check_exists(osp.join('frames', vid_basename, vid_basename + '_{0:05}.jpg'.format(t)))
						if exists:
							existing_files.remove(osp.join(vid_basename + '_{0:05}.jpg'.format(t)))
							output = vid_basename + ' ' + '{0:05}'.format(t)
							cnn_output = vid_basename + ' ' + '{0:05}'.format(t)

							# Go through each of the canonical labels
							# (merge_labels() function ensures the proper order)
							for lbl in output_classes:

								# Get index of label
								idx = output_classes.index(lbl)

								# Update the number of times this label has been observed (i.e. non-zero value) in the dataset
								if fdata[row_num, idx] > 0:
									if lbl in label_weights:
										label_weights[lbl] += 1
									else:
										label_weights[lbl] = 1

								cnn_output = cnn_output + ' ' + str(fdata[row_num, idx])

							# End line
							cnn_output = cnn_output + '\n'

							# Write outputs to file
							# Split data into 90% training, 10% test
							bit = random.randrange(0,10) 
							if bit == 0:
								f_test.write(cnn_output)
							elif bit == 1:
								f_valid.write(cnn_output)
							else:
								f_train.write(cnn_output)
							lines_written += 1

print label_weights

# Determine positive sample weights from label observances
weights_output = 'Label +Observations/Total Weight\n'
for lbl in label_weights:
	weight = float((lines_written - label_weights[lbl])) / float(label_weights[lbl]) # Ratio of negative occurances to positive occurances
	weights_output = weights_output + '{0} {1}/{2} {3:.3f}\n'.format(lbl, label_weights[lbl], lines_written, weight)
f_weights.write(weights_output)

# Close all files
f_train.close()
f_valid.close()
f_test.close()
f_weights.close()

print 'Lines written = {}'.format(lines_written)
print 'Mismatch = {}'.format(len(existing_files))
if existing_files:
	print existing_files

