__author__ = 'Marc Eder'
__date__ ='October 19, 2016'


# A script to parse the SRT files.
# (COMPLETE)	 	- Shifts the time stamps so that each episodes starts at 0:00:00.00
# (COMPLETE)		- Corrects misspelled words (a common issue is interchanging I <--> l)
# (TODO)		- Aligns character names with dialogue

import os
import os.path as osp
from nltk.tag import pos_tag
import enchant
import re
import codecs

# Functiion to verify that each word is valid (i.e. in the dictionary or a proper noun)
def replace(sp_dict, word, log_file, log_info):

	# Return if word is empty string
	if word == '':
		return word

	# Checks if the word is valid. If so, returns it back
	if sp_dict.check(word) or pos_tag([word]) == 'NNP':
		return word

	# If the word is invalid, check if replacing 'I' with 'l' returns a valid word
	ifix_word = word.replace('I', 'l')
	if sp_dict.check(ifix_word) or pos_tag([ifix_word]) == 'NNP':
		return ifix_word

	# Also try the reverse
	lfix_word = word.replace('l', 'I')
	if sp_dict.check(lfix_word) or pos_tag([lfix_word]) == 'NNP':
		return lfix_word

	# If there is a possesive suffix, return true if the base word is valid
	if word[-2:] == '\'s':
		if word[:-2] == replace(sp_dict, word[:-2], log_file, log_info):
			return word

	# If a capital 'I' falls in the middle of the word, replace it with a lowercase 'l'
	if 'I' in word[1:]:
		word = word[0] + word[1:].replace('I', 'l')
		return word

	# Corrects the common parsing mistake of 'IK' instead of 'K'
	if word[0] == 'I' and word[1].isupper():
		return word[1:]		

	# If it still fails at this point, use the word anyway, but log when this happens
	log_file.write(log_info + ' - \'' + word + '\'\n')
	return word



# Function to strip all punctuation at the start and end of a word
# e.g. '(the)' --> 'the', but 'don't' --> 'don't'
# Returns the leading punctuation, trailing puncutation, and word itself
def strip_external_punctuation(exclude, word):
	leading = ''
	trailing = ''
	word = word.strip()
	if len(word) >= 3:
		if word[:3] == '<i>':
			leading = '<i>'
			word = word[3:]
	if len(word) >= 4:
		if word[-4:] == '</i>':
			trailing = '</i>'
			word = word[:-4]
	if len(word) > 0:
		ch = word[0]
		while ch in exclude:
			leading += ch
			word = word[1:]
			if len(word) > 0:
				ch = word[0]
			else:
				ch = ''
	if len(word) > 0:
		ch = word[-1]
		while ch in exclude:
			trailing = ch + trailing
			word = word[:-1]
			if len(word) > 0:
				ch = word[-1]
			else:
				ch = ''
	return leading, trailing, word


####################
# FORMAT SRT FILES
####################
import pysrt
import os
import string

# Punctuation set for exclusion
exclude = set(string.punctuation)
exclude.add('<i>')
exclude.add('</i>')

# Load the Amerian English dictionary
spell_dict = enchant.Dict('en_US')

if not osp.exists('edited'):
	os.mkdir('edited')

log_file = codecs.open('spell_check_log.txt', 'w', encoding='utf-8')

# Go through each SRT file
for f in os.listdir('subtitles'):
	if f.endswith('.srt'):

		print f

		# Open the subtitle files
		subs = pysrt.open(osp.join('subtitles', f))

		# Remove the titular subtitle
		del subs[0]

		# Shift the timestamps
		subs.shift(milliseconds=-subs[0].start.milliseconds)
		subs.shift(seconds=-subs[0].start.seconds)
		subs.shift(minutes=-subs[0].start.minutes)

		# Correct spelling errors
		for i in xrange(len(subs)):

			log_info = '{}, {:02d}:{:02d}.{:03d}'.format(f, subs[i].start.minutes, subs[i].start.seconds, subs[i].start.milliseconds)

			# Break sentence into list of words
			words = subs[i].text.split(' ')

			# Separate any words that may be joined by a newline character and remove any all-whitespace words
			words = [w for word in words for w in word.split('\n') if not w.isspace() and w != '']

			# Spell-check words in subtitle text
			clean_text = []
			for word in words:
				leading, trailing, word = strip_external_punctuation(exclude, word)
				clean_text.append(leading + replace(spell_dict, word, log_file, log_info) + trailing)

			# Recombine subtitle
			fixed = ' '.join(clean_text)

			# Separate lines that may have been combined by mistake in parsing
			fixed = fixed.replace('-', '\n')


			# Remove any empty lines that may have been formed
			fixed = [phrase for phrase in fixed.split('\n') if not phrase.isspace() and phrase != '']
			subs[i].text = '\n'.join(fixed)

		# Save modified SRT file
		subs.save(osp.join('edited', 'edited_' + f), encoding='utf=8') 

import ngram

# Go through each SRT file
for transcript in os.listdir('transcripts'):
	if transcript.endswith('.txt'):
		with open(osp.join('transcripts', transcript), 'r') as f:

			basename = osp.splitext(transcript)[0]

			# Parse the transcript file and remove any non-dialogue (denoted by lines starting with punctuation)
			lines = f.readlines()
			lines = [line.replace('[', '\n[').strip() for line in lines]
			lines = [l for line in lines for l in line.split('\n') if not l.isspace() and l != ''] # Flatten list
			lines = [line for line in lines if line != '' and line[0] not in exclude]

			# Split the transcript into pairs of (single dialogue sentence, speaker)
			lines = [[line[line.find(':')+1:].strip(), line[:line.find(':')].strip()] for line in lines]
			lines = [zip(*[line[0].split('. '), [line[1] for i in xrange(len(line[0].split('. ')))]]) for line in lines]
			lines = [pair for line in lines for pair in line]

			# Now separate the dialogue and the speaker into two corresponding lists
			dialogue = [line[0] for line in lines]
			speakers = [line[1] for line in lines]
			
			# Open the corresponding edited subtitle file
			subs = pysrt.open(osp.join('edited', 'edited_' + basename + '.srt'))

			tmp = []
			for i in xrange(len(subs)):
				tmp.append(subs[i].text)
			G = ngram.NGram(tmp, N=9)
			for i in xrange(15):
				print 'SUB: ' + dialogue[i]
				print 'MATCH: ' + G.find(dialogue[i])


#			with open('test.txt', 'w') as fout:
#				fout.write('\n'.join(lines))


