% This is the code used to postprocess the data.  
% It takes rawdata_immediate.txt, rawdata_delayed_session1.txt and 
% rawdata_delayed_session2.txt as input and produces 
% data_steegenetal2014.mat

% Steegen, S., Dewitte, L., Tuerlinckx, F., & Vanpaemel, W. (2014). Measuring the crowd within again: A pre-registered replication study. Frontiers in Psychology

clear

%% immediate condition

% DATA READING

fileID = fopen('rawdata_immediate.txt');  
alldata_imm_header = textscan(fileID, '%s', 54);
format = ['%s %s %f %s %s' repmat('%f ', [1 48]) '%s'];
alldata_imm = textscan(fileID, format, 'CollectOutput', 1);
id = (1:size(alldata_imm{1},1))';

data{1} = [id alldata_imm{4}(:,1) alldata_imm{4}(:,4) alldata_imm{4}(:,7) alldata_imm{4}(:,10) alldata_imm{4}(:,13) alldata_imm{4}(:,16) alldata_imm{4}(:,19) alldata_imm{4}(:,22) alldata_imm{4}(:,25) alldata_imm{4}(:,28) alldata_imm{4}(:,31) alldata_imm{4}(:,34) alldata_imm{4}(:,37) alldata_imm{4}(:,40) alldata_imm{4}(:,43) alldata_imm{4}(:,46)];
data_cheated = alldata_imm{5}; 

% delete everyone who did not complete the experiment.
% the informed consent was signed on paper
data_cheated = data_cheated(all(~isnan(data{1}),2),:); 
data{1} = data{1}(all(~isnan(data{1}),2),:); 

% DATA CLEANING

% delete everyone who defocused the browser window.
% due to a technical problem, the digital assessment of whether 
% participants had defocused the browser window was not reliable in the 
% immediate condition, so we could not execute this part of the data
% cleaning plan

% delete everyone who admitted having looked up the answers 
[delete_cheat] = find(strcmp(data_cheated,'Ja')==1);
data{1}(delete_cheat,:) = [];  

data{1} = data{1}(:,2:17);


%% delayed condition

% DATA READING

% session 1

fileID = fopen('rawdata_delayed_session1.txt');
alldata_del1_header = textscan(fileID, '%s', 32);
format = ['%s %s %f %s %s %s %s %f' repmat('%f', [1 24])];
alldata_del1 = textscan(fileID, format, 'CollectOutput', 1);

data_del_1 = [alldata_del1{4}(:,1) alldata_del1{4}(:,3) alldata_del1{4}(:,6) alldata_del1{4}(:,9) alldata_del1{4}(:,12) alldata_del1{4}(:,15) alldata_del1{4}(:,18) alldata_del1{4}(:,21) alldata_del1{4}(:,24) alldata_del1{4}(:,2) alldata_del1{4}(:,5) alldata_del1{4}(:,8) alldata_del1{4}(:,11) alldata_del1{4}(:,14) alldata_del1{4}(:,17) alldata_del1{4}(:,20) alldata_del1{4}(:,23)];

% delete everyone who did not complete the experiment
data_del_1 = data_del_1(all(~isnan(data_del_1),2),:); 

% session 2

fileID = fopen('rawdata_delayed_session2.txt');
alldata_del2_header = textscan(fileID, '%s', 29);
format = ['%s %s %s %f' repmat('%f', [1 24]) '%s'];
alldata_del2 = textscan(fileID, format, 'CollectOutput', 1);

data_del_2 = [alldata_del2{2}(:,1) alldata_del2{2}(:,3) alldata_del2{2}(:,6) alldata_del2{2}(:,9) alldata_del2{2}(:,12) alldata_del2{2}(:,15) alldata_del2{2}(:,18) alldata_del2{2}(:,21) alldata_del2{2}(:,24) alldata_del2{2}(:,2) alldata_del2{2}(:,5) alldata_del2{2}(:,8) alldata_del2{2}(:,11) alldata_del2{2}(:,14) alldata_del2{2}(:,17) alldata_del2{2}(:,20) alldata_del2{2}(:,23)];

% delete everyone who did not complete the experiment
data_del_2 = data_del_2(all(~isnan(data_del_2),2),:);

% DATA MATCHING

[match1,match2] = ismember(data_del_1(:,1),data_del_2(:,1));
data_del_1 = data_del_1(match1,:);
data_del_2 = data_del_2(match2(match2~=0),:);
data_merge = [data_del_1 data_del_2];

% DATA CLEANING

% delete everyone who defocused
data_merge = data_merge(~any(data_merge(:,[2:9 19:26])==1,2),:);  

% delete everyone who admitted having looked up the answers 
cheaters = find(strcmp(alldata_del2{3},'Ja')==1);
id_cheaters = alldata_del2{2}(cheaters,1);
data_merge(find(ismember(data_merge(:,1),id_cheaters)),:)=[];
data_merge_final = data_merge(:,[10:17 27:34]);

data{2} = data_merge_final;

% save('data_steegenetal2014', 'data')