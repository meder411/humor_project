import os
import os.path as osp
from nltk.tag import pos_tag
import nltk
import pysrt

full_subs_dir = osp.join('subtitles', 'full')

def str_to_time_obj(string):
	return datetime.time(int(string[0:2]), int(string[3:5]), int(string[6:8]), int(string[9:]) * 1000)

def time_in_sec(time):
	return time.hour * 3600 + time.minute * 60 + time.second + time.microsecond * 10e-7

for f in os.listdir(full_subs_dir):
	subs = pysrt.open(f, 'r')

	for sub in subs:

		raw_text = str(sub.text)
		word_vec = raw_text.replace('LAUGH', '').split()
		rate_of_speech = (time_in_sec(str_to_time_obj(str(sub.start))) - time_in_sec(str_to_time_obj(str(sub.end)))) / len(word_vec) # Words / second
		speaker = str(sub.text).split(:)[0] # Speaker

		pos = [word[1] for word in pos_tag(word_vec)] # Part of speech vector
