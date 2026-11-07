################################################################################
##################          REPLICATION R CODES               ##################
################################################################################
#
##@@ INSTRUCTIONS @@##
# Please do not remove any comments from this file, but feel free to add as many
# comments to R code as you like!
#
# Replace all ---USER INPUT--- sections with relevant input (including the - 
# symbols).
#
# When you are done, save this file as RPP_YYYY.R, where YYYY is the OSF code of 
# the project.
# e.g., The first study, Tracing attention and the activation...., should be
# called RPP_qwkum.R (since https://osf.io/qwkum/ is the project site)
#
# For any questions, please contact me at sacha.epskamp@gmail.com
#
##@@ GENERAL INFORMATION @@##
#@ Study Title: A word-order constraint on phonological activation. 
#@ Coder name: Frits Traets
#@ Coder e-mail: frits.traets@student.kuleuven.be
#@ Type of statistic: t
#@ Type of effect-size: Cohens d
#@ OSF link project: https://osf.io/dncxa/
#@ OSF link replication report: https://osf.io/e3ry5/
#
##@@ REQUIRED PACKAGES @@##
library("httr")          #To read in data
library("RCurl")         #To read in data
library("foreign")       #To read in data
library("dplyr")         #To transoform data
library("tidyr")         #To transform data
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

#data with subjects
file<-getOSFfile("https://osf.io/d3mpe/")
subjects<-read.spss(file,to.data.frame=T)

 
##@@ DATA MANIPULATION @@##
  #@ NOTE: Include here ALL difference between OSF data and data used in analysis
  #@ TIP: You will want to learn all about dplyr for manipulating data.


#create dataframes (item/subjects * colour naming/object naming)
  #SUBJECTS= data per naming task ( colour & object )
  SUB.obj<- subset(subjects,NamingTask!="colour") 
  
  #Go to long format
  sub.obj<-gather(SUB.obj,condition, score, congruent_mean:incongruent_mean)
  
##@@ DATA ANLAYSIS @@##
  #@ NOTE: Include a print or sumarry call on the resulting object
  
  

  #object naming task (subjects):
  result_so<-t.test(score~condition,data=sub.obj,paired=T) 
  print(result_so)
  #same as reported=t1 (11)= 1.9, p= 0.09

  
  ##@@ STATISTIC @@##
  result_so$statistic
  
  ##@@ P-VALUE @@##
  result_so$p.value
  
  ##@@ SAMPLE SIZE @@##
  nrow(subjects)/2
  
  ##@@ EFFECT SIZE @@##
  result_so$statistic/sqrt(12)
  
  ##@@ AGREEMENT WITH AUTHORS @@##
  TRUE
  
  #@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---