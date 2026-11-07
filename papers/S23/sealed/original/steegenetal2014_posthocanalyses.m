% This code is code for the post-hoc analyses.
% Before running this code, first run steegenetal2014_confirmatoryanalyses.m.

% Steegen, S., Dewitte, L., Tuerlinckx, F., & Vanpaemel, W. (2014). Measuring the crowd within again: A pre-registered replication study. Frontiers in Psychology


%% comparison of magnitude of averaging benefit over guess 2 between immediate and delayed condtion. 

grp(2).mudiff{2};
grp(2).sddiff{2};
grp(1).mudiff{2};
grp(1).sddiff{2}; 
% ttest
[h p ci stats] = ttest2(grp(2).d{2} - grp(2).d{3}, grp(1).d{2} - grp(1).d{3});
grpcmp.t{2} = stats.tstat;
grpcmp.df{2} = stats.df;
grpcmp.p{2} = p;
% effect size (cohen's standardized mean difference d for independent groups)
grpcmp.d{2} = grpcmp.t{2}.*sqrt((1/grp(1).n)+(1/grp(2).n));
% confidence interval
df = grpcmp.df{2};
tnonct = inline('nctcdf(x,df,delta) - pr');
ncp_low = fzero(@(delta) tnonct(delta, df, 1-alpha/2, grpcmp.t{2}), [-20,20]);
ncp_high = fzero(@(delta) tnonct(delta, df, alpha/2, grpcmp.t{2}), [-20,20]);
grpcmp.dlow{2} = ncp_low.*sqrt((1/grp(1).n)+(1/grp(2).n));
grpcmp.dhigh{2} = ncp_high.*sqrt((1/grp(1).n)+(1/grp(2).n));