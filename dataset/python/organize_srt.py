import os.path as osp
import os
import pysrt
import datetime

# Directory tree
project_root = '..' 
srt_dir = osp.join(project_root, 'subtitles', 'full')
output_dir = osp.join(project_root, 'organized_data')

def time_to_frame_num(secs):
	fps = 23.976
	return fps * secs

def str_to_time_obj(string):
	return datetime.time(int(string[0:2]), int(string[3:5]), int(string[6:8]), int(string[9:]) * 1000)

def time_in_sec(time):
	return time.hour * 3600 + time.minute * 60 + time.second + time.microsecond * 10e-7

# Assign transcript text to matched subtitle
for srt_file in os.listdir(srt_dir):
	# Current episode
	ep = matches[:5]
	print ep
	
	# Open the subtitle
	subs = pysrt.open(osp.join(srt_dir, srt_file))

	# Write to file
	with open(osp.join(output_dir, ep + '.txt')) as fout:
		fout.write('Frame_Start Frame_End Laugh Speaker Dialogue\n')
		for sub in subs:
			fstart = time_to_frame_num(time_in_sec(str_to_time_obj(str(sub.start))))
			fend = time_to_frame_num(time_in_sec(str_to_time_obj(str(sub.end))))
			text = sub.text
			if 'LAUGH' in text:
				laugh = 1
				text.replace('LAUGH', '')
			else:
				laugh = 0
			speaker = text.split(':')[0].strip()
			dialogue = text.split(':')[1].strip()
			fout.write('{} {} {} {} {}\n'.format(fstart, fend, laugh, speaker, dialogue))
