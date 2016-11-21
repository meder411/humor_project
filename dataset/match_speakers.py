import os
import os.path as osp
import pysrt
from ngram import NGram


######################
# FORMAT TRANSCRIPTS
######################

seasons = [1,2]
for season in seasons:
	# Directory containing subtitle files
	srt_dir = osp.join('subtitles', 'edited', 'season' + str(season))

	# Run through each SRT file
	for srt in os.listdir(srt_dir):

		# Open SRT file
		subs = pysrt.open(osp.join(srt_dir, srt))

		# Get basename of file and episode number
		basename = osp.splitext(srt)[0]
		ep = int(basename[2:])

		# Load the scene transcripts corresponding to the episode
		transcript_dir = osp.join('transcripts', 'scenes', 'season' + str(season))
		transcripts = []
		for scene in os.listdir(transcript_dir):
			if scene.startswith(basename + '_'):
				with open(osp.join(transcript_dir, scene)) as fscene:
					# Split the transcript into pairs of (single dialogue sentence, speaker)
					lines = fscene.readlines()
					lines = [[line[line.find(':')+1:].strip(), line[:line.find(':')].strip()] for line in lines]

					# Now separate the dialogue and the speaker into two corresponding lists
					dialogue = [line[0] for line in lines]
					speakers = [line[1] for line in lines]
					transcripts.append([speakers, dialogue])

		# Figure out where each scene ends in the subtitle
		scene_num = 0
		match_threshold = 0.15 # NGram matching confidence required to declare a match
		sub_idx = 0 # Index of subtitle list
		while scene_num < len(transcripts):
			speakers = transcripts[scene_num][0]
			dialogue = transcripts[scene_num][1]
			dialogue_len = len(dialogue)
			dialogue_idx = 0 # Index of dialogue list
			num_fails = 0 # Number of dialogue pairs in which no match was found for current subtitle
			return_to_dialogue_idx = 0 # Dialogue index to return to for next subtitle if no match is ever found for current subtitle
			while dialogue_idx < dialogue_len and sub_idx < len(subs):
				next_dialogue_idx = min(dialogue_idx+1, dialogue_len-1)
				curr_line = dialogue[dialogue_idx]
				next_line = dialogue[next_dialogue_idx]
				curr_sub = subs[sub_idx].text
				curr_score = NGram.compare(curr_line, curr_sub)
				next_score = NGram.compare(next_line, curr_sub)
				print curr_score, next_score, dialogue_idx
				# If we're somewhat confident that a match is found, handle it
			#	if curr_score > match_threshold or next_score > match_threshold:
				# If the subtitle matches to the current line of dialogue
				# better than it matches to the next one, assign it the speaker of this line
				# and increment the subtitle index to the next one
				if curr_score >= next_score:
					subs[sub_idx].text = speakers[dialogue_idx] + ': ' + curr_sub
					sub_idx += 1
					num_fails = 0
				# If the better match is to the next line of dialogue, then
				# assign the speaker of the next line to this subtitle and increment
				# both the subtitle and the dialogue to dialogue to the next one
				else:
					subs[sub_idx].text = speakers[next_dialogue_idx] + ': ' + curr_sub
					sub_idx += 1
					dialogue_idx += 1
					return_to_dialogue_idx = dialogue_idx
					num_fails = 0

#				print subs[sub_idx].text
			break	

