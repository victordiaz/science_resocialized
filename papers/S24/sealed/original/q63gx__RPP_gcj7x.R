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
#@ Study Title: How to say no: Single-and dual-process theories of short-term recognition tested on negative probes
#@ Coder name: Jolanda Kossakowski
#@ Coder e-mail: jolanda.kossakowski@student.uva.nl
#@ Type of statistic: F-value
#@ Type of effect-size: Partial eta-squared
#@ OSF link project: https://osf.io/gcj7x/
#@ OSF link replication report: NA
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("foreign")
library("ez")
library("reshape2")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

File <- getOSFfile("https://osf.io/n87dw/")
data_wide <- read.spss(File, to.data.frame = TRUE)


##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

# Transform data to long format
data <- melt(data_wide, id.vars = c("subject", "listtype"))
colnames(data) <- c("subject", "listtype", "condition", "reactiontime")

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

res <- ezANOVA(data = data, dv = .(reactiontime), between = .(listtype), within = .(condition), wid =.(subject), type = 3, detailed = TRUE)

res

##@@ STATISTIC @@##

res$ANOVA$F[2]

##@@ P-VALUE @@##

res$ANOVA$p[2]

##@@ SAMPLE SIZE @@##

nrow(data_wide)

##@@ EFFECT SIZE @@##

# Partial eta squared

res$ANOVA$SSn[2] / (res$ANOVA$SSn[2] + res$ANOVA$SSd[2])

##@@ AGREEMENT WITH AUTHORS @@##
TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---
