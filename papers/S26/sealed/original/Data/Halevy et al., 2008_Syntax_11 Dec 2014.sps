
DATASET ACTIVATE DataSet1.
UNIANOVA Pool_B_Percent BY Condition_Game Condition_Communication
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /EMMEANS=TABLES(Condition_Game) 
  /PRINT=ETASQ
  /CRITERIA=ALPHA(.05)
  /DESIGN=Condition_Game Condition_Communication Condition_Game*Condition_Communication.

USE ALL.
COMPUTE filter_$=(Condition_Game = 2).
VARIABLE LABELS filter_$ 'Condition_Game = 2 (FILTER)'.
VALUE LABELS filter_$ 0 'Not Selected' 1 'Selected'.
FORMATS filter_$ (f1.0).
FILTER BY filter_$.
EXECUTE.

T-TEST GROUPS=Condition_Communication(1 2)
  /MISSING=ANALYSIS
  /VARIABLES=Pool_W_Percent
  /CRITERIA=CI(.95).
