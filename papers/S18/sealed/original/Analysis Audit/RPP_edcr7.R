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
#@ Nonconscious goal pursuit in novel environments: The case of implicit learning.
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: t test
#@ Type of effect-size: Cohen's D
#@ OSF link project: https://osf.io/edcr7/
#@ OSF link replication report: https://osf.io/x75fq/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("foreign")
library("compute.es")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

#Data available in SPSS .sav format

file <- getOSFfile("https://osf.io/g97uv/")
eitam.data <- read.spss(file, to.data.frame=TRUE) 

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

#Calculate learning from difference between random and fixed sequence blocks

eitam.data$mean.learn <- with(eitam.data,RB12Mean - FSMean)

#Exclude participants from the analysis as detailed in the replication report. Only inlcude
#participants for whom include1 = "Include for analyses". Remove from data frame as number of
#rows is used for n to calculate ES below

eitam.data <- eitam.data[eitam.data$Include1=="Include for analyses", ]

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

#Paired t-test between RTs for correct rejections and RTs for misses
eitam.t.test <- t.test( mean.learn ~ Condition, data=eitam.data, var.equal=TRUE) 
print(eitam.t.test)

##@@ STATISTIC @@##
eitam.t.test$statistic 

##@@ P-VALUE @@##
eitam.t.test$p.value

##@@ SAMPLE SIZE @@##
nrow(eitam.data)

##@@ EFFECT SIZE @@##
t = eitam.t.test$statistic
n = nrow(eitam.data)
efd = t/sqrt(n)

effectSize <- des(efd, n.1=n, n.2=n, level=95, dig=2, id=NULL, data=NULL)
effectSize$d  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---