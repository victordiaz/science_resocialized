**********Confirmatory analysis: conditional percentage of correct T2 reports using a 2 (group: bilingual and monolingual) x 4 (lag: 1, 3, 5, and 8) mixed ANOVA where lag was a within participants variable.
 GLM Lag1_T2_correct Lag3_T2_correct Lag5_T2_correct Lag8_T2_correct BY Group
  /WSFACTOR=lag 4 Polynomial 
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Group*lag) 
  /PRINT=ETASQ 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=lag 
  /DESIGN=Group.

**********Confirmatory analysis: t-test at Lag 3.
T-TEST GROUPS=Group(1 2)
  /MISSING=ANALYSIS
  /VARIABLES=Lag3_T2_correct
  /CRITERIA=CI(.95).


**********Exploratory analyses: T1 accuracy with language group varying between participants and lag varying within participants.
GLM Lag1_T1_correct Lag3_T1_correct Lag5_T1_correct Lag8_T1_correct BY Group
  /WSFACTOR=lag 4 Polynomial 
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Group*lag) 
  /PRINT=ETASQ 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=lag 
  /DESIGN=Group.

**********Exploratory analyses: T1 accuracy correlated with Raven scores.
CORRELATIONS
  /VARIABLES=T1_correct_overall Raven_total
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

**********Exploratory analyses: conditional T2|T1 accuracy correlated with Raven scores.
CORRELATIONS
  /VARIABLES=Raven_total Lag1_T2_correct Lag3_T2_correct Lag5_T2_correct Lag8_T2_correct
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

**********Exploratory analyses: exclude the four participants who did not acquire their second language until adulthood (i.e., after age 12) and repeated the 
analysis of conditional percentage of correct T2 reports using a 2 (group: bilingual and monolingual) x 4 (lag: 1, 3, 5, and 8) mixed ANOVA. 
USE ALL.
COMPUTE filter_$=(Both_as_child  ~= 2).
VARIABLE LABELS filter_$ 'Both_as_child  ~= 2 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

GLM Lag1_T2_correct Lag3_T2_correct Lag5_T2_correct Lag8_T2_correct BY Group
  /WSFACTOR=lag 4 Polynomial 
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(Group*lag) 
  /PRINT=ETASQ 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=lag 
  /DESIGN=Group.

T-TEST GROUPS=Group(1 2)
  /MISSING=ANALYSIS
  /VARIABLES=Lag3_T2_correct
  /CRITERIA=CI(.95).
