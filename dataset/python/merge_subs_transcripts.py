import os.path as osp
import os
import pysrt
from nltk.tag import pos_tag
import datetime

project_root = '..' 
matches_dir = osp.join(project_root, 'matches')
srt_dir = osp.join(project_root, 'subtitles', 'edited')
transcript_dir = osp.join(project_root, 'transcripts', 'scenes')
laughs_file = osp.join(project_root, 'laugh_times.txt')
output_dir = osp.join(project_root, 'subtitles', 'full')

def str_to_time_obj(string):
	return datetime.time(int(string[0:2]), int(string[3:5]), int(string[6:8]), int(string[9:]) * 1000)

def time_in_sec(time):
	return time.hour * 3600 + time.minute * 60 + time.second + time.microsecond * 10e-7

# This should be called after reassigning subtitle texts
# i.e sub1 and sub2 should have the same text
def merge_subtitles(sub1, sub2):
	# Pick the index
	idx = min(sub1.index, sub2.index)

	# Pick the earlier starting time
	start1 = str_to_time_obj(str(sub1.start))
	start2 = str_to_time_obj(str(sub2.start))
	if start1 < start2:
		start = str(sub1.start)
	else:
		start = str(sub2.start)

	# Pick the later starting time
	end1 = str_to_time_obj(str(sub1.end))
	end2 = str_to_time_obj(str(sub2.end))
	if end1 > end2:
		end = str(sub1.end)
	else:
		end = str(sub2.end)

	# Return new SRT item
	return pysrt.SubRipItem(idx, start=start, end=end, text=str(sub1.text))	

# Index the laugh occurences
with open(laughs_file, 'r') as flaughs:
	laughs = flaughs.readlines()
	laughs = [laugh.strip().split() for laugh in laughs]
	laugh_dict = {laugh[0] : [int(round(float(l))) for l in laugh[1:]] for laugh in laughs} # Subtract 1 second from the laugh time (as in originial paper)

# Assign transcript text to matched subtitle
for matches in os.listdir(matches_dir):
	if matches.endswith('.matches'):
		# Current episode
		ep = matches[:5]
		print ep
		
		# Open the subtitle->transcript matches
		with open (osp.join(matches_dir, matches)) as fmatches:
			pairs = fmatches.readlines()[1:]
			pairs = [map(int, pair.strip().split()) for pair in pairs]
		
		# Open the subtitles	
		subs = pysrt.open(osp.join(srt_dir, ep + '.srt'))

		# Open the transcript
		with open(osp.join(transcript_dir, ep + '.txt')) as ftrans:
			lines = ftrans.readlines()

		# Assign the transcript text to the matching subtitle
		for pair in pairs:
			if pair[1] >= 0:
				subs[pair[0]-1].text = lines[pair[1]-1]

		# Merge subtitles that match to the same transcript line
		for i in xrange(len(pairs)-1, 0, -1):
			if pairs[i-1][1] == pairs[i][1] and pairs[i][1] >= 0:
				subs[pairs[i-1][0]-1] = merge_subtitles(subs[pairs[i-1][0]-1], subs[pairs[i][0]-1])
				del subs[pairs[i][0]-1]
		subs.clean_indexes()

		# Assign LAUGH indicators
		laughs = laugh_dict[ep]
		laugh_idx = 0
		sub_idx = 0
		while laugh_idx < len(laughs) and sub_idx < len(subs)-1:
			start1 = str(subs[sub_idx].start)
			end2 = str(subs[sub_idx+1].end)
			# If a laugh falls between two subtitles, mark the earlier one as the punchline
			if time_in_sec(str_to_time_obj(start1)) < laughs[laugh_idx] < time_in_sec(str_to_time_obj(end2)):
				subs[sub_idx+1].text = subs[sub_idx+1].text.strip() + ' LAUGH'
				laugh_idx += 1
				sub_idx += 1
			# If the first laugh time is before any dialogue, skip it
			elif laughs[laugh_idx] < time_in_sec(str_to_time_obj(str(subs[0].start))):
 				laugh_idx += 1
			else:
				sub_idx += 1
		# If there are still laughs remaining (hopefully no more than 1...), assign it to the last subtitle
		if laugh_idx < len(laughs):
			subs[len(subs)-1].text = subs[len(subs)-1].text.strip() + ' LAUGH'

		subs.save(osp.join(output_dir, ep + '.srt')) 
