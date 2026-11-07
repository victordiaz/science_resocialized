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
#@ Study Title: 
#@ Coder name: Jolanda Kossakowski
#@ Coder e-mail: jolanda.kossakowski@student.uva.nl
#@ Type of statistic: F-value
#@ Type of effect-size: Partial eta-squared
#@ OSF link project: https://osf.io/p9thw/
#@ OSF link replication report: https://osf.io/a5ukz/
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

File <- getOSFfile("https://osf.io/4xs8w/")
data <- read.spss(File, to.data.frame = TRUE)


##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

# Subset only the needed variables
data_wide <- data[,c(1,7,8,9,10,18)]

# Transform dataset to long format

data_long <- melt(data_wide, id.vars = c("Code", "Group"))
colnames(data_long) <- c("Code", "Group", "Lag", "Correct")


##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

res <- ezANOVA(data = data_long, dv = .(Correct), between = .(Group), within = .(Lag), wid = .(Code), type = 3, detailed = TRUE)

res

# DF correction because sphericity is not met

DF1 <- res$ANOVA$DFn[4] * res$`Sphericity Corrections`[[2]][2]
DF2 <- res$ANOVA$DFd[4] * res$`Sphericity Corrections`[[2]][2]

##@@ STATISTIC @@##

res$ANOVA$F[4]

##@@ P-VALUE @@##

res$ANOVA$p[4]

##@@ SAMPLE SIZE @@##

nrow(data_wide)

##@@ EFFECT SIZE @@##

# Partial eta squared

res$ANOVA$SSn[4] / (res$ANOVA$SSn[4] + res$ANOVA$SSd[4])

##@@ AGREEMENT WITH AUTHORS @@##
TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---

