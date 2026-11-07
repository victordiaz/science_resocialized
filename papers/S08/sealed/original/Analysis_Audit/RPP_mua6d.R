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
#@ Study Title: Self-handicapping, excuse making, and counterfactual thinking: Consequences for self-esteem and future motivation.
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: t test
#@ Type of effect-size: Cohen's D
#@ OSF link project: https://osf.io/mua6d/
#@ OSF link replication report: https://osf.io/g9sxb/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("compute.es")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
#Down,load csv data file
file <- getOSFfile("https://osf.io/dy3zn/")
mcdata <- read.csv(file, as.is=TRUE) 

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

#Convert to factor and add labels
mcdata$Cond <- factor(mcdata$Cond)
levels(mcdata$Cond) <- c("Handicap", "Control")

#Analysis in replication asks one tailed hypothesis is Control greater than Handicap
#Use Control as reference level to get direction in accord with replication
mcdata$Cond <- relevel(mcdata$Cond, ref="Control")

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

#One tailed t-test Control greater than handicap, equal variance assumed
mct.test <- t.test(Correct/Attempted ~ Cond, data=mcdata, alternative="greater",var.equal=TRUE)
print(mct.test)

##@@ STATISTIC @@##
mct.test$statistic 

##@@ P-VALUE @@##
mct.test$p.value

##@@ SAMPLE SIZE @@##
nrow(mcdata)

##@@ EFFECT SIZE @@##
t = mct.test$statistic
n = nrow(mcdata)
efd = t/sqrt(n)

effectSize <- des(efd, n.1=n, n.2=n, level=95, dig=2, id=NULL, data=NULL)
effectSize$d  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---