*Full factorial model

GLM Sens_Friend Sens_SI Sens_Sad Sens_Rej BY Gender Pres_time
  /WSFACTOR=affect 2 Polynomial sex 2 Polynomial 
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(OVERALL) 
  /EMMEANS=TABLES(Gender) 
  /EMMEANS=TABLES(Pres_time) 
  /EMMEANS=TABLES(affect) 
  /EMMEANS=TABLES(sex) 
  /EMMEANS=TABLES(Gender*Pres_time) 
  /EMMEANS=TABLES(Gender*affect) 
  /EMMEANS=TABLES(Gender*sex) 
  /EMMEANS=TABLES(Pres_time*affect) 
  /EMMEANS=TABLES(Pres_time*sex) 
  /EMMEANS=TABLES(affect*sex) 
  /EMMEANS=TABLES(Gender*Pres_time*affect) 
  /EMMEANS=TABLES(Gender*Pres_time*sex) 
  /EMMEANS=TABLES(Gender*affect*sex) 
  /EMMEANS=TABLES(Pres_time*affect*sex) 
  /EMMEANS=TABLES(Gender*Pres_time*affect*sex) 
  /PRINT=DESCRIPTIVE ETASQ 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=affect sex affect*sex
  /DESIGN=Gender Pres_time Gender*Pres_time.

* post-hoc / primary analysis of interest: gender x positive sensitivity

GLM Sens_Friend Sens_SI BY Gender
  /WSFACTOR=affect 2 Polynomial 
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(OVERALL) 
  /EMMEANS=TABLES(affect) 
  /EMMEANS=TABLES(Gender) 
  /EMMEANS=TABLES(Gender*affect) 
  /PRINT=DESCRIPTIVE ETASQ 
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=affect 
  /DESIGN=Gender.
