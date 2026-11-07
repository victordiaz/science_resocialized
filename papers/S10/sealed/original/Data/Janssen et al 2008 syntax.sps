

**Open master data file


GET
  FILE='/Users/amelinger/Dropbox/My stuff/Experiments/RP-P/Data/alldata.sav'.
DATASET NAME DataSet4 WINDOW=FRONT.

** exclude error trials

DATASET ACTIVATE DataSet3.
USE ALL.
COMPUTE filter_$=(Errors = 0).
VARIABLE LABELS filter_$ 'Errors = 0 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

** identify outliers**

compute outlier=0.
execute.

if subject = "01"	& RT > 	317.7226	AND RT<	770.5174	outlier = 1.
if subject = "02"	& RT > 	215.1508	AND RT<	1232.8672	outlier = 1.
if subject = "04"	& RT > 	252.3149	AND RT<	1216.8491	outlier = 1.
if subject = "05"	& RT > 	300.9555	AND RT<	929.6805	outlier = 1.
if subject = "06"	& RT > 	207.8266	AND RT<	1257.8734	outlier = 1.
if subject = "07"	& RT > 	243.4472	AND RT<	981.9428	outlier = 1.
if subject = "08"	& RT > 	-89.7763	AND RT<	1568.6543	outlier = 1.
if subject = "09"	& RT > 	367.4003	AND RT<	881.5217	outlier = 1.
if subject = "10"	& RT > 	331.6466	AND RT<	1226.6954	outlier = 1.
if subject = "11"	& RT > 	244.0319	AND RT<	637.5041	outlier = 1.
if subject = "12"	& RT > 	183.2074	AND RT<	1292.9926	outlier = 1.
if subject = "13"	& RT > 	154.4489	AND RT<	1500.6791	outlier = 1.
if subject = "14"	& RT > 	263.0308	AND RT<	1078.5772	outlier = 1.
if subject = "15"	& RT > 	282.2567	AND RT<	841.0373	outlier = 1.
if subject = "16"	& RT > 	245.4398	AND RT<	1362.2942	outlier = 1.
if subject = "17"	& RT > 	372.2903	AND RT<	1050.5717	outlier = 1.
if subject = "18"	& RT > 	-110.8782	AND RT<	1548.0282	outlier = 1.
if subject = "19"	& RT > 	288.3015	AND RT<	1014.2805	outlier = 1.
if subject = "20"	& RT > 	214.5013	AND RT<	1227.3787	outlier = 1.
if subject = "21"	& RT > 	342.2927	AND RT<	1128.7253	outlier = 1.
if subject = "22"	& RT > 	287.9816	AND RT<	992.6504	outlier = 1.
if subject = "23"	& RT > 	189.6405	AND RT<	1529.3475	outlier = 1.
if subject = "24"	& RT > 	222.1288	AND RT<	1238.5672	outlier = 1.
if subject = "53"	& RT > 	287.6424	AND RT<	957.5376	outlier = 1.
Execute.

***exclude outliers, in addition to error trials***

USE ALL.
COMPUTE filter_$=(Errors = 0 & outlier = 1).
VARIABLE LABELS filter_$ 'Errors = 0 & outlier = 1 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

**Calcualte by-subject condition means

DATASET DECLARE Aggr_F1.
AGGREGATE
  /OUTFILE='Aggr_F1'
  /BREAK=Subject NamingTask Condition
  /RT_mean=MEAN(RT).

**create columns for each condition

DATASET ACTIVATE Aggr_F1.
IF  (Condition = "Congruent") congruent=RT_mean.
IF (Condition = "Incongruent") incongruent=RT_mean.
EXECUTE.

**create file with subject RTs

DATASET DECLARE F1.
AGGREGATE
  /OUTFILE='F1'
  /BREAK=Subject NamingTask
  /congruent_mean=MEAN(congruent) 
  /incongruent_mean=MEAN(incongruent).

**split file by task

DATASET ACTIVATE F1.
SORT CASES  BY NamingTask.
SPLIT FILE LAYERED BY NamingTask.

**conduct t-test on subject RTs

T-TEST PAIRS=Congruent_mean WITH incongruent_mean (PAIRED)
  /CRITERIA=CI(.9500)
  /MISSING=ANALYSIS.

***By-items analyses

**Open master data file


GET
  FILE='/Users/amelinger/Dropbox/My stuff/Experiments/RP-P/Data/alldata.sav'.
DATASET NAME DataSet4 WINDOW=FRONT.

** exclude error trials

DATASET ACTIVATE DataSet3.
USE ALL.
COMPUTE filter_$=(Errors = 0).
VARIABLE LABELS filter_$ 'Errors = 0 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

** identify outliers**

compute outlier=0.
execute.

if subject = "01"	& RT > 	317.7226	AND RT<	770.5174	outlier = 1.
if subject = "02"	& RT > 	215.1508	AND RT<	1232.8672	outlier = 1.
if subject = "04"	& RT > 	252.3149	AND RT<	1216.8491	outlier = 1.
if subject = "05"	& RT > 	300.9555	AND RT<	929.6805	outlier = 1.
if subject = "06"	& RT > 	207.8266	AND RT<	1257.8734	outlier = 1.
if subject = "07"	& RT > 	243.4472	AND RT<	981.9428	outlier = 1.
if subject = "08"	& RT > 	-89.7763	AND RT<	1568.6543	outlier = 1.
if subject = "09"	& RT > 	367.4003	AND RT<	881.5217	outlier = 1.
if subject = "10"	& RT > 	331.6466	AND RT<	1226.6954	outlier = 1.
if subject = "11"	& RT > 	244.0319	AND RT<	637.5041	outlier = 1.
if subject = "12"	& RT > 	183.2074	AND RT<	1292.9926	outlier = 1.
if subject = "13"	& RT > 	154.4489	AND RT<	1500.6791	outlier = 1.
if subject = "14"	& RT > 	263.0308	AND RT<	1078.5772	outlier = 1.
if subject = "15"	& RT > 	282.2567	AND RT<	841.0373	outlier = 1.
if subject = "16"	& RT > 	245.4398	AND RT<	1362.2942	outlier = 1.
if subject = "17"	& RT > 	372.2903	AND RT<	1050.5717	outlier = 1.
if subject = "18"	& RT > 	-110.8782	AND RT<	1548.0282	outlier = 1.
if subject = "19"	& RT > 	288.3015	AND RT<	1014.2805	outlier = 1.
if subject = "20"	& RT > 	214.5013	AND RT<	1227.3787	outlier = 1.
if subject = "21"	& RT > 	342.2927	AND RT<	1128.7253	outlier = 1.
if subject = "22"	& RT > 	287.9816	AND RT<	992.6504	outlier = 1.
if subject = "23"	& RT > 	189.6405	AND RT<	1529.3475	outlier = 1.
if subject = "24"	& RT > 	222.1288	AND RT<	1238.5672	outlier = 1.
if subject = "53"	& RT > 	287.6424	AND RT<	957.5376	outlier = 1.
Execute.

***exclude outliers, in addition to error trials***

USE ALL.
COMPUTE filter_$=(Errors = 0 & outlier = 1).
VARIABLE LABELS filter_$ 'Errors = 0 & outlier = 1 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.


**calculate by-item mean RTs


DATASET ACTIVATE DataSet3.
DATASET DECLARE Aggr_F2.
AGGREGATE
  /OUTFILE='Aggr_F2'
  /BREAK=Object NamingTask Condition
  /RT_mean=MEAN(RT).


**create condition columns

DATASET ACTIVATE Aggr_F2.
IF  (Condition = "Congruent") congruent=RT_mean.
IF (Condition = "Incongruent") incongruent=RT_mean.
EXECUTE.

**create file with by-item RTs


DATASET ACTIVATE Aggr_F2.
DATASET DECLARE F2.
AGGREGATE
  /OUTFILE='F2'
  /BREAK=Object NamingTask
  /congruent_mean=MEAN(congruent) 
  /incongruent_mean=MEAN(incongruent).

**split file by naming task


DATASET ACTIVATE F2.
SORT CASES  BY NamingTask.
SPLIT FILE LAYERED BY NamingTask.

**conduct by-item t-test


T-TEST PAIRS=congruent_mean WITH incongruent_mean (PAIRED)
  /CRITERIA=CI(.9500)
  /MISSING=ANALYSIS.
