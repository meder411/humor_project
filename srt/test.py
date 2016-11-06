
def get_all_substrings(min_word_len, max_word_len, line):
	words = line.split(' ')
	num_words = len(words)
	sublines = []
	for l in xrange(min_word_len, max_word_len+1):
		sublines += [' '.join(words[i:i+l]) for i in xrange(num_words-l)]
	return sublines


z = 'i hate that this isnt working right now. what the hell can i do?'


print get_all_substrings(3, 4, z)
