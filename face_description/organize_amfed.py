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
	if not exist:
		print fname
	return exist

def correct_label(label):
	if label == 'Au17' or label == 'AU17':
		return 'AU17'
	elif label == 'AU58' or label == 'Backward' or label == '58':
		return 'AU58'
	elif label == 'Forward' or label == 'AU57' or label == '57':
		return 'AU57'
	elif label == 'AU26' or label == 'Au26':
		return 'AU26'
	else:
		return label

# Paths
amfed_dir = '/playpen/meder/projects/humor/face_description/AMFED/AULabels'
f_all = open('amfed_uniform_labels.txt', 'w')
f_train = open('amfed_train_labels.txt', 'w')
f_test = open('amfed_test_labels.txt', 'w')

# Labels used as part of FaceNet
cnn_labels = set(['Smile', 'AU02', 'AU26', 'AU04', 'AU05', 'AU09', 'AU12', 'negAU12', \
	'Unilateral_LAU12', 'Unilateral_LAU14', 'AU57', 'AU58', 'AU18', 'AU15', \
	'AU14', 'AU17', 'AU10', 'Unilateral_RAU12', 'Unilateral_RAU14', 'Expressive'])

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

# Get all labels used
label_dict = {}
for f in os.listdir(amfed_dir):
	if f.endswith('.csv'):
		with open(osp.join(amfed_dir, f), 'r') as data_file:
			labels = data_file.readline().strip('\r\n').split(',')
			for lbl in labels:
				lbl = correct_label(lbl)
				if lbl in label_dict:
					label_dict[lbl] += 1
				else:
					label_dict[lbl] = 1

# Output file header
output = 'Basename Frame'
for lbl in label_dict:
	lbl = correct_label(lbl)
	output = output + ' ' + lbl
output = output + '\n'
f_all.write(output)

# Output CNN files headers
cnn_output = 'Basename Frame'
for lbl in cnn_labels:
	cnn_output = cnn_output + ' ' + lbl
cnn_output = cnn_output + '\n'
f_train.write(cnn_output)
f_test.write(cnn_output)

# Unify data across videos
file_dicts = {}
lines_written = 0
for f in os.listdir(amfed_dir):
	if f.endswith('.csv'):
		with open(osp.join(amfed_dir, f), 'r') as data_file:
			
			# Read this file's labels
			labels = data_file.readline().strip('\r\n').split(',')
			labels = [correct_label(lbl) for lbl in labels]

			# Read and format data
			data = data_file.readlines()
			data = [line.strip('\r\n').split(',') for line in data]
			fdata = []
			for line in data:
				fdata.append([float(x) for x in line])
			fdata = np.array(fdata) / 100.0

			# Print each set of video labels to file
			vid_basename = osp.splitext(f)[0][:-6]
			time_idx = labels.index('Time')
			row_num = 0
			for f in xrange(int(fnumbers[vid_basename])):
				if row_num < fdata.shape[0]-1:
					end_time = fdata[row_num+1, time_idx]
				else:
					end_time = fnumbers[vid_basename] * 0.04
				time = f * 0.04
				if time > end_time:
					row_num += 1
				if row_num < fdata.shape[0]:
					# Make sure this row has a corresponding video frame
					exists = check_exists(osp.join('frames', vid_basename, vid_basename + '_{0:05}.jpg'.format(f)))
					if exists:
						existing_files.remove(osp.join(vid_basename + '_{0:05}.jpg'.format(f)))
						output = vid_basename + ' ' + '{0:05}'.format(f)
						cnn_output = vid_basename + ' ' + '{0:05}'.format(f)
						for lbl in label_dict:
							if lbl in labels:
								idx = labels.index(lbl)
								output = output + ' ' + str(fdata[row_num, idx])
								if lbl in cnn_labels:
									cnn_output = cnn_output + ' ' + str(fdata[row_num, idx])
							else:
								output = output + ' ' + str(0.0)
								if lbl in cnn_labels:
									cnn_output = cnn_output + ' ' + str(0.0)
						output = output + '\n'
						cnn_output = cnn_output + '\n'
						f_all.write(output)

						# Split data into 90% training, 10% test
						if random.randrange(0,10) == 0:
							f_test.write(cnn_output)
						else:
							f_train.write(cnn_output)
						lines_written += 1

print 'Lines written = {}'.format(lines_written)
print 'Mismatch = {}'.format(len(existing_files))
