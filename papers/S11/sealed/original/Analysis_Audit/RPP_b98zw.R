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
#@ Study Title: Replication of "Where do we look during potentially offensive behavior?"
#@ Coder name: Julian Mestwerdt
#@ Coder e-mail: julian.mestwerdt@gmail.com
#@ Type of statistic: F
#@ Type of effect-size: Partial eta squared
#@ OSF link project: https://osf.io/b98zw/
#@ OSF link replication report: https://osf.io/nkaw4/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
library("ez")

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
File <- getOSFfile("https://osf.io/mkyvt/")
Data <- read.table(File, header=TRUE, fill=TRUE)
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL differences between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
Data$Subject <- 1:30
Data$Subject <- as.factor(Data$Subject)
Data$Discussant <- as.factor(Data$Discussant)
Data$Condi <- as.factor(Data$Condi)

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object
res <- ezANOVA(data=Data
               , dv=Looktime
               , wid=Subject
               , within=Discussant
               , between=Condi
               , type=2
               , detailed=TRUE
  )
print(res)

##@@ STATISTIC @@##
res$ANOVA[[6]][[4]]

##@@ P-VALUE @@##
res[["Sphericity Corrections"]][[3]][[2]]

##@@ SAMPLE SIZE @@##
nrow(Data)/4

##@@ EFFECT SIZE @@##
SumSq_effect <- res$ANOVA[[4]][[4]]
SumSq_error <- res$ANOVA[[5]][[4]]
SumSq_effect / (SumSq_effect + SumSq_error)
  
##@@ AGREEMENT WITH AUTHORS @@##
TRUE
  