import os
import os.path as osp
import string
import codecs
from html2text import html2text
import unidecode
import unicodedata 
import string

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


# Go through each transcript file
for season in seasons:
	html_dir = 'transcripts/html/season' + str(season)
	for transcript in os.listdir(html_dir):
		if transcript.endswith('.html'):
			with codecs.open(osp.join(html_dir, transcript), 'r', 'latin-1') as f:

				# Episode number
				ep = osp.splitext(transcript)[0][-2:]

				# Read the HTML file and parse it
				html = f.read()
				html = unicodedata.normalize('NFKD', html).encode('ascii', 'ignore')
				lines = unidecode.unidecode(html2text(html))

				# Break into scenes
				lines = lines.replace('**', '')
				scenes = ['[Scene' + e for e in lines.split('[Scene') if e != ""]
				scenes = scenes[1:] # Ignore header info

				# Go through each scene
				for i in xrange(len(scenes)):
					# Process scenes
					lines = scenes[i].split('\n') # Split at new-lines

					# Remove all parenthetical phrases
					lines = [remove_parentheticals(line).strip() for line in lines]
					lines = [l for line in lines for l in line.split('\n') if not l.isspace() and l != ''] # Flatten list
					lines = [line for line in lines if line != '' and line[0] not in exclude and ':' in line]

					# Rejoin list into a string
					scenes[i] = '\n'.join(lines)

				# Write to file with SCENE markers
				# Scenes output directory
				scenes_dir = osp.join('transcripts', 'scenes', 'season' + str(season))
				if not osp.exists(scenes_dir):
					os.mkdir(scenes_dir)
				scenes_output = '\n\nSCENE BREAK\n\n'.join(scenes)
				with open(osp.join(scenes_dir, 'ep' + str(ep) + '.txt'), 'w') as fout:
					fout.write(scenes_output)

