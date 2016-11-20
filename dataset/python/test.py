import os
import os.path as osp
import codecs
import re
from ngram import NGram
import string
import pysrt
import jellyfish
import numpy as np

# Function to remove parentheticals from lines
# Courtesy of this answer http://stackoverflow.com/a/14598135/3427580
def remove_parentheticals(line):
    ret = ''
    skip1c = 0
    skip2c = 0
    for i in line:
        if i == '[':
            skip1c += 1
        elif i == '(':
            skip2c += 1
        elif i == ']' and skip1c > 0:
            skip1c -= 1
        elif i == ')'and skip2c > 0:
            skip2c -= 1
        elif skip1c == 0 and skip2c == 0:
            ret += i
    return ret

def fix_delim(lines, line_ends):
	for i in reversed(xrange(len(lines) - 1)):
		if not lines[i][0]:
			del lines[i]
			continue
		if lines[i][0][:2] in line_ends:
			lines[i-1][0] = lines[i-1][0] + lines[i][0][0]
			del lines[i]
	return lines

def get_all_substrings(min_word_len, max_word_len, line):
	words = line.split(' ')
	num_words = len(words)
	sublines = []
	# If there are fewer words in line than the minimum word-size of our desired substrings,
	# Just return line (as a list to match format of substrings being returned)
	if num_words < min_word_len:
		return [line]
	# If there are fewer words in line than the maximum word-size desired, change the max
	# to be the number of words in the string (i.e. the whole string)
	if num_words < max_word_len:
		max_word_len = num_words
	# Loop over the string pulling sub-sequences of words
	for l in xrange(min_word_len, max_word_len+1):
		sublines += [' '.join(words[i:i+l]) for i in xrange(num_words-l+1)]
	return sublines


######################
# FORMAT TRANSCRIPTS
######################

exclude = set(string.punctuation)
delim = map(re.escape, ['. ', '? ', '! ', '\n', '\r'])
delim = ['(' + d + ')' for d in delim if d != '\n' and d != '\r']
delim = '|'.join(delim)
line_ends = set(['. ','! ','? '])

#flog = codecs.open(osp.join('logs', 'speaker_matching_log.txt'), 'w', 'utf-8')

# Go through each transcript file
for transcript in os.listdir('transcripts'):
	if transcript.endswith('.txt'):
		with codecs.open(osp.join('transcripts', transcript), 'r', 'utf-8') as f:

			basename = osp.splitext(transcript)[0]
			print basename

			# Parse the transcript file and remove any non-dialogue (denoted by lines starting with punctuation)
			lines = f.readlines()
			lines = [line.decode('utf-8', 'ignore').encode('ascii', 'ignore') for line in lines]
			lines = [remove_parentheticals(line).strip() for line in lines]
			lines = [l for line in lines for l in line.split('\n') if not l.isspace() and l != ''] # Flatten list
			lines = [line for line in lines if line != '' and line[0] not in exclude]
			
			# Split the transcript into pairs of (single dialogue sentence, speaker)
			# Extract speaker and dialogue separately
			lines = [[line[line.find(':')+1:].strip(), line[:line.find(':')].strip()] for line in lines]

			# Now separate the dialogue and the speaker into two corresponding lists
			dialogue = [line[0] for line in lines]
			speakers = [line[1] for line in lines]
		
			# Open the corresponding edited subtitle file
			subs = pysrt.open(osp.join('edited', 'edited_' + basename + '.srt'))
			print dialogue
		break
