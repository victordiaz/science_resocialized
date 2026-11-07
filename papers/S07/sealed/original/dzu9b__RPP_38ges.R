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
#@ Study Title: Decision making and learning while taking sequential risks
#@ Coder name: Sacha Epskamp
#@ Coder e-mail: sacha.epskamp@gmail.com
#@ Type of statistic: z
#@ Type of effect-size: NA
#@ OSF link project: https://osf.io/38ges/
#@ OSF link replication report: https://osf.io/gyn9e/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
library("haven")

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
zipFile <- getOSFfile("https://osf.io/7xzkb/")
unzip(zipFile, exdir = Dir <- tempdir())
Data <- read_dta(paste0(Dir,"/table6data.dta"))

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL differences between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
# Remove NA:
Data <- subset(Data,!is.na(polydrug))

  
##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object
# Following Meng, Rosenthal & Rubin (1992)

fisher <- function(r) 1/2 * log((1+r)/(1-r))
N <- nrow(Data)
cors <- cor(Data$polydrug,Data[c("KS", "KC", "RS", "RC")])
corsX <- cor(Data[c("KS", "KC", "RS", "RC")])
lambda <- c(1,-1,1,-1)
zs <- fisher(cors)
rx <- median(corsX[upper.tri(corsX)])
f <- (1-rx) / (2 * (1 - mean(cors^2)))
h <- (1-f*mean(cors^2)) / (1 - mean(cors^2))

Z <- sum(lambda * zs) * sqrt( (N-3) / (sum(lambda^2)* (1 - rx) * h))
print(2*pnorm(Z,lower.tail = FALSE))


##@@ STATISTIC @@##
Z

##@@ P-VALUE @@##
2*pnorm(Z,lower.tail = FALSE)

##@@ SAMPLE SIZE @@##
N

##@@ EFFECT SIZE @@##
NA
  
##@@ AGREEMENT WITH AUTHORS @@##
TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---