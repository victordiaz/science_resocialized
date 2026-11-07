*Compute variables: mean of all vignettes, mean of private body consciousness,
PBC*Condition interaction.
*COMPUTE mean_vignettes=mean(Dog,Trolley,Wallet,Plane,Resume,Kitten).
*COMPUTE mean_PBC=mean(PBC#1,PBC#4,PBC#6,PBC#9,PBC#12).
*COMPUTE PBCbyCondition=mean_PBC*Condition.
*COMPUTE SST_correct=sum(SST#1,SST#2,SST#3,SST#4,SST#5,SST#6,SST#7,SST#8,SST#9,
SST#10,SST#11,SST#12,SST#13,SST#14,SST#15,SST#16,SST#17,SST#18,SST#19,SST#20,
SST#21,SST#22,SST#23,SST#24,SST#25,SST#26,SST#27,SST#28,SST#29,SST#30,SST#31,
SST#32,SST#33,SST#34,SST#35,SST#36,SST#37,SST#38,SST#39,SST#40).
*COMPUTE C_PBC = mean_PBC - 2.6192.
*COMPUTE C_PBCbyCondition = PBCbyCondition - 1.3053.
*EXECUTE.

*Use this filter for all analyses (with "all" Ps). It selects out participants who said that 
*all their answers were made up, those for whom there were experimental errors, and
*those that failed the SST task.
*This removes 11 Ps, leaving 208 useful Ps.
USE ALL.
COMPUTE filter_$=(Madeup_dummy = 0 & Exp_Error = 0 & SST_dummy = 1).
VARIABLE LABELS filter_$ 'Madeup_dummy = 0 & Exp_Error = 0 & SST_dummy = 1 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

*Testing emotion ratings. Schnall found that participants did not differ on any emotion
*based on experimental condition.

UNIANOVA Relaxed BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Angry BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Happy BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Sad BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Relaxed BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Afraid BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Depressed BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Disgusted BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Upset BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.
UNIANOVA Confused BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=Condition.


*************************************************
*In Exp1, Schnall found no group difference among the emotion ratings. DID REPLICATE.
*The two conditions did not differ in any of the emotion. Note: For Happy, p=0.091.


T-TEST GROUPS=Condition(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=Relaxed Angry Happy Sad Afraid Depressed Disgusted Upset Confused
  /CRITERIA=CI(.95).
*************************************************

*ANOVA testing the composite vignette rating based on condition. Schnall found that Ps
*evaluated the scenarios as less immoral after cleanliness prime. DID NOT REPLICATE.
*Means 6.50 (no prime), 6.47 (cleanliness prime).
UNIANOVA mean_vignettes BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Follow-ups on individual scenarios.
*All nonsignificant. DID NOT REPLICATE.

*Dog. Schnall: nonsignificant. Replication: nonsignificant.
UNIANOVA Dog BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Trolley. Schnall: nonsignificant. Replication: nonsignificant.
UNIANOVA Trolley BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Wallet. Schnall: nonsignificant. Replication: nonsignificant.
UNIANOVA Wallet BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Plane Crash. Schnall: nonsignificant. Replication: nonsignificant.
UNIANOVA Plane BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Resume. Schnall: nonsignificant. Replication: nonsignificant.
UNIANOVA Resume BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Kitten. Schnall: significant. Replication: nonsignificant.
UNIANOVA Kitten BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

**********************************************************************************
*Analyses using PBC as a moderator.
*Median split.
*PBC does not moderate feelings of "wrongness." Effect nonsignificant.
*High PBC individuals rate actions as MORE wrong (opposite direction), although ns.
*Follow-ups on individual scenarios; all were nonsignificant with PBC as a moderator,
*although the interaction on resume was marginal (but in the opposite direction).
UNIANOVA mean_vignettes BY Condition median_PBC
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(Condition)
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition median_PBC Condition*median_PBC.
UNIANOVA Dog BY Condition median_PBC
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(Condition)
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition median_PBC Condition*median_PBC.
UNIANOVA Trolley BY Condition median_PBC
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(Condition)
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition median_PBC Condition*median_PBC.
UNIANOVA Wallet BY Condition median_PBC
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(Condition)
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition median_PBC Condition*median_PBC.
UNIANOVA Plane BY Condition median_PBC
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(Condition)
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition median_PBC Condition*median_PBC.
UNIANOVA Resume BY Condition median_PBC
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(Condition)
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition median_PBC Condition*median_PBC.
UNIANOVA Kitten BY Condition median_PBC
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(Condition)
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition median_PBC Condition*median_PBC.


*Regression controlling for PBC.
*Model nonsignificant.
*Follow-ups on individual scenarios, all were nonsignificant.
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT mean_vignettes
  /METHOD=ENTER Condition C_PBC C_PBCbyCondition.
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT Dog
  /METHOD=ENTER Condition C_PBC C_PBCbyCondition.
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT Trolley
  /METHOD=ENTER Condition C_PBC C_PBCbyCondition.
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT Wallet
  /METHOD=ENTER Condition C_PBC C_PBCbyCondition.
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT Plane
  /METHOD=ENTER Condition C_PBC C_PBCbyCondition.
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT Resume
  /METHOD=ENTER Condition C_PBC C_PBCbyCondition.
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT Kitten
  /METHOD=ENTER Condition C_PBC C_PBCbyCondition.


**********************************************************************************
*Analyses using 3 levels of filtering. (No participant correctly guessed the hypotheses)
*1 Ps who suspected that the SST influenced their responses.
*2 Ps who suspected that SST influenced their vignette answers.
*3 Ps who correctly guessed the experimental hypotheses.

*Calculating Cohen's kappa for reliability on filter variables.
*FC and DJ as raters.
*k = .79 ("substantial agreement"). spearman's r = .81.
CROSSTABS
  /TABLES=Filter_DJ BY Filter_FC
  /FORMAT=AVALUE TABLES
  /STATISTICS=CORR KAPPA 
  /CELLS=COUNT
  /COUNT ROUND CELL.

*Number of suspicious participants.
*0 (198), 1 (5), 2 (6), 3 (0).
FREQUENCIES VARIABLES=Final_Rating
  /ORDER=ANALYSIS.

*Filter by group 3 (and those who made up answers or had experimenter errors).
*No Ps in this category; all effects do not change; all still nonsignificant.
USE ALL.
COMPUTE filter_$=(Madeup_dummy = 0 & Exp_Error = 0 & Final_Rating < 2).
VARIABLE LABELS filter_$ 'Madeup_dummy = 0 & Exp_Error = 0 & Final_Rating < 2 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

*Filter by groups 3 and 2 (and those who made up answers or had experimenter errors).
*All effects do not change; all still nonsignificant.
USE ALL.
COMPUTE filter_$=(Madeup_dummy = 0 & Exp_Error = 0 & Final_Rating < 2).
VARIABLE LABELS filter_$ 'Madeup_dummy = 0 & Exp_Error = 0 & Final_Rating < 2 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.


*Filter by groups 3, 2, 1 (and those who made up answers or had experimenter errors).
*All effects do not change; all still nonsignificant.
USE ALL.
COMPUTE filter_$=(Madeup_dummy = 0 & Exp_Error = 0 & Final_Rating < 1).
VARIABLE LABELS filter_$ 'Madeup_dummy = 0 & Exp_Error = 0 & Final_Rating < 1 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.
