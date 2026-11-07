GLM correct intrusion new BY listtype
  /WSFACTOR=probetype 3 Polynomial 
  /METHOD=SSTYPE(3)
  /PLOT=PROFILE(probetype*listtype)
  /EMMEANS=TABLES(OVERALL) 
  /EMMEANS=TABLES(listtype) 
  /EMMEANS=TABLES(probetype) 
  /EMMEANS=TABLES(listtype*probetype) 
  /PRINT=DESCRIPTIVE ETASQ OPOWER 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=probetype 
  /DESIGN=listtype.
