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
#@ Study Title: Ganor-Stern (Across-notation automatic numerical processing)
#@ Coder name: David Dobolyi
#@ Coder e-mail: ddobolyi@virginia.edu
#@ Type of statistic: repeated measures ANOVA
#@ Type of effect-size: partial eta squared
#@ OSF link project: https://osf.io/vmipw/
#@ OSF link replication report: https://osf.io/7mgwh/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("ez") # needed for repeated measures anova
library("car") # needed for recode function (data organization)
library("doBy") # needed for data manipulation
library("reshape2") # needed for data manipulation
library("schoRsch") # compute p-eta-sq automatically
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

dat <- read.csv(getOSFfile("https://osf.io/rwusn/")) # please upload and add Numerical_task.csv here
participantOrder <- read.csv(getOSFfile("https://osf.io/hcg5m/")) # please upload and add Order.csv here

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL differences between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

# merge dataset with participant order
fullDat <- merge(dat, participantOrder, by="participant")

# clean up dataset
str(fullDat)
fullDat$participant <- factor(fullDat$participant)

# recode factors of interest using Codes.docx
fullDat$Notation <- factor(recode(fullDat$Notation, "'1'='Arabic'; '2'='Indian'; '3'='Mixed'"))
fullDat$Distance <- factor(recode(fullDat$Distance, "'1'='Small'; '2'='Large'; '0'='Same'"))
fullDat$Order <- factor(fullDat$Order)
str(fullDat)

# remove distance of "same" since we only want small/large
finalDat <- subset(fullDat, Distance != "Same")

# remove RT outliers mentioned in replication report
finalDat <- subset(finalDat, !(RT < 200) & !(RT > 2500))

# remove observations based on filter in Codes.docx (some not described in replication report, e.g., removal of P 24)
# Filter= RT < 2500 & RT > 200 & participant ~= 24 & Distraction ~= 1 & Distance ~= 0 (FILTER)
# note that RT outlier removal and Distance removal (of "Same") was done on the prior two lines

finalDat <- subset(finalDat, participant != 24)
finalDat <- subset(finalDat, Distraction != 1)

# final cleanup of data types
str(finalDat)
finalDat$Participant <- factor(finalDat$participant)
finalDat$Distance <- factor(finalDat$Distance)
str(finalDat)

# collapse RT means for analysis
anovaDat <- summaryBy(RT ~ Order + Participant + Notation + Distance, data=finalDat)
#write.csv(anovaDat, "auditData.csv", row.names=FALSE)

##@@ DATA ANALYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object

# check descriptives

# RT ranged (none should be below 200 or above 2500)
range(finalDat$RT)

# cell means (descriptives) for main effect of Distance
summaryBy(RT.mean ~ Distance, data=anovaDat)

# cell means (descriptives) for main effect of Notation
summaryBy(RT.mean ~ Notation, data=anovaDat)

(threeWay <- ezANOVA(
    data = anovaDat
    , dv = RT.mean
    , wid = Participant
    , within = .(Notation, Distance)
    , between = Order
    , detailed = TRUE
    , return_aov = TRUE
    , type = 3
))

result <- anova_out(threeWay, print=TRUE)

##@@ STATISTIC @@##
round(threeWay$ANOVA$F[4],2)

##@@ P-VALUE @@##
round(threeWay$ANOVA$p[4],2)
  
##@@ SAMPLE SIZE @@##
length(unique(anovaDat$Participant)) # note we are missing one from the replication report n of 32 (i.e., missing participant id #24), who was noted as being dropped in Codes.docx

##@@ EFFECT SIZE @@##
result[[1]][4,7] # using package schoRsch
# 
# # alternatively
# round(summary(threeWay$aov)$"Error: Participant:Distance"[[1]]$"Sum Sq"[1]/(summary(threeWay$aov)$"Error: Participant:Distance"[[1]]$"Sum Sq"[1] + summary(threeWay$aov)$"Error: Participant:Distance"[[1]]$"Sum Sq"[3]),2)
# # above matches with author, given rounding
  
##@@ AGREEMENT WITH AUTHORS @@##
TRUE
  
#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---
