import numpy as np

gt = np.random.rand(10,4) > 0.5
print 'GT'
print gt

est = np.random.rand(10,4) > 0.5
print 'EST'
print est

#TP
tp = np.sum(np.float32(np.bitwise_and(gt, est)), axis=0)
print 'TP'
print tp

#ALL EST P
p = np.sum(np.float32(est), axis=0)
print 'EST P'
print p

#FN
fn = np.sum(np.float32(np.bitwise_and(gt, ~est)), axis=0)
print 'FN'
print fn

#Precision
precision = tp/p
print 'Precision'
print precision

#Recall
recall = tp/(tp + fn)
print 'Recall'
print recall

# F1
f1 = 2 * precision * recall / (precision + recall)
print 'F1'
print f1
