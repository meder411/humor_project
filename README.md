This is code for my project to detect humor in videos by leveraging both visual cues and dialogue.


The project has 3 components:

1. Building a humor dataset that explicitly aligns visuals wih language in humorous situations
2. Detecting and describing the speakers' expressions
3. The actual humor detection


This repository contains the files listed below. All code is my work unless indicated below or in the code's comments where relevant.

	|>> face_description : Top-level Directory for face detection and description
	|	|
	|	|>> facenet : Neural network components
	|	|	|
	|	|	|>> layers: Directory containing soft-links to a modified version of Caffe's sigmoid_cross_entropy_layer (now it can accept class weights)
	|	|	|	|
	|	|	|	|-- weighted_sigmoid_cross_entropy_loss_layer.cpp
	|	|	|	|-- weighted_sigmoid_cross_entropy_loss_layer.hpp
	|	|	|	|-- weighted_sigmoid_cross_entropy_loss_layer.cu
	|	|	|	=
	|	|	|	
	|	|	|>> models: Directory containing .prototxt files describing the FaceNet architecture
	|	|	|	|
	|	|	|	|--facenet_train_solver.prototxt : solver parameters file
	|	|	|	|--facenet_train.prototxt : train net (provided by FaceNet authors)
	|	|	|	|--facenet_test.prototxt : test net
	|	|	|	|--facenet_valid.prototxt : validation net
	|	|	|	=
	|	|	|
	|	|	|-- amfed_label_weights.txt : List of class weights based on negative:positive sample ratio
	|	|	|-- amfed_test_labels.txt : Test set
	|	|	|-- amfed_train_labels.txt : Training set
	|	|	|-- amfed_valid_labels.txt : Validation set
	|	|	|-- facenet_data_layer : Custom Python data layer to load images into FaceNet
	|	|	|-- network_util.py : Utility functions for FaceNet
	|	|	|-- test_facenet.py : Script to test the network
	|	|	|-- train_facenet.py : Script to train the network
	|	|	=
	|	|
	|	|>> matlab : Directory containing tools for video sampling and face extraction
	|	|	|>> +lib : Directory containing functions for face detection and cropping (only cropping is used) (from FaceNet creators) 
	|	|	|-- points2xyxy.m : Function to convert bounding box representation
	|	|	|-- tlwh2xyxy.m : Another function to convert bounding box representation
	|	|	|-- sample_video.m : Script to automatically extract faces from videos
	|	|	=
	|	|	
	|	|-- number_of_frames.txt : File mapping AMFED videos to the number of frames in the video
	|	|-- organize_amfed.py : Script to unify the AMFED dataset (the data is highly disorganized) and generate the training, test, and validation sets for FaceNet
	|	=
	|
	|>> dataset : Top-level directory for components related to building the dataset
	|	|
	|	|>> edited : Directory to store subtitle files after they have been edited for OCR mistakes (dialogue with time-of-appearance, no speakers)
	|	|>> transcripts : Directory to store transcripts of episodes (just dialogue, with speakers)
	|	|>> full_subtitles : Directory to store merged subtitles and transcripts (full dialogue with speakers and time-of-appearance)
	|	|>> subtitles : Directory to store raw subtitles ripped from the DVDs
	|	|>> logs : Directory containing logs of spell-checking and speaker matching
	|	|-- format_srt.py : Script to spell-check and parse the raw subtitles
	|	|-- match_speakers_old.py : Script to attempt to assign speakers from transcripts to lines in subtitles using N-gram matching of lines (old version)
	|	|-- match_speakers.py : Better script to assign speakers to subtitles. Takes advantage of inherent ordering, but still uses N-gram similarity
	|	=
	|
	|>> sentence_encoding : Top-level directory for sentences feature extraction (currently empty)
	|
	|>> humor_detector : Top-level directory for components of the final system (currently empty)
