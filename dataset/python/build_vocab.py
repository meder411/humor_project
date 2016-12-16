import os.path as osp
import os
import pysrt
import datetime
import string
import nltk

# Directory tree
project_root = '..' 
srt_dir = osp.join(project_root, 'subtitles', 'full')
output_dir = osp.join(project_root, 'subtitles', 'organized_data')

# Vocabulary and speakers sets
vocab = dict()
speakers = dict()
pos = dict()

wnl = nltk.stem.WordNetLemmatizer()

# Assign transcript text to matched subtitle
for srt_file in os.listdir(srt_dir):
	# Current episode
	ep = srt_file[:5]
	print ep
	
	# Open the subtitle
	subs = pysrt.open(osp.join(srt_dir, srt_file))

	# Write to file
	for sub in subs:
		try:
			divided = sub.text.split(':')
			if len(divided) > 1:
				speaker = divided[0].strip().strip(string.punctuation).upper() # Extract speaker

				# Add speaker to speaker set
				if speaker not in speakers:
					speakers[speaker] = 1
				else:
					speakers[speaker] += 1

				dialogue = ' '.join(divided[1:]).strip() # Extract dialogue

				# Tokenize sentence and determine POS
				sent = ' '.join([str(word).strip(string.punctuation) for word in dialogue.split(' ') if word != ''])
				tags = nltk.pos_tag(nltk.word_tokenize(sent))

				# Add to collections
				for tag in tags:
					lemma = wnl.lemmatize(tag[0]).lower()
					if lemma not in vocab:
						vocab[lemma] = 1
					else:
						vocab[lemma] += 1
					if tag[1] not in pos:
						pos[tag[1]] = 1
					else:
						pos[tag[1]] += 1
			else:
				dialogue = ' '.join(divided).strip() # Extract dialogue

				# Tokenize sentence and determine POS
				sent = ' '.join([str(word).strip(string.punctuation) for word in dialogue.split(' ') if word != ''])
				tags = nltk.pos_tag(nltk.word_tokenize(sent))

				# Add to collections
				for tag in tags:
					lemma =wnl.lemmatize(tag[0]).lower()
					if lemma not in vocab:
						vocab[lemma] = 1
					else:
						vocab[lemma] += 1
					if tag[1] not in pos:
						pos[tag[1]] = 1
					else:
						pos[tag[1]] += 1
		except:
			pass


# Print vocab to file
fvocab = open(osp.join(output_dir, 'vocab.txt'), 'w')
for word in vocab:
	fvocab.write(word + ' ' +str( vocab[word]) + '\n')
fvocab.close()

# Print parts of speech  to file
fpos = open(osp.join(output_dir, 'pos.txt'), 'w')
for p in pos:
	fpos.write(p + '\n')
fpos.close()

# Print speakers to file
#fspeakers = open(osp.join(output_dir, 'speakers.txt'), 'w')
#for speaker in speakers:
#	fspeakers.write(speaker + '\n')
#fspeakers.close()

print 'Vocab size: ', len(vocab)
print 'Number of speakers: ', len(speakers)
print 'Number of POS: ', len(pos)
