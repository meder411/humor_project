import os.path as osp
import os
import pysrt
import datetime
import string
import nltk

# Directory tree
project_root = '..' 
srt_dir = osp.join(project_root, 'subtitles', 'full')
collection_dir = osp.join(project_root, 'subtitles', 'organized_data')
output_dir = osp.join(project_root, 'subtitles', 'organized_data')

# Functions
def time_to_frame_num(secs):
	fps = 23.976
	return int(round(fps * secs))

def str_to_time_obj(string):
	return datetime.time(int(string[0:2]), int(string[3:5]), int(string[6:8]), int(string[9:]) * 1000)

def time_in_sec(time):
	return time.hour * 3600 + time.minute * 60 + time.second + time.microsecond * 10e-7

# Vocabulary and speakers sets
with open(osp.join(collection_dir, 'vocab.txt'), 'r') as fvocab:
	vocab = fvocab.read().split()

with open(osp.join(collection_dir, 'speakers.txt'), 'r') as fspeakers:
	speakers = fspeakers.read().split()

with open(osp.join(collection_dir, 'pos.txt'), 'r') as fpos:
	pos = fpos.read().split()


# Assign transcript text to matched subtitle
for srt_file in os.listdir(srt_dir):
	# Current episode
	ep = srt_file[:5]
	print ep
	
	# Open the subtitle
	subs = pysrt.open(osp.join(srt_dir, srt_file))

	# Write to file
	fdata = open(osp.join(output_dir, ep + '.txt'), 'w')
	fdata.write('Frame_Start Frame_End Laugh Speaker Dialogue\n')
	for sub in subs:
		fstart = time_to_frame_num(time_in_sec(str_to_time_obj(str(sub.start))))
		fend = time_to_frame_num(time_in_sec(str_to_time_obj(str(sub.end))))
		text = sub.text
		if 'LAUGH' in text:
			laugh = 1
			text = text.replace('LAUGH', '')
		else:
			laugh = 0
		divided = text.split(':')
		if len(divided) > 1:
			speaker = divided[0].strip() # Extract speaker
			speakers.add(speaker) # Add speaker to speaker set
			dialogue = ' '.join(divided[1:]).strip() # Extract dialogue

			# Tokenize sentence and determine POS
			sent = ' '.join([str(word).strip(string.punctuation) for word in dialogue.split(' ') if word != ''])
			tags = nltk.pos_tag(nltk.word_tokenize(sent))

			# Add to collections
			[vocab.add(tag[0]) for tag in tags]
			[pos.add(tag[1]) for tag in tags]
		else:
			speaker = 'UNKNOWN'
			dialogue = divided[0]
			dialogue = ' '.join(divided[1:]).strip() # Extract dialogue

			# Tokenize sentence and determine POS
			sent = ' '.join([str(word).strip(string.punctuation) for word in dialogue.split(' ') if word != ''])
			tags = nltk.pos_tag(nltk.word_tokenize(sent))

			# Add to collections
			[vocab.add(tag[0]) for tag in tags]
			[pos.add(tag[1]) for tag in tags]
		fdata.write('{},{},{},{},{}\n'.format(fstart, fend, laugh, speaker, dialogue))
	fdata.close()	

# Print vocab to file
fvocab = open(osp.join(output_dir, 'vocab.txt'), 'w')
for word in vocab:
	fvocab.write(word + '\n')
fvocab.close()

# Print parts of speech  to file
fpos = open(osp.join(output_dir, 'pos.txt'), 'w')
for p in pos:
	fpos.write(p + '\n')
fpos.close()

# Print speakers to file
fspeakers = open(osp.join(output_dir, 'speakers.txt'), 'w')
for speaker in speakers:
	fspeakers.write(speaker.upper() + '\n')
fspeakers.close()

print 'Vocab size: ', len(vocab)
print 'Number of speakers: ', len(speakers)
print 'Number of POS: ', len(pos)
