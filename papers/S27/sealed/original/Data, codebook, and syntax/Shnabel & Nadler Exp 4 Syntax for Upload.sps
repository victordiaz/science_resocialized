# This is the SPSS data analysis code for Elizabeth Gilbert's replication of Experiment 4 from 
# Shnabel & Nadler (JPSP 2008).    This code applies to the data titled "Shnabel & Nadler Rep Data - for
# OSF upload 2.23.2015" available along with codebook at https://osf.io/7dhum/. 

# Manipulation check of role

DATASET ACTIVATE DataSet1.
T-TEST GROUPS=VictimOrPerpV0P1(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=FeelingOffendedRev1 Offending1 PartnerAngrywithYou1
  /CRITERIA=CI(.95).


# Manipulation check for Feedback Condition (accept or empower)

T-TEST GROUPS=AcceptOrEmpowerA0E1(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=ThinkCompetent2 ThinkNice2
  /CRITERIA=CI(.95).


# T-tests to examine participant’s sense of power, public moral image, and willingness to reconcile
# prior to receiving the feedback by condition (victim or perpetrator).

T-TEST GROUPS=VictimOrPerpV0P1(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=SensePowerTime1 PublicMoralImage1 AvgWillingReconcileTime1
  /CRITERIA=CI(.95).


# Split file by whether in Acceptance or Empowerment condition
SORT CASES  BY AcceptOrEmpowerA0E1.
SPLIT FILE SEPARATE BY AcceptOrEmpowerA0E1.


# T-tests to examine participant’s sense of power, public moral image, and willingness to reconcile
# after receiving the feedback by condition (victim or perpetrator and by accept or empower).

# Victim or perpetrator t-test
T-TEST GROUPS=VictimOrPerpV0P1(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=AvgSensePowerTime2 PublicMoralImageTime2 AvgWillingReconcileTime2
  /CRITERIA=CI(.95).

#Unsplit file so no longer separated by Accept or Empower condition
SPLIT FILE OFF.

# Accept or Empower t-test
DATASET ACTIVATE DataSet1.
T-TEST GROUPS=AcceptOrEmpowerA0E1(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=ThinkCompetent2 ThinkNice2
  /CRITERIA=CI(.95).

# Sense of Power, Public Moral Image, and Willingness to Reconcile Before and After Receiving 
# Acceptance or Empowerment Feedback. (t-tests)

# Before

T-TEST GROUPS=VictimOrPerpV0P1(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=SensePowerTime1 PublicMoralImage1 AvgWillingReconcileTime1
  /CRITERIA=CI(.95).

# After Accept or Empower

SORT CASES  BY AcceptOrEmpowerA0E1.
SPLIT FILE SEPARATE BY AcceptOrEmpowerA0E1.

T-TEST GROUPS=VictimOrPerpV0P1(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=AvgSensePowerTime2 PublicMoralImageTime2 AvgWillingReconcileTime2
  /CRITERIA=CI(.95).

SPLIT FILE OFF.

# Series of mixed ANOVAs to test the effects of role, message, and time on the 
# dependent variables of sense of power, public moral image, and willingness to reconcile

# DV = Sense of Power

GLM SensePowerTime1 AvgSensePowerTime2 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

# DV = Public Moral Image

GLM PublicMoralImage1 PublicMoralImageTime2 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

# DV = Willingness to Reconcile

GLM AvgWillingReconcileTime1 AvgWillingReconcileTime2 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

# Follow Up Comparisons Comparing Main Effects of Role, Message, and Time, on Sense of Power, 
# Public Moral Image, and Willingness to Reconcile.

# IV = Role

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT AvgSensePowerTime2
  /METHOD=ENTER VictimOrPerpV0P1.

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT PublicMoralImageTime2
  /METHOD=ENTER VictimOrPerpV0P1.

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT AvgWillingReconcileTime2
  /METHOD=ENTER VictimOrPerpV0P1.


# IV = Message (accept or empower)

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT AvgSensePowerTime2
  /METHOD=ENTER AcceptOrEmpowerA0E1.

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT PublicMoralImageTime2
  /METHOD=ENTER AcceptOrEmpowerA0E1.

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT AvgWillingReconcileTime2
  /METHOD=ENTER AcceptOrEmpowerA0E1.

# IV = Time 

GLM SensePowerTime1 AvgSensePowerTime2
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time.

GLM PublicMoralImage1 PublicMoralImageTime2
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time.

GLM AvgWillingReconcileTime1 AvgWillingReconcileTime2
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time.

# Two-way Time X Message, Time X Message, and Message X Role interactions 
# DVs = Sense of Power, Public Moral Image, and Willingness to Reconcile

# Time X Role (Victim or Perpetrator)

DATASET ACTIVATE DataSet1.
GLM SensePowerTime1 AvgSensePowerTime2 BY VictimOrPerpV0P1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=VictimOrPerpV0P1.

GLM PublicMoralImage1 PublicMoralImageTime2 BY VictimOrPerpV0P1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=VictimOrPerpV0P1.

GLM AvgWillingReconcileTime1 AvgWillingReconcileTime2 BY VictimOrPerpV0P1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=VictimOrPerpV0P1.

# Time X Message (Accept or Empower)

GLM SensePowerTime1 AvgSensePowerTime2 BY AcceptOrEmpowerA0E1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=AcceptOrEmpowerA0E1.

GLM PublicMoralImage1 PublicMoralImageTime2 BY AcceptOrEmpowerA0E1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=AcceptOrEmpowerA0E1.

GLM AvgWillingReconcileTime1 AvgWillingReconcileTime2 BY AcceptOrEmpowerA0E1
  /WSFACTOR=Time 2 Polynomial 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=Time 
  /DESIGN=AcceptOrEmpowerA0E1.

# Role (Victim or Perpetrator) X Message (Accept or Empower)
# Before (Time 1) and After (time 2)

UNIANOVA SensePowerTime1 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

UNIANOVA PublicMoralImage1 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

UNIANOVA AvgWillingReconcileTime1 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

UNIANOVA AvgSensePowerTime2 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

UNIANOVA PublicMoralImageTime2 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.

UNIANOVA AvgWillingReconcileTime2 BY VictimOrPerpV0P1 AcceptOrEmpowerA0E1
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /CRITERIA=ALPHA(0.05)
  /DESIGN=VictimOrPerpV0P1 AcceptOrEmpowerA0E1 VictimOrPerpV0P1*AcceptOrEmpowerA0E1.
