
# Utility functions for FaceNet

import numpy as np

# Sigmoid Function
def sigmoid(x):
	return 1 / (1 + np.exp(-x))

# Assumes gt and est are boolean values
def true_positives(gt, est):
	return np.sum(np.float32(np.bitwise_and(gt, est)), axis=0)

# Assumes gt and est are boolean values
def false_negatives(gt, est):
	return np.sum(np.float32(np.bitwise_and(gt, ~est)), axis=0)

# Assumes gt and est are boolean values
def all_est_positives(est):
	return np.sum(np.float32(est), axis=0)

# Assumes gt and est are boolean values
def precision(gt, est):
	return true_positives(gt, est) / all_est_positives(est)

# Assumes gt and est are boolean values
def recall(gt, est):
	tp = true_positives(gt, est)
	return tp / tp + false_negatives(gt, est)

# Assumes gt and est are boolean values
def f1_score(gt, est):
	pr = precision(gt, est)
	re = recall(gt, est)
	return 2 * pr * re / (pr + re)

# Hamming distance
def hamming_distance(gt, est):
	return np.float32(np.sum(~np.bitwise_xor(gt, est), axis=0)) / np.float32(gt.shape[0])

# Calculate attribute detection accuracy
def check_accuracy(gt, est):
	pr = precision(gt, est)
	re = recall(gt, est)
	f1 = f1_score(gt, est)
	h_dist = hamming_distance(gt, est)
	return pr, re, f1, h_dist

# Test network
def test_network(itt, gpu_idx, net_proto_path, img_file_path, accuracy_file_path):
	gt = np.zeros((num_batches*batch_size, num_classes), dtype=bool)
	est = np.zeros((num_batches*batch_size, num_classes), dtype=bool)
	for t in range(num_batches):
		net.forward()
		start_idx = t * batch_size
		end_idx = (t+1) * batch_size
		gt[start_idx : end_idx, :] = net.blobs['labels'].data > 0.5
		est[start_idx : end_idx, :] = sigmoid(net.blobs['att_scores'].data) > 0.5
	return gt, est

# Nicely format the display of the accuracy metrics
def format_accuracy(pr, re, f1, h_dist):
	pr_str = '  Precision: '
	for i in xrange(pr.size):
		pr_str = pr_str + '{:.3f} '.format(pr[i])
	pr_str = pr_str + '\n'
	re_str = '  Recall: '
	for i in xrange(re.size):
		re_str = re_str + '{:.3f} '.format(re[i])
	re_str = re_str + '\n'
	f1_str = '  F1 Score: '
	for i in xrange(f1.size):
		f1_str = f1_str + '{:.3f} '.format(f1[i])
	f1_str = f1_str + '\n'
	hdist_str = '  Hamming Distance: '
	for i in xrange(h_dist.size):
		hdist_str = hdist_str + '{:.3f} '.format(h_dist[i])
	hdist_str = hdist_str + '\n'
	return pr_str + re_str + f1_str + hdist_str

# Function to write accuracy to file
def write_accuracy_to_file(filename, itt, pr, re, f1, h_dist):
	with open(filename, 'a') as f:
		f.write('Iteration: {}\n'.format(itt) + format_accuracy(pr, re, f1, h_dist) + '\n')
