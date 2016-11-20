import os
import os.path as osp
import pysrt



######################
# FORMAT TRANSCRIPTS
######################


seasons = [1,2]
for season in seasons:
	# Directory containing subtitle files
	srt_dir = osp.join('subtitles', 'edited', 'season' + str(season))

	# Run through each SRT file
	for srt in os.listdir(srt_dir):
		subs = pysrt.open(osp.join(srt_dir, srt))
		basename = osp.splitext(srt)[0]
		print basename
		ep = int(basename[2:])
			
		print ep
