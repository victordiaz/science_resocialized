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
#@ Study Title: Replication of The Effects of an Implemental Mind-set on Attitude Strength by Henderson, de Liver, & Gollwitzer (2008, Journal of Personality and Social Psychology) 
#@ Coder name: Julian Mestwerdt
#@ Coder e-mail: julian.mestwerdt@gmail.com
#@ Type of statistic: F
#@ Type of effect-size: Partial eta squared
#@ OSF link project: https://osf.io/79dey/
#@ OSF link replication report: https://osf.io/cjr7d/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
File <- getOSFfile("https://osf.io/3xv8u/")
Data <- read.delim(File, header=TRUE, skip=3)

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
Data <- Data[Data$Include==1,] # Excluding cases
Data$Indecisive <- as.numeric(as.character(Data$Indecisive))
Data$Condition  <- as.factor(Data$Condition)

Data$NotTorn     <- Data$NotTorn*-1   # Reverse code item 2
Data$Indecisive  <- Data$Indecisive-4 # Equating the scoring of item 3 (1 to 7) to 
                                      # the scoring of item 1 & 2 (-3 to 3) 

Data$value <- (Data$StrongMixed + Data$NotTorn + Data$Indecisive)/3
# Creating the ambivalence score, based on the mean of item 1 to 3                                                             

Data[49,33] <- (Data[49,22]+Data[49,22])/2
# This participant did not provide an answer for item 3.
# The ambivalence score for this participant is calculated to be the mean of item 1 & 2.

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object
Results <- aov(value ~ Condition, data=Data)
summary(Results)

##@@ STATISTIC @@##
summary(Results)[[1]][["F value"]][[1]]

##@@ P-VALUE @@##
summary(Results)[[1]][["Pr(>F)"]][[1]]

##@@ SAMPLE SIZE @@##
nrow(Data)

##@@ EFFECT SIZE @@##
SumSq_effect <- summary(Results)[[1]][["Sum Sq"]][1]
SumSq_error <- summary(Results)[[1]][["Sum Sq"]][2]
SumSq_effect / (SumSq_effect + SumSq_error)

##@@ AGREEMENT WITH AUTHORS @@##
TRUE
