options ls=120 nocenter nodate yearcutoff=2000;  
*Look Pretty;
libname perm 'V:\KLane\Bard.Office.Computer\Research.office\OSF\Reproducability\data';  
*Work with this Directory;
Title1 'Henderson et al. Replicaiton'; 
*Use this as a title on all pages;
proc import datafile='V:\KLane\Bard.Office.Computer\Research.office\OSF\Reproducability\data\alldata.txt'
     out=data      dbms=dlm      replace;      delimiter='09'x;      getnames=yes; 	 guessingrows=100; run;

data perm.alldata; set data;
NotTorn_R=-1*NotTorn; Indecisive_RC=Indecisive-4; ambiv=mean (of strongmixed nottorn_r indecisive_rc);
run;

**Demos;
proc freq data=perm.alldata; tables gender;
proc freq; tables race;
proc means n mean std median; var age; 
proc freq; tables sexoffender; 
proc freq data=perm.alldata; tables sexoffender*condition;
run;


**Analyses Exlcuding People Who Answered "Yes" to the Sex offender Question;
Title2 'Exlcuding Yes to Sex Offender';
data nosexoffend; set perm.alldata; if sexoffender="Yes" then delete; run;
proc corr alpha nocorr; var strongmixed nottorn_r indecisive_rc; 
proc corr; var certain ambiv; 
proc glm; class condition; model ambiv=condition; means condition; 
proc ttest data=nosexoffend; class condition; var ambiv; where condition in (1 2); run;
proc ttest; class condition; var ambiv; where condition in (0 2); run;
proc ttest; class condition; var ambiv; where condition in (0 1); run;
proc glm; class condition; model certain=condition; means condition;run;

**Analyses of all subjects;
Title2 'Including Everyone';
proc corr alpha nocorr data=perm.alldata; var strongmixed nottorn_r indecisive_rc; 
proc corr data=perm.alldata; var certain ambiv; 
proc glm data=perm.alldata; class condition; model ambiv=condition; means condition; 
proc ttest data=perm.alldata; class condition; var ambiv; where condition in (1 2); run;
proc ttest data=perm.alldata; class condition; var ambiv; where condition in (0 2); run;
proc ttest data=perm.alldata; class condition; var ambiv; where condition in (0 1); run;
proc glm data=perm.alldata; class condition; model certain=condition; means condition; run;

proc sort data=perm.alldata; by sexoffender; proc ttest; var ambiv certain; class sexoffender; run;

proc sort; by gender; proc means; var ambiv certain; by gender; run;
run;
