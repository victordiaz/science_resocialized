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
#@ Study Title: "Temporal selection is supressed"
#@ Coder name: Milan Valasek
#@ Coder e-mail: mivalek@gmail.com
#@ Type of statistic: F
#@ Type of effect-size: N/A
#@ OSF link project: https://osf.io/rzjvn/
#@ OSF link replication report: https://osf.io/jupew/
#
##@@ REQUIRED PACKAGES @@##

library("car")
library("heplots")
library("httr")
library("RCurl")
library("reshape2")
library("xlsx")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function


##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
file <- getOSFfile('https://osf.io/5fdvw', scanMethod = 'httr')

## replicated data
df <- read.xlsx(file, 1, startRow = 5,
                colIndex = c(7:11), colClasses = "numeric")

## original Vul et al. data
df2 <- read.xlsx(file, 1, startRow = 5,
                 colIndex = c(1:5), colClasses = "numeric")


  ##@@ DATA MANIPULATION @@##
  #@ NOTE: Include here ALL differences between OSF data and data used in analysis
  #@ TIP: You will want to learn all about dplyr for manipulating data.

  for (i in 2:ncol(df)) {
    df[ ,i] <- factor(df[ ,i])
  }

  for (i in 2:ncol(df2)) {
    df2[ ,i] <- factor(df2[ ,i])
  }
  

  ##@@ DATA ANLAYSIS @@##
  #@ NOTE: Include a print or summary call on the resulting object

  # between-subject ANOVA
  m1 <- lm(temporal.selection ~ efficacy*latency*precision, data = df)
  Anova(m1, test.statistic = "F")

  # Vul et al. data
  m2 <- lm(temporal.selection ~ efficacy*latency*precision, data = df2)
  Anova(m2, test.statistic = "F")


  ##@@ STATISTIC @@##
  round(Anova(m1, test.statistic = "F")[7,][[3]], 3)

  ##@@ P-VALUE @@##
  Anova(m1, test.statistic = "F")[7,][[4]]

  ##@@ SAMPLE SIZE @@##
  length(unique(df$subject))

  ##@@ EFFECT SIZE @@##
  # partial eta^2
  # NOT ORIGINALLY REPORTED by replicators
  round(etasq(m1)[[1]][7], 3)

  ##@@ AGREEMENT WITH AUTHORS @@##
  TRUE

  #@ Reason disagreement: N/A