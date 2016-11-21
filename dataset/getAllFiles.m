function fileList = getAllFiles(dirName, suffix)
% % % % % 
% A function that returns the path to all of the files in <dirName> and its subdirectories.
%
% INPUTS
% dirName    :  parent directory of interest (string)
% suffix     :  filetype suffix WITHOUT leading period (string)
%
% OUTPUT
% fileList   :  M x 1 cell array of filepaths, where M is the number of files returned
% % % % %

    % Get the data for the current directory
    dirData = dir(dirName);
    
    % Find the index for directories  
    dirIndex = [dirData.isdir];
  
    % Get a list of the <suffix> files in current directory
    if nargin < 2
        files = dir(dirName);
    else
        files = dir([dirName, '\*.', suffix]);
    end
    
    % Initialize empty list to hold all filenames
    fileList = [];
  
    % Pulls file information from struct
    if ~isempty(files)
        % Extracts filenames from dir struct
        fileList = extractfield(files, 'name')';
    
        % Prepend path to files
        fileList = cellfun(@(x) fullfile(dirName,x), fileList,'UniformOutput',false);
    end
    
    % Get a list of the subdirectories
    subDirs = {dirData(dirIndex).name};
    
    % Find index of subdirectories that are not '.' or '..'
    validIndex = ~ismember(subDirs,{'.','..'});
  
    % Loop over valid subdirectories
    for iDir = find(validIndex)
        % Get the subdirectory path
        nextDir = fullfile(dirName,subDirs{iDir});
        
        % Recursively call getAllFiles
        if nargin < 2
            fileList = [fileList; getAllFiles(nextDir)];
        else
            fileList = [fileList; getAllFiles(nextDir, suffix)];
        end
    end
end