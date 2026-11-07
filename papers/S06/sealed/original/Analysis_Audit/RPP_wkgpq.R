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
#@ Study Title: Individual differences in the regulation of intergroup bias
#@ Coder name: Bobby den Bezemer
#@ Coder e-mail: bobbydenbezemer@gmail.com
#@ Type of statistic: F statistic
#@ Type of effect-size: partial eta squared
#@ OSF link project: https://osf.io/wkgpq/
#@ OSF link replication report: https://osf.io/ysxmf/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
File <- getOSFfile("https://osf.io/xdzas/")
Data <- read.csv(File)
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

# as we're going to use a mixed model anova with 1 within subjects variable,
# ID variable needs to be a factor
Data$ID <- as.factor(Data$ID)
  
##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

# Do a mixed model anova with as HiLoCat, Task and their interaction
# and include errors as they are not independent.
Results <- aov(PD ~ HiLoCat * Task + Error(ID / Task), data = Data)
summary(Results)  

##@@ STATISTIC @@##
summary(Results)[[2]][[1]][["F value"]][[2]]

##@@ P-VALUE @@##
summary(Results)[[2]][[1]][["Pr(>F)"]][[2]]
  
##@@ SAMPLE SIZE @@##
# only the unique participant numbers, otherwise you get duplicates
length(unique(Data$ID))
  
##@@ EFFECT SIZE @@##

# get the sum of squares for the effect
SS_effect <- summary(Results)[[2]][[1]][["Sum Sq"]][2]
# get the error sum of squares
SS_error <- summary(Results)[[2]][[1]][["Sum Sq"]][3]
# fill out the formula for the partial_eta_squared
partial_eta_squared = SS_effect / (SS_effect + SS_error) 
  
##@@ AGREEMENT WITH AUTHORS @@##
TRUE
  
#@ Reason disagreement: 