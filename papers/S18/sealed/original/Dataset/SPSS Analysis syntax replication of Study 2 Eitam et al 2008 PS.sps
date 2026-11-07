* Encoding: UTF-8.
*Calculating the mean response time for random blocks 1 and 2.
COMPUTE RB12Mean=Mean(R1Mean,R2Mean).
EXECUTE.
VARIABLE LABELS
RB12Mean 'Mean response time for the two random blocks (experimental blocks 6 and 8)'.
EXECUTE.

*Calculating the index of learning for mean RT.
COMPUTE Learning=FSMean-RB12Mean.
EXECUTE.
VARIABLE LABELS
Learning 'Difference between the mean RT in the two random blocks and the mean RT in the fixed-sequence block'.
EXECUTE.

*Calculating the mean of the median response times for random blocks 1 and 2.
COMPUTE RB12Median=Mean(R1Median,R2Median).
EXECUTE.
VARIABLE LABELS
RB12Median 'Average of median response time for the two random blocks (experimental blocks 6 and 8)'.
EXECUTE.

*Calculating the index of learning for median RT.
COMPUTE MedLearn=FSMedian-RB12Median.
EXECUTE.
VARIABLE LABELS
MedLearn 'Difference between the average median RT in the two random blocks and the median RT in the fixed-sequence block'.
EXECUTE.



*Filtering to only use those who were not excluded based on initial exclusionary criteria.
*Participants were excluded if they did not have complete response time data.
*Specifically, if they did not have RT data for the blocks under consideration.
*Also, those who suspected the goal priming procedure were excluded.
*Lastly, we only looked at the first 79 from each condition as our stopping rule was to achieve a power of .80
*to detect the original effect.

USE ALL.
COMPUTE filter_$=(Include=0).
VARIABLE LABELS filter_$ 'Include=0 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

*The next exclusion criterion was to exclude anyone whose learning score was
*4 stadard deviations or more from the mean.
*Thus, we examined the learning variable to see if any participants met this criterion.

EXAMINE VARIABLES=learning
  /PLOT BOXPLOT HISTOGRAM NPPLOT
  /COMPARE GROUPS
  /STATISTICS DESCRIPTIVES
  /CINTERVAL 95
  /MISSING LISTWISE
  /NOTOTAL.

*The Mean was -33.4 and the SD was 72.5.
*Thus, participants were excluded if their learning score was <-323.4 or >256.6.
*Two were excluded (one from each condition) based on the > 4 S.D. from the learning mean exclusionary criterion.
*Thus, the next one from each condition was included in order to maintain the sample size at 158 for a power of .80.

USE ALL.
COMPUTE filter_$=(Include1=0).
VARIABLE LABELS filter_$ 'Include1=0 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

*Re-examining the learning variable with the two new participants included to check if their learning scores were also
*greater than 4 S.D. from the mean.

EXAMINE VARIABLES=learning
  /PLOT BOXPLOT HISTOGRAM NPPLOT
  /COMPARE GROUPS
  /STATISTICS DESCRIPTIVES
  /CINTERVAL 95
  /MISSING LISTWISE
  /NOTOTAL.

*The new mean is -27.7 and SD=51.8.
*Therefore, >4SD would be <-234.9 and >179.5.
*No cases fell outside of these values.

*Now that the sample of n=79 for each condition has been established, testing whether or not
*learning is different for the two conditions as indexed by mean response times.

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=Learning
  /CRITERIA=CI(.95).

*Now that the sample of n=79 for each condition has been established, testing whether or not
*learning is different for the two conditions as indexed by median response time.

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=MedLearn
  /CRITERIA=CI(.95).

*Also examining average accuracy as done in Eitam.

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=R1correct
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=R2correct
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=FScorrect
  /CRITERIA=CI(.95).

*As done in Eitam, next comparing performace between the conditions in mean and median RT in the random blocks.

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=R1mean
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=R2mean
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=R1median
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=R2median
  /CRITERIA=CI(.95).

*Next, comparing motivation variables: accurate, fast, learn rule, and succeed.

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=accurate
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=quickly
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=succeed
  /CRITERIA=CI(.95).

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=howimportantrule
  /CRITERIA=CI(.95).

*Next, comparing explicit knowledge verbilization score between groups.

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=orderdescribe
  /CRITERIA=CI(.95).

*Next, comparing explicit knowledge graphic probe score between groups.

T-TEST GROUPS=Condition(2 1)
  /MISSING=ANALYSIS
  /VARIABLES=gprobe
  /CRITERIA=CI(.95).

*Examining the analysis as a repeated-measures design.
*Also doing this as one way to get the data to reproduce Figure 1 from Eitam.

GLM R1Mean FSMean R2Mean BY Condition
  /WSFACTOR=Block 3 Polynomial 
  /METHOD=SSTYPE(3)
  /PLOT=PROFILE(Block*Condition)
  /EMMEANS=TABLES(OVERALL) 
  /PRINT=DESCRIPTIVE ETASQ OPOWER HOMOGENEITY 
  /PLOT=RESIDUALS 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Block 
  /DESIGN=Condition.
