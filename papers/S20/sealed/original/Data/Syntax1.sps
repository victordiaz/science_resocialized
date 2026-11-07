
DESCRIPTIVES VARIABLES=avg_time_sum_ac avg_time_neutral_ac avg_time_sum_mu avg_time_neutral_mu
  /STATISTICS=MEAN STDDEV MIN MAX SEMEAN.


T-TEST PAIRS=avg_sum avg_time_sum_ac avg_time_sum_mu WITH avg_neutral avg_time_neutral_ac 
    avg_time_neutral_mu (PAIRED)
  /CRITERIA=CI(.9500)
  /MISSING=ANALYSIS.

DATASET ACTIVATE DataSet1.
GLM avg_time_sum_ac avg_time_neutral_ac avg_time_sum_mu avg_time_neutral_mu
  /WSFACTOR=factor1 2 Polynomial 
  /MEASURE=AC MU 
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=factor1.

