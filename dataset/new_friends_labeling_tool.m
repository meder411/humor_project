function varargout = new_friends_labeling_tool(varargin)
% NEW_FRIENDS_LABELING_TOOL MATLAB code for new_friends_labeling_tool.fig
%      NEW_FRIENDS_LABELING_TOOL, by itself, creates a new NEW_FRIENDS_LABELING_TOOL or raises the existing
%      singleton*.
%
%      H = NEW_FRIENDS_LABELING_TOOL returns the handle to a new NEW_FRIENDS_LABELING_TOOL or the handle to
%      the existing singleton*.
%
%      NEW_FRIENDS_LABELING_TOOL('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in NEW_FRIENDS_LABELING_TOOL.M with the given input arguments.
%
%      NEW_FRIENDS_LABELING_TOOL('Property','Value',...) creates a new NEW_FRIENDS_LABELING_TOOL or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before new_friends_labeling_tool_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to new_friends_labeling_tool_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help new_friends_labeling_tool

% Last Modified by GUIDE v2.5 21-Nov-2016 00:40:46

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @new_friends_labeling_tool_OpeningFcn, ...
                   'gui_OutputFcn',  @new_friends_labeling_tool_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before new_friends_labeling_tool is made visible.
function new_friends_labeling_tool_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to new_friends_labeling_tool (see VARARGIN)

% Choose default command line output for new_friends_labeling_tool
handles.output = hObject;

handles.subs_dropdown.String = getAllFiles('.', 'srt');
handles.scenes_dropdown.String = getAllFiles('.', 'txt');
handles.output = hObject;
handles.sub_scene_pairs = [];
handles.results_out_text = {};
handles.sub_idx = 1;
handles.line_idx = 1;
handles.episode = '';
handles.scene = '';

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes new_friends_labeling_tool wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = new_friends_labeling_tool_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;




function current_sub_Callback(hObject, eventdata, handles)
% hObject    handle to current_sub (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of current_sub as text
%        str2double(get(hObject,'String')) returns contents of current_sub as a double


% --- Executes during object creation, after setting all properties.
function current_sub_CreateFcn(hObject, eventdata, handles)
% hObject    handle to current_sub (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function current_line_Callback(hObject, eventdata, handles)
% hObject    handle to current_line (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of current_line as text
%        str2double(get(hObject,'String')) returns contents of current_line as a double


% --- Executes during object creation, after setting all properties.
function current_line_CreateFcn(hObject, eventdata, handles)
% hObject    handle to current_line (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function remaining_lines_Callback(hObject, eventdata, handles)
% hObject    handle to remaining_lines (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of remaining_lines as text
%        str2double(get(hObject,'String')) returns contents of remaining_lines as a double


% --- Executes during object creation, after setting all properties.
function remaining_lines_CreateFcn(hObject, eventdata, handles)
% hObject    handle to remaining_lines (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function remaining_subs_Callback(hObject, eventdata, handles)
% hObject    handle to remaining_subs (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of remaining_subs as text
%        str2double(get(hObject,'String')) returns contents of remaining_subs as a double


% --- Executes during object creation, after setting all properties.
function remaining_subs_CreateFcn(hObject, eventdata, handles)
% hObject    handle to remaining_subs (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function results_display_Callback(hObject, eventdata, handles)
% hObject    handle to results_display (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of results_display as text
%        str2double(get(hObject,'String')) returns contents of results_display as a double


% --- Executes during object creation, after setting all properties.
function results_display_CreateFcn(hObject, eventdata, handles)
% hObject    handle to results_display (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in next_sub.
function next_sub_Callback(hObject, eventdata, handles)
% hObject    handle to next_sub (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.sub_scene_pairs = [handles.sub_scene_pairs; [handles.sub_idx, handles.line_idx]];
handles.sub_idx = handles.sub_idx + 1;
handles.results_out_text = {sprintf('Sub %d --> Line %d', handles.sub_idx-1, handles.line_idx), handles.results_out_text{:}};
set(handles.results_display, 'string', handles.results_out_text)
update_sub_display(hObject, handles)

% --- Executes on button press in next_line.
function next_line_Callback(hObject, eventdata, handles)
% hObject    handle to next_line (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.line_idx = handles.line_idx + 1;
update_scene_display(hObject, handles)

function update_sub_display(hObject, handles)
start = (handles.sub_idx - 1) * 3 + 1;
finish = (handles.sub_idx) * 3;
if finish < length(handles.subs)
    set(handles.remaining_subs, 'string', handles.subs(finish+1:end))
    set(handles.current_sub, 'string', handles.subs(start:finish))
end
guidata(hObject, handles)

function update_scene_display(hObject, handles)
if handles.line_idx < length(handles.lines)
    set(handles.remaining_lines, 'string', handles.lines(handles.line_idx+1:end))
    set(handles.current_line, 'string', handles.lines(handles.line_idx))
end
guidata(hObject, handles)



% --- Executes on button press in save.
function save_Callback(hObject, eventdata, handles)
% hObject    handle to save (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
matches = handles.sub_scene_pairs;
fid = fopen([handles.episode, '_', handles.scene, '.txt'], 'w');
fprintf(fid, 'SUB LINE\n', matches);
fprintf(fid, '%d %d\n', matches);
fclose(fid);

% --- Executes on selection change in scenes_dropdown.
function scenes_dropdown_Callback(hObject, eventdata, handles)
% hObject    handle to scenes_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns scenes_dropdown contents as cell array
%        contents{get(hObject,'Value')} returns selected item from scenes_dropdown

% --- Executes during object creation, after setting all properties.
function scenes_dropdown_CreateFcn(hObject, eventdata, handles)
% hObject    handle to scenes_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in load_scene.
function load_scene_Callback(hObject, eventdata, handles)
% hObject    handle to load_scene (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Reset variables
handles.sub_scene_pairs = [];
handles.line_idx = 1;
handles.results_out_text = {};

% Load subtitles
[~, name, ~] = fileparts(handles.scenes_dropdown.String{get(handles.scenes_dropdown, 'Value')});
handles.scene = name;
handles.lines = readScenes(handles.scenes_dropdown.String{get(handles.scenes_dropdown, 'Value')});

% Update displays
set(handles.results_display, 'string', handles.results_out_text)
set(handles.remaining_lines, 'string', handles.lines(2:end))
set(handles.current_line, 'string', handles.lines(1))
set(handles.next_line, 'Enable', 'on')
set(handles.back, 'Enable', 'on')
guidata(hObject, handles)


function lines = readScenes(path)
lines = {};
line_idx = 1;
fid = fopen(path);
tline = fgetl(fid);
while ischar(tline)
    lines{line_idx} = tline;
    line_idx = line_idx + 1;
    tline = fgetl(fid);
end
fclose(fid);


% --- Executes on selection change in subs_dropdown.
function subs_dropdown_Callback(hObject, eventdata, handles)
% hObject    handle to subs_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns subs_dropdown contents as cell array
%        contents{get(hObject,'Value')} returns selected item from subs_dropdown


% --- Executes during object creation, after setting all properties.
function subs_dropdown_CreateFcn(hObject, eventdata, handles)
% hObject    handle to subs_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in load_subs.
function load_subs_Callback(hObject, eventdata, handles)
% hObject    handle to load_subs (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if ~isempty(handles.episode)
    save_Callback(hObject, eventdata, handles)
end

% Reset variables
handles.sub_scene_pairs = [];
handles.sub_idx = 1;

% Load subtitles
[~, name, ~] = fileparts(handles.subs_dropdown.String{get(handles.subs_dropdown, 'Value')});
handles.episode = name;
handles.subs = readSRT(handles.subs_dropdown.String{get(handles.subs_dropdown, 'Value')});

% Update displays
set(handles.remaining_subs, 'string', handles.subs(4:end))
set(handles.current_sub, 'string', handles.subs(1:3))
set(handles.next_sub, 'Enable', 'on')
set(handles.undo, 'Enable', 'on')
set(handles.next_sub, 'Enable', 'on')
set(handles.skip_sub, 'Enable', 'on')
set(handles.undo, 'Enable', 'on')
guidata(hObject, handles)


function subs = readSRT(path)
subs = {};
sub_idx = 1;
fid = fopen(path);
tline = fgetl(fid);
sub = {};
line_idx = 1;
while ischar(tline)
    if ~isempty(tline)
        sub{line_idx} = tline;
        line_idx = line_idx + 1;
    else
        subs = {subs{:}, sub{:}};
        sub = {};
        line_idx = 1;
        sub_idx = sub_idx + 1;
    end
    tline = fgetl(fid);
end
fclose(fid);


% --- Executes on button press in skip_sub.
function skip_sub_Callback(hObject, eventdata, handles)
% hObject    handle to skip_sub (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if handles.sub_idx < length(handles.subs)
    handles.sub_idx = handles.sub_idx + 1;
    update_sub_display(hObject, handles)
end

% --- Executes on key release with focus on figure1 and none of its controls.
function figure1_KeyReleaseFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  structure with the following fields (see MATLAB.UI.FIGURE)
%	Key: name of the key that was released, in lower case
%	Character: character interpretation of the key(s) that was released
%	Modifier: name(s) of the modifier key(s) (i.e., control, shift) released
% handles    structure with handles and user data (see GUIDATA)
if eventdata.Key == 's'
    skip_sub_Callback(hObject, [], handles)
elseif strcmp(eventdata.Key, 'leftarrow')
    undo_Callback(hObject, [], handles)
elseif eventdata.Key == 'b'
    back_Callback(hObject, [], handles)
elseif strcmp(eventdata.Key, 'space')
    next_line_Callback(hObject, [], handles)
elseif strcmp(eventdata.Key, 'rightarrow')
    next_sub_Callback(hObject, [], handles)
end


% --- Executes on button press in undo.
function undo_Callback(hObject, eventdata, handles)
% hObject    handle to undo (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if handles.sub_idx > 1
    handles.sub_scene_pairs = handles.sub_scene_pairs(1:end-1, :);
    handles.sub_idx = handles.sub_idx - 1;
    handles.results_out_text = handles.results_out_text(2:end);
    set(handles.results_display, 'string', handles.results_out_text)
    update_sub_display(hObject, handles)
end


% --- Executes on button press in back.
function back_Callback(hObject, eventdata, handles)
% hObject    handle to back (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if handles.line_idx > 1
    handles.line_idx = handles.line_idx - 1;
    update_scene_display(hObject, handles)
end
