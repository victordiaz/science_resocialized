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
#@ Study Title: Perceptual mechanisms that characterize gender differences in decoding women's sexual intent
#@ Coder name: Simon Columbus
#@ Coder e-mail: simon@simoncolumbus.com
#@ Type of statistic: F
#@ Type of effect-size: partial eta squared
#@ OSF link project: https://osf.io/7dyp5/
#@ OSF link replication report: https://osf.io/5u4km/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
library("foreign")
library("reshape2")
library("ez")  

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

File <- getOSFfile("https://osf.io/evcbi/")
Data <- read.spss(File, to.data.frame=TRUE)

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

## Reshape to long format for within-subjects analysis

Data.1 <- melt(Data, measure.vars=c(22:23), variable.name="Condition")

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

fit <- ezANOVA(Data.1, dv=value, wid=ID, within=Condition, between=Gender)
fit  

##@@ STATISTIC @@##

fit$ANOVA[3,4]

##@@ P-VALUE @@##

fit$ANOVA[3,5]
  
##@@ SAMPLE SIZE @@##

length(unique(Data.1$ID))

##@@ EFFECT SIZE @@##

(fit$ANOVA[3,4]*1)/(fit$ANOVA[3,4]*fit$ANOVA[3,2]+fit$ANOVA[3,3])
  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE
  
#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---