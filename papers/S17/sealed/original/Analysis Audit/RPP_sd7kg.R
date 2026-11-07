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
#@ Detecting the Snake in the Grass. Attention to Fear-Relevant Stimuli by Adults and Young Children.
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: F
#@ Type of effect-size: f
#@ OSF link project: https://osf.io/sd7kg/
#@ OSF link replication report: https://osf.io/5ygej/
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

file <- getOSFfile("https://osf.io/nd7we/")
lobue.data <- read.spss(file, to.data.frame=TRUE) 

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.


##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

#ANOVA for critical interaction (2-way) two-way between subjects model
# R uses type 1 sum of squares (SS) for aov, SPSS uses type 3 sum of squares (SS)
# Check for differences, but should be same as interaction term entered last in R  

options(contrasts=c("contr.sum", "contr.poly"))
lobue.aov <- aov(average ~ parentvschild * Stim_cond , data=lobue.data)
summary(lobue.aov)

#as Type 3 SS for SPSS
lobue.aovss3 <- drop1(lobue.aov, ~., test="F")
print(lobue.aovss3)

#Here SS for interaction term is the same. 

##@@ STATISTIC @@##
lobue.aovss3[["F value"]][[4]] 

##@@ P-VALUE @@##
lobue.aovss3[["Pr(>F)"]][[4]]

##@@ SAMPLE SIZE @@##
nrow(lobue.data)

##@@ EFFECT SIZE @@##
sumsq.error <- lobue.aovss3[["RSS"]][[1]]
sumsq.effect <- lobue.aovss3[["Sum of Sq"]][[4]]

effect.size <- sumsq.effect / (sumsq.effect + sumsq.error)
print(effect.size)  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---