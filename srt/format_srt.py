import enchant

def levenshteinDistance(s1, s2):
	if len(s1) > len(s2):
		s1, s2 = s2, s1

	distances = range(len(s1) + 1)
	for i2, c2 in enumerate(s2):
		distances_ = [i2+1]
	for i1, c1 in enumerate(s1):
		if c1 == c2:
			distances_.append(distances[i1])
	else:
		distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
		distances = distances_
	return distances[-1]

def replace(sp_dict, word, edit_dist):

	if sp_dict.check(word):
		return word

	suggestions = sp_dict.suggest(word)

	if suggestions and levenshteinDistance(word, suggestions[0]) <= edit_dist:
		return suggestions[0]
	else:
		return word


####################
# FORMAT SRT FILES
####################
import pysrt
import os
import string

exclude = set(string.punctuation)
spell_dict = enchant.Dict('en_US')

for f in os.listdir('.'):
	if f.endswith('.srt'):

		subs = pysrt.open(f)
#		subs.shift(index=-subs[0].index)
		subs.shift(milliseconds=-subs[0].start.milliseconds)
		subs.shift(seconds=-subs[0].start.seconds)
		subs.shift(minutes=-subs[0].start.minutes)
		for i in xrange(1):#xrange(len(subs)):
#			text = ''.join(ch for ch in subs[i].text if ch not in exclude)
			words = subs[i].text.split()
			for word in words:
				print replace(spell_dict, word, 8)
	


		subs.save('shifted_' + f, encoding='utf=8') 
