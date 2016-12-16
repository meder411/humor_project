This is code for my project to detect humor in videos by leveraging both visual cues and dialogue.


The project has 3 components:

1. Building a humor dataset that explicitly aligns visuals wih language in humorous situations
2. Encoding video data
3. The actual humor detection


This repository contains the files listed below. All code is my work unless indicated below or in the code's comments where relevant.

	|>> face_description : Top-level Directory for face detection and description (DEPRECATED)
	|
	|
	|>> dataset : Top-level directory for components related to building the dataset
	|	|
	|	|>> edited : Subtitle files edited for OCR mistakes
	|	|>> transcripts : Transcripts of episodes (just dialogue, with speakers)
	|	|>> full_subtitles : Merged subtitles and transcripts (full dialogue, speakers, and time)
	|	|>> subtitles : Directory to store raw subtitles ripped from the DVDs (time, no speakers)
	|	|>> matlab : MATLAB files
	|	|	|-- find_laughs.m : Script to detect laughter from episode audio tracks
	|	|	|-- new_friends_labeling_tool.fig : Layout of labeling tool
	|	|	|-- new_friends_labeling_tool.m : Labeling tool
	|	|	=
	|	|
	|	|>> old : Old stuff (DEPRECATED)
	|	|
	|	|>> logs : Directory containing logs of spell-checking and speaker matching
	|	|>> python : Python files
	|	|	|-- build_vocab.py : Script to compile vocabulary files (words, speakers, POS)
	|	|	|-- merge_subs_transcripts.py : Align speakers with subtitles (from MATLAB output)
	|	|	|-- format_srt.py : Script to spell-check and parse the raw subtitles
	|	|	|-- organize_srt.py : Script to organize the text data for loading into LSTM
	|	|	|-- match_speakers_old.py : Script to assign speakers with subtitles (old version)
	|	|	|-- match_speakers.py : Better script to assign speakers to subtitles.
	|	|	|-- split_transcript_scenes.py : Split episode transcripts into scenes
	|	|	|-- html2text.py : Aaron Swartz's library for converting HTML to plain text
	|	=
	|
	|>> scene_encoding : Top-level directory for video frame feature extraction
	|	|
	|	|--vgg.protoxt : humor LSTM architecture
	|	|--humornet_solver.prototxt : solver parameters file
	|	|--vgg_data_layer : Python data layer to load data into network
	|	|--extract_features.py : Python script to extract video feature the network
	|	=
	|
	|>> humor_net : Neural network components
	|	|
	|	|--humornet.protoxt : humor LSTM architecture
	|	|--humornet_solver.prototxt : solver parameters file
	|	|--humornet_data_layer : Python data layer to load data into network
	|	|--train_humornet.py : Python script to train the network
	|	=
