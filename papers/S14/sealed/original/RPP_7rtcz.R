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
#@ Study Title: Replication of JE Marsh, F Vachon, DM Jones (2008, JEPLMC 34(1))
#@ Coder name: Sarah Thomas
#@ Coder e-mail: slt4bg@virginia.edu
#@ Type of statistic: F from mixed ANOVA
#@ Type of effect-size: eta squared
#@ OSF link project: https://osf.io/7rtcz/
#@ OSF link replication report: https://osf.io/sqcwk/

##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("reshape2")
library("foreign")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
Rawdat<-getOSFfile("https://osf.io/sue7q/")
dat <- read.spss(Rawdat,use.value.labels = FALSE, to.data.frame=TRUE)

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
  
#Get data in long format
# Sound 1- R_QUIET
# Sound 2- R_DISSIMILAR
# Sound 3- R_SIMILAR
  
longdat <- melt(dat, 
               id.vars = c("NUMBER","AGE", "SEX", "LANG","TASK"), # Between subject variables
               measure.vars = c("R_QUIET", "R_DISSIMILAR", "R_SIMILAR"), # Variables to gather
               variable.name = "SOUND", # Name of within subjects variable
               value.name = "RT") # Name of dependent variable)
longdat$NUMBER<-as.factor(longdat$NUMBER)

##@@ DATA ANALYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object
mymodel<-aov(data=longdat,  RT ~  1 + SOUND + SOUND*TASK + TASK + Error(NUMBER/SOUND))
summary(mymodel) 

##@@ STATISTIC @@##
summary(mymodel)[["Error: NUMBER:SOUND"]][[1]]$F[2]

##@@ P-VALUE @@##
summary(mymodel)[["Error: NUMBER:SOUND"]][[1]]$P[2]

##@@ SAMPLE SIZE @@##
nrow(dat)

##@@ EFFECT SIZE @@##
# Eta squared
(summary(mymodel)[["Error: NUMBER:SOUND"]][[1]][["Sum Sq"]][2])/
sum(summary(mymodel)[["Error: NUMBER:SOUND"]][[1]][["Sum Sq"]][1],
summary(mymodel)[["Error: NUMBER:SOUND"]][[1]][["Sum Sq"]][2],
summary(mymodel)[["Error: NUMBER:SOUND"]][[1]][["Sum Sq"]][3])

##@@ AGREEMENT WITH AUTHORS @@##
TRUE

#@ Reason disagreement: 
