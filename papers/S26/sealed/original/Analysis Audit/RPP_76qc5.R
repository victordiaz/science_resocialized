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
#@ Study Title: 'In-Group Love' and 'Out-Group Hate' as Motives for Individual Participation in Intergroup Conflict: A New Game Paradigm
#@ Coder name: Bobby den Bezemer
#@ Coder e-mail: bobbydenbezemer@gmail.com
#@ Type of statistic: F statistic
#@ Type of effect-size: Partial eta squared
#@ OSF link project: https://osf.io/76qc5/
#@ OSF link replication report: https://osf.io/sjwcd/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
library("foreign")
library("dplyr")

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
File <- getOSFfile("https://osf.io/m3b7k/")
Data <- read.spss(File, to.data.frame = TRUE)
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

# using dplyr to group the dataframe and then summarise it by the mean value
# of a groups contributions to the between group pool
Data_edited <- Data %>%
  dplyr::group_by(Group_Num, Condition_Game, Condition_Communication) %>%
  dplyr::summarise(GivePool_B = mean(GivePool_B))
  
##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

# Do an anova with as independent variables, game type, communication and their interaction
Result <- aov(GivePool_B ~ Condition_Game*Condition_Communication, data= Data_edited)
summary(Result)  
  
##@@ STATISTIC @@##
summary(Result)[[1]][["F value"]][1]
  
##@@ P-VALUE @@##
summary(Result)[[1]][["Pr(>F)"]][1]
  
##@@ SAMPLE SIZE @@##
nrow(Data_edited)
  
##@@ EFFECT SIZE @@##

# get the sum of squares for the effect
SS_effect <- summary(Result)[[1]][["Sum Sq"]][1]
# get the error sum of squares
SS_error <- summary(Result)[[1]][["Sum Sq"]][4]
# fill out the formula for the partial_eta_squared
partial_eta_squared = SS_effect / (SS_effect + SS_error)   

##@@ AGREEMENT WITH AUTHORS @@##
TRUE
  
#@ Reason disagreement: