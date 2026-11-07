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
#@ Study Title: The effect of global versus local processing styles on assimilation versus contrast in social judgment.
#@ Coder name: Johnny van Doorn
#@ Coder e-mail: Johnnydoorn@gmail.com
#@ Type of statistic: F
#@ Type of effect-size: Partial Eta Squared
#@ OSF link project: https://osf.io/mxryb/
#@ OSF link replication report: https://osf.io/sxnu6/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("car")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
dir <- getOSFfile('https://osf.io/m65gx/')


# Read files:
data <- read.csv(dir)

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
data2<- data[1:15,]
data2<- rbind(data2,data[17:22,])
data2<- rbind(data2,data[24:67,])
data2<- rbind(data2,data[69:74,])
data<-data2 # This is the data used by the replicator eventually, participants that suspected
            # the setup of the experiment were excluded

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object
aov <- aov(aggressivenessScore ~ mapCondition*puzzleCondition, data)
analysis <- Anova(aov, type = "II")
print(analysis)
##@@ STATISTIC @@##
analysis$F[3]
##@@ P-VALUE @@##
analysis$Pr[3]

##@@ SAMPLE SIZE @@##
length(unique(data$PID))
##@@ EFFECT SIZE @@##
SumSq_effect <- analysis$Sum[3]
SumSq_error <- analysis$Sum[4]
Effect_size <- SumSq_effect / (SumSq_effect + SumSq_error) # Partial Eta Squared for the interaction
print(Effect_size)
##@@ AGREEMENT WITH AUTHORS @@##
TRUE  
#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---