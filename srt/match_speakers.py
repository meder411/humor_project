import os
import os.path as osp
import re
import ngram
import string
import pysrt
import math

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

######################
# FORMAT TRANSCRIPTS
######################

exclude = set(string.punctuation)
#delim = '|'.join(map(re.escape, ['. ', '? ', '! ', '\n', '\r']))
delim = map(re.escape, ['. ', '? ', '! ', '\n', '\r'])
delim = ['(' + d + ')' for d in delim if d != '\n' and d != '\r']
delim = '|'.join(delim)
line_ends = set(['. ','! ','? '])

def fix_delim(lines, line_ends):
	for i in reversed(xrange(len(lines) - 1)):
		if not lines[i][0]:
			del lines[i]
			continue
		if lines[i][0][:2] in line_ends:
			lines[i-1][0] = lines[i-1][0] + lines[i][0][0]
			del lines[i]
	return lines

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
			# Split multi-sentence lines into separate (phrase, speaker) groupings
			lines = [zip(*[re.split(delim, line[0]), [line[1] for i in xrange(len(re.split(delim, line[0])))]]) for line in lines]
			lines = [list(pair) for line in lines for pair in line if pair[0]]
			# Re-insert the deliminaters that we split on
			lines = fix_delim(lines, line_ends)
			# Strip any last whitespace
			lines = [(line[0].strip(), line[1].strip()) for line in lines]

			# Now separate the dialogue and the speaker into two corresponding lists
			dialogue = [line[0] for line in lines]
			speakers = [line[1] for line in lines]
		
			# Open the corresponding edited subtitle file
			subs = pysrt.open(osp.join('edited', 'edited_' + basename + '.srt'))

			rng = 0.33 # Range of the transcript to check
			num_top_matches = 8
			num_speakers_matched = 0 # Number of speakers identified
			num_lines_examined = 0 # Number of lines queried
			for i in xrange(len(subs)):
				sub_dist = float(i) / float(len(subs))
				start_idx = max(0, int(math.floor(sub_dist * len(subs)) - 4))
				end_idx = min(int(math.ceil(start_idx + rng * len(dialogue))), len(dialogue))
				print start_idx, end_idx
				G = ngram.NGram(dialogue[start_idx : end_idx], N=4)
				lines = [line[1:] if line[0] == '-' else line for line in subs[i].text.split('\n-')]
				new_subtitle = ''
				for line in lines:
					num_lines_examined += 1
					print 'QUERY: ' + line
					closest_matches = G.search(line)[:num_top_matches]
					print closest_matches
					matches, scores = zip(*closest_matches)
					num_speakers_matched += 1
					match = matches[0]
					match_idx = dialogue.index(matches[0])
					speaker = speakers[match_idx]
					new_subtitle += speaker + ': ' + line + '\n'
				if new_subtitle:
					subs[i].text = new_subtitle
				print 'UPDATED: ' + subs[i].text
					
			subs.save(osp.join('edited', 'speakers_' + basename + '.srt'), encoding='utf=8') 

			print 'Number of speakers matches: {} / {}'.format(num_speakers_matched, num_lines_examined)





