*Compute variables: mean of all vignettes, mean of private body consciousness,
PBC*Condition interaction.
*COMPUTE mean_vignettes=mean(Dog,Trolley,Wallet,Plane,Resume,Kitten).
*COMPUTE mean_PBC=mean(PBC#1,PBC#4,PBC#6,PBC#9,PBC#12).
*COMPUTE PBCbyCondition=mean_PBC*Condition.
*COMPUTE C_PBC = mean_PBC - 2.6192.
*COMPUTE C_PBCbyCondition = PBCbyCondition - 1.3053.
*EXECUTE.

*Use this filter for all analyses (with "all" Ps). It selects out participants who said that all 
their answers were made up, and those for whom there were experimental errors.
USE ALL.
COMPUTE filter_$=(Madeup_dummy = 0 & Exp_Error = 0).
VARIABLE LABELS filter_$ 'Madeup_dummy = 0 & Exp_Error = 0 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

*Testing emotion ratings. Schnall found that participants were more disgusted than any
*other emotion, with no effects of condition. REPLICATED.
*Post-hoc tests also reveal elevated levels of feeling upset and confused.
GLM Relaxed Angry Happy Sad Afraid Depressed Disgusted Upset Confused BY Condition
  /WSFACTOR=Emotion 9 Polynomial 
  /METHOD=SSTYPE(3)
  /PLOT=PROFILE(Emotion*Condition)
  /EMMEANS=TABLES(Emotion) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Emotion 
  /DESIGN=Condition.

*ANOVA testing the composite vignette rating based on condition. Schnall found that Ps
*evaluated the scenarios as less immoral after hand-washing. DID NOT REPLICATE.
*Means 5.65 (no hand-washing), 5.65 (hand-washing).
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

*Trolley. Schnall: significant. Replication: nonsignificant.
UNIANOVA Trolley BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Wallet. Schnall: significant. Replication: nonsignificant.
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

*Resume. Schnall: marginally significant. Replication: nonsignificant.
UNIANOVA Resume BY Condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition.

*Kitten. Schnall: nonsignificant. Replication: nonsignificant.
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
*Follow-ups on individual scenarios; all were nonsignificant with PBC as a moderator.
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
*Model nonsignificant, neither predictor significant.
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
*Analyses using 3 levels of filtering.
*1 Ps who suspected that the videos or handwashing influenced their responses.
*2 Ps who suspected that the videos of handwashing influenced their vignette answers.
*3 Ps who correctly guessed the experimental hypotheses.

*Calculating Cohen's kappa for reliability on filter variables.
*FC and DJ as raters.
*k = .65 ("substantial agreement"). spearman's r = .75.
CROSSTABS
  /TABLES=Filter_DJ BY Filter_FC
  /FORMAT=AVALUE TABLES
  /STATISTICS=CORR KAPPA 
  /CELLS=COUNT
  /COUNT ROUND CELL.

*Number of suspicious participants.
*0 (89), 1 (25), 2 (12), 3 (6).
FREQUENCIES VARIABLES=Final_Rating
  /ORDER=ANALYSIS.

*Filter by group 3 (and those who made up answers or had experimenter errors).
*All effects do not change; all still nonsignificant.
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
