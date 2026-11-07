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
#@ Study Title: Replication of Hajcak & Foti (2008, PS, Study 1)
#@ Coder name: Pia Tio
#@ Coder e-mail: piatio@gmail.com
#@ Type of statistic: t-staistic
#@ Type of effect-size: r
#@ OSF link project: https://osf.io/73pnd/
#@ OSF link replication report: https://osf.io/xaqsf/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
  file <- getOSFfile('https://osf.io/2hgsk/')
  data <-read.csv(file, header = TRUE)
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL differences between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
  #No data manipulation necessary 
  
  ##@@ DATA ANLAYSIS @@##
  #@ NOTE: Include a print or summary call on the resulting object
  Result = cor.test(data[data$startle_type=="error",]$ERN,data[data$startle_type=="error",]$EPS)
  print(Result)

  ##@@ STATISTIC @@##
  Result$statistic
  
  ##@@ P-VALUE @@##
  Result$p.value
  
  ##@@ SAMPLE SIZE @@##
  nrow(data)
  
  ##@@ EFFECT SIZE @@##
  Result$estimate
  
  ##@@ AGREEMENT WITH AUTHORS @@##
  TRUE
  


  #@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---