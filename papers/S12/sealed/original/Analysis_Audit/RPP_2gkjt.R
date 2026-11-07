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
#@ Study Title: Replication of Ratliff (Ranganath) & Nosek, 2008, Psych Science
#@ Coder name: Pia Tio
#@ Coder e-mail: piatio@gmail.com
#@ Type of statistic: t-statistic
#@ Type of effect-size: not calculated
#@ OSF link project: https://osf.io/2gkjt/
#@ OSF link replication report: https://osf.io/9xt25/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
library(Hmisc)

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
  file <- getOSFfile('https://osf.io/8tzep/')
  data <-read.csv(file, header = TRUE)
  fie = data
    
  ##@@ DATA MANIPULATION @@##
  #@ NOTE: Include here ALL differences between OSF data and data used in analysis
  #@ TIP: You will want to learn all about dplyr for manipulating data.
  # now, create the final dataset by excluding everyone who doesn't have a valid score on both measures. 
  nrow(fie)
  fin<-fie[!is.na(fie$exppref),]
  nrow(fin)
  fin<-fin[!is.na(fin$d),]
  nrow(fin)
  fin<-fin[fin$fastpct10==0,]
  nrow(fin)
  fin<-fin[fin$alltrials == 200,]
    
  ##@@ DATA ANLAYSIS @@##
  #@ NOTE: Include a print or summary call on the resulting object
  #here it is! The test of difference between the explicit rating groups
  t_ex<-t.test(fin$exppref[fin$rateorig==0], fin$exppref[fin$rateorig==1])
  print(t_ex)
  # now for implicit preference
  tapply(fin$imppref,  fin$rateorig, psych::describe)
  tapply(fin$imppref,  fin$rateorig, Hmisc::describe)
  t_in<-t.test(fin$imppref[fin$rateorig==0], fin$imppref[fin$rateorig==1])
  print(t_in)
  
  ##@@ STATISTIC @@##
  t_ex$statistic
  t_in$statistic
  
  ##@@ P-VALUE @@##
  t_ex$p.value
  t_in$p.value

  ##@@ SAMPLE SIZE @@##
  nrow(fin)
  
  ##@@ EFFECT SIZE @@##
  #not calculated by authors 
  
  ##@@ AGREEMENT WITH AUTHORS @@##
  TRUE
  
  #@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---