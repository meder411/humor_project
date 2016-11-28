
plot_sig = 0; % Whether to plot the signal and peaks
peak_radius = 6;  % Number of seconds between laughs
sampling_rate = 100; % How much to downsample the signal by
peak_upper_bound = 0.3; % Upper bound on normalized peak amplitude

% Get files in directory
files = dir('../audio/*.wav');
files = {files(:).name};

% Open output file
fid = fopen('laugh_times.txt', 'w');

for i = 1 : length(files)

    % Read the file
    [y, fs] = audioread(fullfile('..', 'audio', files{i}));
    t = 1/fs : 1/fs : length(y)/fs;
    
    % Resample the audio
    yds = resample(y, 1, sampling_rate);
    tds = t(1:sampling_rate:end)';
    yds = yds / max(yds);
    yds_thresh = yds;
    yds_thresh(yds<0) = 0;
    
    % Update statistics of the signal
    sigma = std(yds_thresh);
    fs = fs / sampling_rate;
    
    % Get signal envelope
    env = envelope(yds_thresh, 500, 'peaks');
    [pks, loc] = findpeaks(env, 'MinPeakDistance', peak_radius*fs, 'MinPeakHeight', 2*sigma);
    loc = loc(pks < peak_upper_bound);
    pks = pks(pks < peak_upper_bound);
    length(pks)
    
    % Plot the signal
    if plot_sig
        figure
        plot(tds, yds_thresh); % Plots downsampled signal
        hold on
        plot(tds, env); % Plots envelope of downsampled signal
        scatter(tds(loc), pks); % Plots the peaks
        title(files{i})
        ylabel('Normalized Signal')
        xlabel('Seconds')
    end

    % Write the laugh times to file
    fprintf(fid, '%s %d ', files{i}(1:5), tds(loc));
    fprintf(fid, '\n');
    

end

% Close output file
fclose(fid);
