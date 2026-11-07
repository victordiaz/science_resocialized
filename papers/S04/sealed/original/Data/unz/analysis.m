%% get data
clear('data');
s = [];
Nsubject = 15;

for i = 1:Nsubject
    load(sprintf('subject%02d.mat', i));
    idx = find(strcmpi(data.triplet_type,'real') == 1);
    s(i) = mean(data.correct(idx));
    clear('data');
end

%% analysis
fprintf('All participants\n--------------------\n');
fprintf('Mean recall rate: %f (std.dev.: %f)\n', mean(s), std(s));
fprintf('t-test:\n');
[h, p, ci, stat] = ttest(s,repmat(0.5,1,length(s)));
h
p
ci
stat

fprintf('Effect size: %f\n', ((mean(s)-0.5)/std(s)));

%% analysis w/o explicit learners
s2 = s;
exclude = [3 5];
%exclude = [1 3 4 5 10];
s2(exclude) = [];

fprintf('\nExcluding explicit learners\n-----------------------------\n');
fprintf('Mean recall rate: %f (std.dev.: %f)\n', mean(s2), std(s2));
fprintf('t-test:\n');
[h2, p2, ci2, stat2] = ttest(s2,repmat(0.5,1,length(s2)));
h2
p2
ci2
stat2

fprintf('Effect size: %f\n', ((mean(s2)-0.5)/std(s2)));