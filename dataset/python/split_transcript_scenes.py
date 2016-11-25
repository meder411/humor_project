import os
import os.path as osp
import string
import codecs
from html2text import html2text
import unidecode
import unicodedata 
import string
import re

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


# Exclusion characters
exclude = set(string.punctuation)

# Season number
seasons = [1, 2]
project_root = '..'
scenes_dir = osp.join(project_root, 'transcripts', 'scenes')


# Go through each transcript file
for season in seasons:
	html_dir = osp.join(project_root, 'transcripts', 'html', 'season' + str(season))
	for transcript in os.listdir(html_dir):
		if transcript.endswith('.html'):
			with codecs.open(osp.join(html_dir, transcript), 'r', 'latin-1') as f:
#				if transcript == '0106.html':
					# Episode number
					ep = int(osp.splitext(transcript)[0][-2:])
					print season, ', ', ep
					# Read the HTML file and parse it
					html = f.read()
					html = unicodedata.normalize('NFKD', html).encode('ascii', 'ignore')
					lines = unidecode.unidecode(html2text(html))

					# Break into scenes
					lines = lines.replace('**', '')
					scenes = ['[Scene' + e for e in lines.split('[Scene') if e != ""]
					if len(scenes) > 1:
						scenes = scenes[1:] # Ignore header info if scenes able to be broken up

					# Go through each scene
					for i in xrange(len(scenes)):
						# Process scenes
						#print scene[i]
						lines = re.split(r'\n\s*\n', scenes[i]) # Split at new-lines
						# Remove all parenthetical phrases
						lines = [line.strip().replace('\n',' ') for line in lines]
						lines = [re.sub(r'\(.*\)|\[.*\]', '', line) for line in lines]
						lines = [line for line in lines if line != '' and line.lower() != 'commercial break' and 
							line.lower() != 'opening credits' and line.lower() != 'closing credits' and line.lower() != 'end' and
							not line.isspace()]

						# Rejoin list into a string
						scenes[i] = '\n'.join(lines)

					# Write to file with SCENE markers
					scenes_output = '\n\nSCENE BREAK\n\n'.join(scenes)
					with open(osp.join(scenes_dir, '{0:02d}_{1:02d}.txt'.format(season, ep)), 'w') as fout:
						fout.write(scenes_output)

