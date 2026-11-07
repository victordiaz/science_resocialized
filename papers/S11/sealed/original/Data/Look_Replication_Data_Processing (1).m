%
% Script for Pre-processing eyetracker data for exact replication of "Where
% Do We Look During Potentially Offensive Behavior?".
%
% Written by: Bob Bramson (RA), for Kai Jonas
% Social Psychology Department, University of Amsterdam
% Date finished: 2-1-2015
%

clear all;
close all;

cd 'C:\Users\Bob\Desktop\Data files where do we look'; % When running from another pc, type file directory here

FileList = dir('pp*');
LookTimeP1 = zeros(length(FileList),1); %prespecify for speed
LookTimeP2 = zeros(length(FileList),1);
LookTimeP3 = zeros(length(FileList),1);
LookTimeP4 = zeros(length(FileList),1);
PPNR = zeros(length(FileList),1);

for subno=1:length(FileList)
       
    %Load in data file
    FileName = FileList(subno).name;
    fileID = fopen(FileName);
    Totaldata = textscan(fileID,'%s %s %s %s %s %s %s %s %s');
    fclose(fileID);
    PPNR(subno)= str2double(FileName(3:4));
    number = str2double(FileName(3:4));
    
    % Select x and y data total movie clip
    x = Totaldata{1,3}; x = str2double(x(2:6421));
    y = Totaldata{1,4}; y = str2double(y(2:6421));
    
    % Select x and y data from second speaker
    xInsult = x(5100:end); 
    yInsult = y(5100:end); 
    
    % Looking time at target
    LookTimeP1(subno)= numel(find((xInsult > 210) & (xInsult < 830)  & (yInsult < 513)  & (yInsult > 0)==1));
    LookTimeP2(subno)= numel(find((xInsult > 848) & (xInsult < 1469) & (yInsult < 513)  & (yInsult > 0)==1));
    LookTimeP3(subno)= numel(find((xInsult > 210) & (xInsult < 830)  & (yInsult < 1050) & (yInsult > 535)==1));
    LookTimeP4(subno)= numel(find((xInsult > 848) & (xInsult < 1469) & (yInsult < 1050) & (yInsult > 535)==1));

end

%Convert look times to ms (sample rate = 60HZ)
LookTimeP1 = round(LookTimeP1 * (1000/60));
LookTimeP2 = round(LookTimeP2 * (1000/60));
LookTimeP3 = round(LookTimeP3 * (1000/60));
LookTimeP4 = round(LookTimeP4 * (1000/60));

%Compute data matrix
Overview = [PPNR LookTimeP1 LookTimeP2 LookTimeP3 LookTimeP4];

