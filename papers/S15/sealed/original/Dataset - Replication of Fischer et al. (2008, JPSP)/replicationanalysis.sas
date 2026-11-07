
/*CREATE LIBRARIES*/ 
libname rep 'C:\Users\ratliff\Documents\Reproducibility Study\data analysis'; 

/*IMPORT DATA*/
PROC IMPORT OUT= rep.explicitimport 
DATAFILE= "C:\Users\ratliff\Documents\Reproducibility Study\data analysis\explicit.txt" 
DBMS=TAB REPLACE;
GETNAMES=YES;
DATAROW=2; 
RUN;


PROC IMPORT OUT= rep.sessionimport 
DATAFILE= "C:\Users\ratliff\Documents\Reproducibility Study\data analysis\sessions.txt" 
DBMS=TAB REPLACE;
GETNAMES=YES;
DATAROW=2; 
RUN;

PROC IMPORT OUT= rep.demoimport 
DATAFILE= "C:\Users\ratliff\Documents\Reproducibility Study\data analysis\demographics.txt" 
DBMS=TAB REPLACE;
GETNAMES=YES;
DATAROW=2; 
RUN;

PROC IMPORT OUT= rep.sessiontaskimport
DATAFILE= "C:\Users\ratliff\Documents\Reproducibility Study\data analysis\sessionTasks.txt" 
DBMS=TAB REPLACE;
GETNAMES=YES;
DATAROW=2; 
RUN;

/*LOOK AT SESSIONTASK INFORMATION SO I CAN MERGE WITH DEMOGRAPHICS BY USERID*/
data rep.session; set rep.sessionimport;
keep session_id _user_id _session_status _session_date; run;

/*data rep.session; set rep.session;
proc freq; tables _session_status; run;*/

/*MERGE DEMOGRAPHICS WITH SESSION INFO BY USER ID*/
data rep.demo; set rep.demoimport;
proc sort; by _user_id; run;
proc transpose data=rep.demo out=rep.demo; by _user_id; id characteristic; var _value; run;
data rep.demo; set rep.demo; drop _name_; run;

data rep.session; set rep.session;
proc sort; by _user_id;
data rep.demo; set rep.demo;
proc sort; by _user_id; run;
data rep.demosession; 
merge rep.demo rep.session; by _user_id; run;

data rep.demosession; set rep.demosession;
if session_id in (' ', '.') then delete; run;
data rep.demosession; set rep.demosession;
_session_id = session_id; drop session_id; run;

/*WORK WITH SESSIONTASK INFO TO GET STUDY/CONDITION INFORMATION*/
data rep.task; set rep.sessiontaskimport; proc sort; by session_id; run;
data rep.task; set rep.task; keep _task_id session_id _task_number; run;

data rep.task; set rep.task;
proc sort; by session_id; run;
proc transpose data=rep.task out=rep.task; by session_id; id _task_number; var _task_id; run;
data rep.task; set rep.task; drop _name_; run;

data rep.task; set rep.task;
_session_id = session_id; drop session_id; run;

data rep.task; set rep.task;
if _6 in ('newinfodirection') then focus = 'direction';
else if _6 in ('newinfoquality') then focus = 'quality';
else if _6 in ('newinfocontrol') then focus = 'control'; run;

data rep.task; set rep.task;
if _7 in ('tenpiecesofinfo') then options = 'ten';
else if _7 in ('twopiecesofinfo1', 'twopiecesofinfo2', 'twopiecesofinfo3', 'twopiecesofinfo4', 'twopiecesofinfo5') 
then options = 'two'; run;

data rep.task; set rep.task;
keep _session_id focus options; run;

/*WORK WITH EXPLICIT DATA*/
data rep.explicit; set rep.explicitimport;
if _question_name in ('text', 'feedback', 'd', 'longlonglonglonglonglonglonglonglonglong') then delete; run;

data rep.explicit; set rep.explicit;
proc sort; by _session_id; run;
proc transpose data=rep.explicit out=rep.explicit; by _session_id; id _question_name; var _question_response; run;

data rep.strategy; set rep.explicit;
keep _session_id strategy; run;

data rep.explicit; set rep.explicit;
drop _name_ strategy tenpiecesrt tenpiecestrt twopiecesrt twopiecestrt twopieces2rt twopieces2trt 
twopieces3rt twopieces3trt twopieces4rt twopieces4trt twopieces5rt twopieces5trt judgment1rt judgment1trt judgment2rt judgment2trt; run;
/*NOTE: I'm dropping the strategy varible from this file so the coders can analyze it separate from the data*/
/*I'm also dropping the responsetime variables because we have no hypotheses for these and they have nothing to 
do with the replication*/

data rep.explicit; set rep.explicit;
if tenpieces in ('1', '3', '5', '7', '9') then newtenpieces = 1;
else if tenpieces in ('2', '4','6','8','10') then newtenpieces = 2; run;

data rep.explicit; set rep.explicit;
if twopieces in ('1','2', '3', '4','5', '6', '7', '8', '9', '10') then newtwopieces = twopieces;
else if twopieces2 in ('1','2', '3', '4','5', '6', '7', '8', '9', '10') then newtwopieces = twopieces2;
else if twopieces3 in ('1','2', '3', '4','5', '6', '7', '8', '9', '10') then newtwopieces = twopieces3;
else if twopieces4 in ('1','2', '3', '4','5', '6', '7', '8', '9', '10') then newtwopieces = twopieces4;
else if twopieces5 in ('1','2', '3', '4','5', '6', '7', '8', '9', '10') then newtwopieces = twopieces5; 
drop twopieces twopieces2 twopieces3 twopieces4 twopieces5; drop tenpieces; run;

/*MERGE ALL MAIN DATAFILES TOGETHER*/
data rep.explicit; set rep.explicit; proc sort; by _session_id; run;
data rep.task; set rep.task; proc sort; by _session_id; run;
data rep.demosession; set rep.demosession; proc sort; by _session_id; run;
data rep.all; merge rep.explicit rep.task rep.demosession; by _session_id; run;

data rep.all; set rep.all;
if _session_status notin ('C') then delete; run;

/*THIS WAS AN A PRIORI DECISION TO ONLY USE US CITIZENS*/
data rep.all; set rep.all;
if citizenship notin ('us') then delete; run;

/*DROP SOME BLANK OR COMPLETELY UNNECESSARY VARIABLES*/
data rep.all; set rep.all;
drop reldenom _session_status citizenship dayofbirth class engfluency ethnicity income; run;

/*CREATE A SINGLE-COLUMN DV AND MAKE IT A NUMERIC VARIABLE*/
data rep.all; set rep.all;
if options in ('two') then newinfochoice = newtwopieces;
else if options in ('ten') then newinfochoice = newtenpieces; run;
data rep.all; set rep.all;
infochoice = (1*newinfochoice); drop newinfochoice; run;

data rep.all; set rep.all;
if judgment1 in ('1') and infochoice in ('2') then decision = 'disconfirming';
else if judgment1 in ('2') and infochoice in ('1') then decision = 'disconfirming';
else if judgment1 in ('1') and infochoice in ('1') then decision = 'confirming';
else if judgment1 in ('2') and infochoice in ('2') then decision = 'confirming'; run;

/*GET RID OF PARTICIPANTS DEEMED TO KNOW THE PURPOSE OF THE STUDY*/
data rep.all; set rep.all;
if _session_id in ('1901549', '1902091', '1902335', '1903358', '1903606', '1903694', '1904148', '1904677', '1904989', '1905015', '1905289', '1905474', '1905484', 
'1905509', '1905560', '1906197', '1906317', '1906539', '1906585', '1906695', '1906888', '1907043', '1908016', '1908093', '1908418', '1908580', '1908585', '1909075',
'1909171', '1909473') then delete; run;

