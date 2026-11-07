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
#@ Study Title: A needs-based model of reconciliation: satisfying the differential 
##              emotional needs of victim and perpetrator as a key to promoting reconciliation.
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: F
#@ Type of effect-size: partial eta squared
#@ OSF link project: https://osf.io/xse7q/
#@ OSF link replication report: https://osf.io/xse7q/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("foreign")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

#Data available in SPSS .sav format

file <- getOSFfile("https://osf.io/8y94x/")
shn.data <- read.spss(file, to.data.frame=TRUE) 


##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

#Check ParticipantNumber is a factor
shn.data <- transform(shn.data, ParticipantNumber=factor(ParticipantNumber))


##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object

#Target analyis is 2 x 2 between subjects for Role (Victim or Perpetrator) vs Message (Accept or Empower)
# at time-point 2

shn.aov1 = aov(AvgWillingReconcileTime2 ~ VictimOrPerpV0P1*AcceptOrEmpowerA0E1 + Error(ParticipantNumber),  data=shn.data)
summ.shn.aov1 <- summary(shn.aov1)
print(summ.shn.aov1)

# As balanced ANOVA, type 1 Sum of Squares will be same as type 3 Sum of Squares. 

##@@ STATISTIC @@##
#F from interaction term
summ.shn.aov1[["Error: ParticipantNumber"]][[1]][["F value"]][[3]]

##@@ P-VALUE @@##
summ.shn.aov1[["Error: ParticipantNumber"]][[1]][["Pr(>F)"]][[3]]

##@@ SAMPLE SIZE @@##
#Ignoring missing data
nrow(shn.data[which(!(is.na(shn.data$AvgWillingReconcileTime2))),])

##@@ EFFECT SIZE @@##
sumsq.error <- summ.shn.aov1[["Error: ParticipantNumber"]][[1]][["Sum Sq"]][[4]]
sumsq.effect <- summ.shn.aov1[["Error: ParticipantNumber"]][[1]][["Sum Sq"]][[3]]

effect.size <- sumsq.effect / (sumsq.effect + sumsq.error)
print(effect.size)  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---