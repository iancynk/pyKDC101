%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATLAB commands to control the PRM1-Z8 rotation stage through the KDC101
% controller over serial.
% These are just some selected commands to show the communication structure
% scripted by ian cynk (ian.cynk@posteo.eu) in 2019
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The address '01' is the host (usually the computer)
% The address '50' refers to generic USB device
% When using commands with parameters, '50' needs to be OR'd with '80'
% leading to 'D0'
% While we create the commands in hex, they are converted to integers and sent
% in binary format by fsend
% "Long" commands (>6 byte) including parameters MUST be transmitted as 'uint8'!
%
% The position parameter structure is "weird":
% You have 4 Bytes to encode a number of increments, e.g. "64 00 10 00"
% To get the number, you have to flip the byte sequence and then convert it:
% 00 10 00 64 = 0000 0000  0001 0000  0000 0000  0110 0100 =
% 2^20 + 2^6 + 2^5 + 2^2 = 1048676
% Divide this by EncCnt yields rotation in degree: 1048676/1920 = 546 degree
%
% Hence to calculate the needed parameter, you take your angle, multiply it with
% the EncCnt per deg, convert it to binary (filling up to 4 bytes). Then you
% flip the sequence of the four bytes.
%
% If you are not familiar with serial: you need to add a delay between sending
% a command and receiving data (e.g. 50 ms)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% about the PRM1-Z8: (from Communication Protocol pdf)
% EncCnt per deg: 1919.6418578623391
% Scaling Factor
%   Velocity 42941.66 (deg/s)
%   Acceleration 14.66 (deg/s^2)
% POS = EncCnt x Pos
% VEL = EncCnt x T x 65536 x Vel
%   VEL (PRM1-Z8) = 6.2942e4 x Vel
% ACC = EncCnt x T^2 x 65536 x Acc
%   ACC (PRM1-Z8) = 14.6574 x Acc
% where T = 2048/6e6 (KDC101)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% setup connection
if ~isempty(instrfind)
    % clear all previous connections
    a = instrfind;
    fclose(a(:));
    delete(a(:));
    clear a
end

s = serial('/dev/ttyUSB0');
fopen(s);
s.BaudRate = 115200;
s.DataBits = 8;
s.StopBits = 1;
s.Parity = 'none';
s.FlowControl = 'hardware';
s.Terminator = '';
s.Timeout = 5;

pause(0.1)

%% flash display
str = '23 02 00 00 50 01'; % to identify stage
% structure:
% 23 02 = command (here: instruct hardware to identify by flashing front panel LEDs)
% 00 00 = param1 and param2 (here zero)
% 50 = dest (here: generic USB unit)
% 01 = source (here: simply means host)
command = sscanf(str, '%2X'); % convert string to hex sequence
disp(['command to stage: ', str])
fwrite(s, command, 'int8')


%% hardware info
str = '05 00 00 00 50 01'; % request hardware info
command = sscanf(str, '%2X'); % convert string to hex sequence
disp(['command to stage: ', str])
fwrite(s, command, 'int8')
pause(0.1)
s.BytesAvailable;
hwinfo = fscanf(s);
% header = fscanf(s, '%c', 6);
% message = fscanf(s, '%c', 84);

%% move home
str = '43 04 01 00 50 01';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'int8')

% prints that it reached home ('44 04 01 00 01 50')
homedmessage = fread(s);
disp(dec2hex(homedmessage))

%% get velocity parameters
str = '14 04 01 00 50 01';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'int8')

% prints that it reached home ('44 04 01 00 01 50')
velparams = fread(s);
disp(dec2hex(velparams))
minvel = velparams(9:12);
acc = velparams(13:16);
maxvel = velparams(17:20);

%% get position counter
str = '11 04 01 00 50 01';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'int8')

poscount = fread(s);

%% get relative movement parameter
str = '46 04 01 00 50 01';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'int8')

% show the parameter
relmove = fread(s);
% disp(dec2hex(relmove(1:6))) % this just is the reply header
% disp(dec2hex(relmove(7:8))) % this is the channel
disp(dec2hex(relmove(9:end))) % this is the preset

%% set rel movement parameter
% the parameter is the last four bytes, inverted somewhat
str = '45 04 06 00 D0 01 01 00 00 0D 03 00';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'uint8')

%% move relative by predefined parameter
str = '48 04 01 00 50 01';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'int8')


%% move relative, setting the parameter
str = '48 04 06 00 D0 01 01 00 20 4E 00 00';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'uint8')


%% get absolute movement parameter
str = '51 04 01 00 50 01';
command = sscanf(str, '%2X'); % convert string to hex sequence
disp(['command to stage: ', str])
fwrite(s, command, 'int8')

% show the parameter
absmove = fread(s);
% disp(dec2hex(absmove(1:6))) % this just is the reply header
% disp(dec2hex(absmove(7:8))) % this is the channel
disp(dec2hex(absmove(9:end))) % this is the preset

%% set absolute movement parameter
str = '50 04 06 00 50 01 01 00 00 01 11 00';
command = sscanf(str, '%2X'); % convert string to hex sequence
disp(['command to stage: ', str])
fwrite(s, command, 'uint8')

%% move absolute by predefined parameter
str = '53 04 01 00 50 01';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'int8')

%% move absolute
str = '53 04 06 00 D0 01 01 00 00 70 00 00';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'uint8')


%% stop
str = '65 04 01 00 50 01';
command = sscanf(str, '%2X');
disp(['command to stage: ', str])
fwrite(s, command, 'uint8')

stopped = fread(s);

%%
fclose(s);
delete(s)
