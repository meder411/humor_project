function varargout = friends_labeling_tool(varargin)
% FRIENDS_LABELING_TOOL MATLAB code for friends_labeling_tool.fig
%      FRIENDS_LABELING_TOOL, by itself, creates a new FRIENDS_LABELING_TOOL or raises the existing
%      singleton*.
%
%      H = FRIENDS_LABELING_TOOL returns the handle to a new FRIENDS_LABELING_TOOL or the handle to
%      the existing singleton*.
%
%      FRIENDS_LABELING_TOOL('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in FRIENDS_LABELING_TOOL.M with the given input arguments.
%
%      FRIENDS_LABELING_TOOL('Property','Value',...) creates a new FRIENDS_LABELING_TOOL or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before friends_labeling_tool_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are pased to friends_labeling_tool_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help friends_labeling_tool

% Last Modified by GUIDE v2.5 20-Nov-2016 18:03:59

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @friends_labeling_tool_OpeningFcn, ...
                   'gui_OutputFcn',  @friends_labeling_tool_OutputFcn, ...
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





% --- Executes just before friends_labeling_tool is made visible.
function friends_labeling_tool_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to friends_labeling_tool (see VARARGIN)

% Choose default command line output for friends_labeling_tool
handles.input_dir = fullfile('subtitles', 'edited', 'season1');
handles.output_dir = '.';
files = dir(fullfile(handles.input_dir, '*.srt'));
files = {files(:).name};
handles.file_dropdown.String = files;
handles.output = hObject;
handles.speakers = {};
handles.srt_idx = 1;
handles.scene_breaks = [];
handles.episode = '';
handles.subs = {};
handles.sub_output_text = {};




% Update handles structure
guidata(hObject, handles);

% UIWAIT makes friends_labeling_tool wait for user response (see UIRESUME)
% uiwait(handles.figure1);



% --- Outputs from this function are returned to the command line.
function varargout = friends_labeling_tool_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button pres in ross.
function ross_Callback(hObject, eventdata, handles)
% hObject    handle to ross (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = addToSpeakerList(handles, 'Ross');
guidata(hObject, handles)

% --- Executes on button pres in rachel.
function rachel_Callback(hObject, eventdata, handles)
% hObject    handle to rachel (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = addToSpeakerList(handles, 'Rachel');
guidata(hObject, handles)

% --- Executes on button pres in monica.
function monica_Callback(hObject, eventdata, handles)
% hObject    handle to monica (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = addToSpeakerList(handles, 'Monica');
guidata(hObject, handles)

% --- Executes on button pres in chandler.
function chandler_Callback(hObject, eventdata, handles)
% hObject    handle to chandler (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = addToSpeakerList(handles, 'Chandler');
guidata(hObject, handles)

% --- Executes on button pres in joey.
function joey_Callback(hObject, eventdata, handles)
% hObject    handle to joey (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = addToSpeakerList(handles, 'Joey');
guidata(hObject, handles)

% --- Executes on button pres in phoebe.
function phoebe_Callback(hObject, eventdata, handles)
% hObject    handle to phoebe (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = addToSpeakerList(handles, 'Phoebe');
guidata(hObject, handles)

% --- Executes on button pres in other_asign.
function other_assign_Callback(hObject, eventdata, handles)
% hObject    handle to other_asign (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Use the text box if it's set, otherwise use the dropdown
other_text = get(handles.other_textbox, 'String');
if isempty(other_text)
    if isempty(handles.other_dropdown.String)
        return
    else
        other_text = handles.other_dropdown.String{get(handles.other_dropdown, 'Value')};
    end
end
if isempty(other_text)
    return
end
% Add to dropdown if not already there
if ~any(strcmp(handles.other_dropdown.String, other_text))
%     handles.other_dropdown.String{length(handles.other_dropdown.String)+1} = other_text;
    handles.other_dropdown.String = {other_text, handles.other_dropdown.String{:}};
    handles.other_dropdown.Value = 1;
end
handles.other_textbox.String = ''; % Reset text box

% Update speaker list
handles = addToSpeakerList(handles, other_text);
guidata(hObject, handles)

function h = addToSpeakerList(h, name)
h.speakers{h.srt_idx} = name;
out_txt = {h.subs{h.srt_idx}{1}, h.subs{h.srt_idx}{2}, sprintf('%s: %s', name, h.subs{h.srt_idx}{3})};
h.sub_output_text = {out_txt{:}, h.sub_output_text{:}};
h.srt_idx = h.srt_idx + 1;
set(h.sub_display, 'string', h.subs{h.srt_idx})
set(h.sub_output, 'string', h.sub_output_text)


function other_textbox_Callback(hObject, eventdata, handles)
% hObject    handle to other_textbox (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of other_textbox as text
%        str2double(get(hObject,'String')) returns contents of other_textbox as a double


% --- Executes during object creation, after setting all properties.
function other_textbox_CreateFcn(hObject, eventdata, handles)
% hObject    handle to other_textbox (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button pres in end_scene.
function end_scene_Callback(hObject, eventdata, handles)
% hObject    handle to end_scene (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if ~ismember(handles.srt_idx-1, handles.scene_breaks)
    if ~isempty(handles.scene_breaks)
        handles.scene_breaks(end+1) = handles.srt_idx-1;
    else
        handles.scene_breaks = handles.srt_idx-1;
    end
end
out_txt = sprintf('%d,',handles.scene_breaks);
set(handles.scene_output, 'string', out_txt(1:end-1))
guidata(hObject, handles)

% --- Executes on button pres in skip.
function skip_Callback(hObject, eventdata, handles)
% hObject    handle to skip (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = addToSpeakerList(handles, '');
guidata(hObject, handles)

% --- Executes on selection change in other_dropdown.
function other_dropdown_Callback(hObject, eventdata, handles)
% hObject    handle to other_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns other_dropdown contents as cell array
%        contents{get(hObject,'Value')} returns selected item from other_dropdown


% --- Executes during object creation, after setting all properties.
function other_dropdown_CreateFcn(hObject, eventdata, handles)
% hObject    handle to other_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



% --- Executes on button pres in save_button.
function save_button_Callback(hObject, eventdata, handles)
% hObject    handle to save_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
speakers = handles.speakers;
scene_breaks = handles.scene_breaks;
save(fullfile(handles.output_dir, [handles.episode, '.mat']), 'speakers', 'scene_breaks')


% --- Executes on selection change in file_dropdown.
function file_dropdown_Callback(hObject, eventdata, handles)
% hObject    handle to file_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns file_dropdown contents as cell array
%        contents{get(hObject,'Value')} returns selected item from file_dropdown


% --- Executes during object creation, after setting all properties.
function file_dropdown_CreateFcn(hObject, eventdata, handles)
% hObject    handle to file_dropdown (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button pres in load_button.
function load_button_Callback(hObject, eventdata, handles)
% hObject    handle to load_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if ~isempty(handles.episode)
    save_button_Callback(hObject, eventdata, handles)
end
handles.speakers = {};
handles.srt_idx = 1;
handles.scene_breaks = [];
handles.other_dropdown.String = {''};
handles.sub_output_text = {};
[~, name, ~] = fileparts(handles.file_dropdown.String{get(handles.file_dropdown, 'Value')});
handles.episode = name;
handles.subs = readSRT(fullfile(handles.input_dir, handles.file_dropdown.String{get(handles.file_dropdown, 'Value')}));
set(handles.sub_display, 'string', handles.subs{handles.srt_idx})
set(handles.scene_output, 'string', {})
set(handles.sub_output, 'string', {})

guidata(hObject, handles)

set(handles.ross, 'Enable', 'on')
set(handles.rachel, 'Enable', 'on')
set(handles.monica, 'Enable', 'on')
set(handles.chandler, 'Enable', 'on')
set(handles.joey, 'Enable', 'on')
set(handles.phoebe, 'Enable', 'on')
set(handles.skip, 'Enable', 'on')
set(handles.other_dropdown, 'Enable', 'on')
set(handles.other_textbox, 'Enable', 'on')
set(handles.other_assign, 'Enable', 'on')
set(handles.end_scene, 'Enable', 'on')
set(handles.save_button, 'Enable', 'on')
set(handles.back, 'Enable', 'on')
set(handles.remove_scene, 'Enable', 'on')



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
        subs{sub_idx} = sub;
        sub = {};
        line_idx = 1;
        sub_idx = sub_idx + 1;
    end
    tline = fgetl(fid);
end
fclose(fid);


% --- Executes on key release with focus on figure1 and none of its controls.
function figure1_KeyReleaseFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  structure with the following fields (see MATLAB.UI.FIGURE)
%	Key: name of the key that was released, in lower case
%	Character: character interpretation of the key(s) that was released
%	Modifier: name(s) of the modifier key(s) (i.e., control, shift) released
% handles    structure with handles and user data (see GUIDATA)
if eventdata.Key == 'r'
    ross_Callback(hObject, [], handles)
elseif eventdata.Key == 'a'
    rachel_Callback(hObject, [], handles)
elseif eventdata.Key == 'm'
    monica_Callback(hObject, [], handles)
elseif eventdata.Key == 'c'
    chandler_Callback(hObject, [], handles)
elseif eventdata.Key == 'j'
    joey_Callback(hObject, [], handles)
elseif eventdata.Key == 'p'
    phoebe_Callback(hObject, [], handles)
elseif eventdata.Key == 'o'
    other_assign_Callback(hObject, [], handles)
elseif eventdata.Key == 'e'
    end_scene_Callback(hObject, [], handles)
elseif eventdata.Key == 's'
    skip_Callback(hObject, [], handles)
elseif eventdata.Key == 'b'
    back_Callback(hObject, [], handles)
elseif eventdata.Key == 'u'
    remove_scene_Callback(hObject, [], handles)
end


% --- Executes on button press in back.
function back_Callback(hObject, eventdata, handles)
% hObject    handle to back (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if handles.srt_idx > 1
    handles.srt_idx = handles.srt_idx - 1;
    set(handles.sub_display, 'string', handles.subs{handles.srt_idx})
    handles.sub_output_text = handles.sub_output_text(4:end);
    set(handles.sub_output, 'string', handles.sub_output_text)
    guidata(hObject, handles)
end


% --- Executes on button press in remove_scene.
function remove_scene_Callback(hObject, eventdata, handles)
% hObject    handle to remove_scene (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if ~isempty(handles.scene_breaks)
    handles.scene_breaks = handles.scene_breaks(1:end-1);
    out_txt = sprintf('%d,',handles.scene_breaks);
    set(handles.scene_output, 'string', out_txt(1:end-1))
    guidata(hObject, handles)
end



function sub_output_Callback(hObject, eventdata, handles)
% hObject    handle to sub_output (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of sub_output as text
%        str2double(get(hObject,'String')) returns contents of sub_output as a double


% --- Executes during object creation, after setting all properties.
function sub_output_CreateFcn(hObject, eventdata, handles)
% hObject    handle to sub_output (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function scene_output_Callback(hObject, eventdata, handles)
% hObject    handle to scene_output (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of scene_output as text
%        str2double(get(hObject,'String')) returns contents of scene_output as a double


% --- Executes during object creation, after setting all properties.
function scene_output_CreateFcn(hObject, eventdata, handles)
% hObject    handle to scene_output (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
