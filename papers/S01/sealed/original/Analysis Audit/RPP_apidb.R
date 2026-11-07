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
#@ Study Title: With a clean conscience: Cleanliness reduces the severity of moral judgments
#@ Coder name: Simon Columbus
#@ Coder e-mail: simon@simoncolumbus.com
#@ Type of statistic: F-statistic
#@ Type of effect-size: Cohen's d
#@ OSF link project: https://osf.io/apidb/
#@ OSF link replication report: https://osf.io/2dem3/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
library("foreign")
library("lsr")
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

File <- getOSFfile('https://osf.io/qghwy/')
Data <- read.spss(File, to.data.frame=TRUE)

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

# Create single variable for exclusion of participants 
# Exclude participants who made up answers or due to experimenter error

Data$Exclude <- as.numeric(Data$Madeup_dummy)
Data[Data$Exclude==0,60] <- as.numeric(Data[Data$Exclude==0,]$Exp_Error)

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

Result <- aov(mean_vignettes ~ Condition, data=Data[Data$Exclude==0,])  
summary(Result)
  
##@@ STATISTIC @@##

summary(Result)[[1]][["F value"]][1]

##@@ P-VALUE @@##

summary(Result)[[1]][["Pr(>F)"]][1]

##@@ SAMPLE SIZE @@##

nrow(Data[Data$Exclude==0,])

##@@ EFFECT SIZE @@##

cohensD(mean_vignettes ~ Condition, data=Data[Data$Exclude==0,])

##@@ AGREEMENT WITH AUTHORS @@##

TRUE
  
#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---
