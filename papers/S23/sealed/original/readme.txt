This is the code for Steegen, S., Dewitte, L., Tuerlinckx, F., & Vanpaemel, W. (2014).  Measuring the crowd within again: A pre-registered replication study. Frontiers in Psychology.

steegenetal2014_confirmatoryanalyses.m contains the code for the confirmatory analyes.

steegenetal2014_posthocanalyses.m contains the code for the post hoc analyes. To run the post hoc analyses, run the confirmatory analyses first.

steegenetal2014_confirmatoryanalyses.m uses the postprocessed data, contained in data_steegenetal2014.mat. This mat files is made from the raw data contained in rawdata_immediate.txt, rawdata_delayed_session1.txt and rawdata_delayed_session2.txt, using steegenetal2014_postprocessing.m


The code crowdwithin_analysis.m was the pre-registered code for the confirmatory analyses. 
However, we used steegenetal2014_confirmatoryanalyses.m instead, which extends the code in crowdwithin_analysis.m (i.e., it contains additional code for the calculation of some descriptive statistics, plots, effect sizes, and confidence intervals). 