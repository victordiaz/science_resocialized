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
#@ Study Title: Alvarez (Representation of simple ensemble visual features)
#@ Coder name: David Dobolyi
#@ Coder e-mail: ddobolyi@virginia.edu
#@ Type of statistic: pairwise t-test
#@ Type of effect-size: Cohen's d
#@ OSF link project: https://osf.io/dnaxe/
#@ OSF link replication report: https://osf.io/dm2kj/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("readstata13") # read STATA data file
library("doBy") # organize data
library("lsr") # compute Cohen's d another way
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
rawDat <- getOSFfile("https://osf.io/d5im2/")
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
dat <- read.dta13(rawDat)

# structure data
str(dat)
dat$subject <- factor(dat$subject)
dat$ExGuess <- factor(dat$ExGuess)

# examine grouping factors
unique(dat$one_vs_four) # needed to identify centroid trials
unique(dat$tar_vs_dis) # target vs. distractor (where NA is guessing)

datCentroid <- dat[!(dat$one_vs_four %in% 1),] # centroid data
datCentroidDistractors <- datCentroid[!(datCentroid$tar_vs_dis %in% 1),] # distractors and guessing within centroid trials

angleMeans <- summaryBy(angle ~ subject + ExGuess + tar_vs_dis, FUN = mean, data = datCentroidDistractors) # compute the angle means within subject for the pairwise t-test (note: I have reservations about computing within subject means for a t-test; this makes assumptions about the distributions of trials within Ps being normal--a more powerful approach would be to maintain the raw data by applying a mixed model design, where trial by trial variations in angle can be explored within a random effect of subject for example)

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object
(centroidDistractorsVersusChance <- t.test(subset(angleMeans, ExGuess == "experimental")$angle.mean, subset(angleMeans, ExGuess == "guessing")$angle.mean, paired=TRUE)) # pairwise t-test on experimental vs. guessing angle means
# str(centroidDistractorsVersusChance)

##@@ STATISTIC @@##
(tVal <- centroidDistractorsVersusChance$statistic)

##@@ P-VALUE @@##
centroidDistractorsVersusChance$p.value
  
##@@ SAMPLE SIZE @@##
(n <- length(unique(dat$subject)))

##@@ EFFECT SIZE @@##
abs(as.numeric(tVal/sqrt(n)))
# alternatively, using the lsr package #
cohensD(subset(angleMeans, ExGuess == "experimental")$angle.mean, subset(angleMeans, ExGuess == "guessing")$angle.mean, method="paired")
  
##@@ AGREEMENT WITH AUTHORS @@##
TRUE
  
#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---