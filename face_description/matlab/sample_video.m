%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Author: Marc Eder
% Date: October 30, 2016
% Description:
%   Detects faces in each video, and writes the detection to file as a
%   224x224 dimensions JPG image. Also prints a file with video names
%   and number of frames in each.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Output directories
vid_dir = '../AMFED/Video - AVI/';
log_dir = '../logs';
output_dir = '../frames';

% Open files for writing
fid_frames = fopen('../number_of_frames.txt', 'w');
fid_log = fopen(fullfile(log_dir, 'vid_sampling_log.txt'), 'w');

% Initialize MATLAB's face detector (works better than the one shipped with VGG-Face)
face_detection = vision.CascadeObjectDetector();

% Get list of videos 
vids = dir(fullfile(vid_dir, '*.avi'));
vids = {vids(:).name};

% Go through each video
for i = 1 : length(vids)
	[~, basename, ~] = fileparts(vids{i}); % Get the file's basename

	% Make the output subdirectory if necessary
	if ~exist(fullfile(output_dir, basename), 'dir')
		mkdir(fullfile(output_dir, basename));
	end

	% Load the video
	V = VideoReader(fullfile(vid_dir, vids{i}));
	
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Find an initial detection
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Only really need one detection because the faces move so
	% infrequently in this dataset)
	detection = [];
	frame_num = 0;
	while isempty(detection) && hasFrame(V)
		frame = readFrame(V);
		detection = step(face_detection, frame);
		frame_num = frame_num + 1;
	end

	% If no detections are found in the entire video, skip the video
	if isempty(detection)
		error('No suitable faces detected in video %s', vids{i})
		continue;
	end

	% Pick largest detection
	[~, idx] = max(detection(:,3) .* detection(:,4));
	template_detection = detection(idx, :);

	% Detect points to track in initial detection
	points = detectMinEigenFeatures(rgb2gray(frame), 'ROI', template_detection);

	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Use tracking to support face detection in every frame
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Restart video
	V.CurrentTime = 0;
	frame_num = 0;

	% Create point tracker
	tracker = vision.PointTracker('MaxBidirectionalError', 2);

	% Initialize the tracker with the initial points and video frame.
	points = points.Location;
	initialize(tracker, points, frame);

	% Run through movie
	old_points = points;
	bbox_points = bbox2points(template_detection);
	while hasFrame(V)
		
		% Console and log feedback
		out_name = fullfile(output_dir, basename, sprintf('%s_%05d.jpg', basename, frame_num));
		fprintf('Analyzing %s_%05d\n', basename, frame_num);
		fprintf(fid_log, 'Analyzing %s_%05d\n', basename, frame_num);

		% Load frame and compute detection
		frame = readFrame(V);
		detection = step(face_detection, frame);

		% If no detection is found, track one
		if isempty(detection)
			fprintf('Using tracking on frame %d\n', frame_num);
			
			% Track the points from the previous frame in the new frame
			[points, is_found] = step(tracker, frame);
			visible_points = points(is_found, :);
			old_inliers = old_points(is_found, :);

			% If at least 2 points are detected, use them to compute the new
			% bounding box location
			if size(visible_points, 1) >= 2

				% Estimate the geometric transformation between the old points
				% and the new points and eliminate outliers
				[xform, old_inliers, visible_points] = estimateGeometricTransform(...
				old_inliers, visible_points, 'similarity', 'MaxDistance', 4);

				% Apply the transformation to the bounding box points
				bbox_points = transformPointsForward(xform, bbox_points);

				% Convert bounding box format back to crop function style
				% ([xmin, ymin, xmax, ymax])
				detection = points2xyxy(bbox_points);

				% Reset the points
				old_points = visible_points;
				setPoints(tracker, old_points);
			else
				% If we can't find a new detection, skip this frame
				warning('Failed to find enough points...skipping frame number %d', frame_num)
				fprintf(fid_log, 'Failed to find enough points...skipping frame number %d', frame_num);
				continue;
			end		
		else
			% Pick largest largest detection
			[~, idx] = max(detection(:,3) .* detection(:,4));
			detection = detection(idx, :);

			% Update tracked points
			% This is not entirely necessary to do for *every* frame, but it doesn't
			% slow stuff down too much, and it improved our detections, se we just
			% run it on every detection
			points = detectMinEigenFeatures(rgb2gray(frame), 'ROI', detection);
			points = points.Location;
			old_points = points;
			setPoints(tracker, old_points);

			% Convert detection format to match requirement for cropping function	
			detection = tlwh2xyxy(detection);

		end

		% Crop face and write to file	
		crop = lib.face_proc.faceCrop.crop(frame, detection);
		imwrite(crop, out_name);
		frame_num = frame_num + 1; % Increment frame number tracker
	end

	% Log number of frames in the video
	fprintf(fid_frames, '%s %d\n', basename, frame_num);

	% Clean up
	release(tracker);
	frame_num = 0;
end

% Close file handles
fclose(fid_frames);
fclose(fid_log);
