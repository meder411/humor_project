import os
import os.path as osp
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
	for l in xrange(min_word_len, max_word_len+1):
		sublines += [' '.join(words[i:i+l]) for i in xrange(num_words-l)]
	return sublines

######################
# FORMAT TRANSCRIPTS
######################

exclude = set(string.punctuation)
delim = map(re.escape, ['. ', '? ', '! ', '\n', '\r'])
delim = ['(' + d + ')' for d in delim if d != '\n' and d != '\r']
delim = '|'.join(delim)
line_ends = set(['. ','! ','? '])

# Go through each transcript file
for transcript in os.listdir('transcripts'):
	if transcript.endswith('.txt'):
		with open(osp.join('transcripts', transcript), 'r') as f:

			basename = osp.splitext(transcript)[0]

			# Parse the transcript file and remove any non-dialogue (denoted by lines starting with punctuation)
			lines = f.readlines()
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

			num_speakers_matched = 0 # Number of speakers identified
			num_lines_examined = 0 # Number of lines queried
			dist = []
			dialogue_idx = 0
			sub_idx = 0
			tmp = 0
			while dialogue_idx < len(dialogue)-1 and sub_idx < len(subs) and tmp < 30:
				tmp+=1
				curr_line = dialogue[dialogue_idx]
				next_line = dialogue[dialogue_idx+1]
				curr_sub = subs[sub_idx].text
				curr_score = NGram.compare(curr_line, subs[sub_idx].text)
				next_score = NGram.compare(next_line, subs[sub_idx].text)

				# If the subtitle matches to the current line of dialogue
				# better than it matches to the next one, assign it the speaker of this line
				# and increment the subtitle index to the next one
				if curr_score >= next_score:
					print 'BEFORE: ' + subs[sub_idx].text
					subs[sub_idx].text = speakers[dialogue_idx] + ': ' + subs[sub_idx].text
					print 'AFTER: ' + subs[sub_idx].text
					sub_idx += 1
				# If the better match is to the next line of dialogue, then
				# don't do anything with this subtitle and just increment the
				# dialogue to the next line (only problematic if the 'line-after-that'
				# is better than the next line--in that case we skip dialogue)
				else:
					dialogue_idx += 1

			subs.save(osp.join('edited', 'speakers_' + basename + '.srt'), encoding='utf=8') 

			print 'Number of speakers matches: {} / {}'.format(num_speakers_matched, num_lines_examined)

			break
