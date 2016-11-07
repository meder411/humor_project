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
			#flog.write('EXAMINING {}\n----------\n\n'.format(basename))

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
			match_threshold = 0.15 # NGram matching confidence required to declare a match
			dialogue_idx = 0 # Index of dialogue list
			sub_idx = 0 # Index of subtitle list
			num_fails = 0 # Number of dialogue pairs in which no match was found for current subtitle
			return_to_dialogue_idx = 0 # Dialogue index to return to for next subtitle if no match is ever found for current subtitle
			while dialogue_idx < len(dialogue) and sub_idx < len(subs):
				next_dialogue_idx = min(dialogue_idx+1, len(dialogue)-1)
				curr_line = dialogue[dialogue_idx]
				next_line = dialogue[next_dialogue_idx]
				curr_sub = subs[sub_idx].text
				curr_score = NGram.compare(curr_line, curr_sub)
				next_score = NGram.compare(next_line, curr_sub)
				#flog.write('SUBTITLE: ' + curr_sub + '\n')
				#flog.write('DIALOGUE_PAIR: ({}, {}), ({}, {})\n'.format(curr_line, curr_score, next_line, next_score))
				# If we're somewhat confident that a match is found, handle it
				if curr_score > match_threshold or next_score > match_threshold:
					# If the subtitle matches to the current line of dialogue
					# better than it matches to the next one, assign it the speaker of this line
					# and increment the subtitle index to the next one
					if curr_score >= next_score:
						subs[sub_idx].text = speakers[dialogue_idx] + ': ' + curr_sub
						#flog.write('RESULT: ' + subs[sub_idx].text + '\n')
						sub_idx += 1
						num_fails = 0
					# If the better match is to the next line of dialogue, then
					# assign the speaker of the next line to with this subtitle and increment
					# both the subtitle and the dialogue to dialogue to the next one
					else:
						subs[sub_idx].text = speakers[next_dialogue_idx] + ': ' + curr_sub
						#flog.write('RESULT: ' + subs[sub_idx].text + '\n')
						sub_idx += 1
						dialogue_idx += 1
						return_to_dialogue_idx = dialogue_idx
						num_fails = 0
					num_speakers_matched += 1
				# If we're not very confident in a match, find the matching scores of the
				# subtitle against each substring of the same length within the line.
				else:
					#flog.write('--CHECKING SUBSTRINGS--\n')
					num_words = len(curr_sub.split(' '))
					# Evaluate current dialogue line's substrings
					curr_line_substrings = get_all_substrings(num_words, num_words, curr_line)
					curr_line_ngrams = NGram(curr_line_substrings)
					curr_searches = curr_line_ngrams.search(curr_sub)
					if curr_searches:
						curr_candidate_matches, curr_candidate_scores = zip(*curr_searches)
						curr_max_substring_score = max(curr_candidate_scores)
						curr_line_substring_line = curr_candidate_matches[np.argmax(curr_candidate_scores)]
					else:
						# If no matches are returned, give a max score of 0
						curr_max_substring_score = 0.0
						curr_line_substring_line = None
					# Evaluate next dialogue line's substrings
					next_line_substrings = get_all_substrings(num_words, num_words, next_line)
					next_line_ngrams = NGram(next_line_substrings)
					next_searches = next_line_ngrams.search(curr_sub)
					if next_searches:
						next_candidate_matches, next_candidate_scores = zip(*next_searches)
						next_max_substring_score = max(next_candidate_scores)
						next_line_substring_line = next_candidate_matches[np.argmax(next_candidate_scores)]
					else:
						# If no matches are returned, give a max score of 0
						next_max_substring_score = 0.0
						next_line_substring_line = None
#					print (curr_line_substring_line, curr_max_substring_score), (next_line_substring_line, next_max_substring_score)
					# Check if we now have a matching score above the match threshold
					if curr_max_substring_score > match_threshold or next_max_substring_score > match_threshold:
						# If we do, choose the line of dialogue in the same way as before
						if curr_max_substring_score >= next_max_substring_score:
							subs[sub_idx].text = speakers[dialogue_idx] + ': ' + curr_sub
							#flog.write('RESULT: ' + subs[sub_idx].text + '\n')
							sub_idx += 1
							num_fails = 0
						else:
							subs[sub_idx].text = speakers[next_dialogue_idx] + ': ' + curr_sub
							#flog.write('RESULT: ' + subs[sub_idx].text + '\n')
							sub_idx += 1
							dialogue_idx += 1
							return_to_dialogue_idx = dialogue_idx
							num_fails = 0
						num_speakers_matched += 1
					# If there is still no confidence match, then move on to the next line
					# of dialogue because neither of these are probably right
					else:
						dialogue_idx += 1
						num_fails += 1
						#flog.write('>>==MOVING TO NEXT DIALOGUE (fails: {})\n'.format(num_fails))
				# If the subtitle hasn't been found in 3 dialogue lines, skip it and return the dialogue index
				# to where it was before we started checking the failed subtitle
				if num_fails >= 5:
					#flog.write('--GIVING UP ON SUBTITLE--\n')
					dialogue_idx = return_to_dialogue_idx
					sub_idx += 1
					num_fails = 0
			#flog.write('\n\n')
			subs.save(osp.join('edited', 'speakers_' + basename + '.srt'), encoding='utf=8') 

			print 'Number of speakers matches: {} / {}'.format(num_speakers_matched, len(subs))

#flog.close()
