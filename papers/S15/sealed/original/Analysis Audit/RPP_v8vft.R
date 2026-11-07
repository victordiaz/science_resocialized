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
#@ Study Title: ---Selective exposure and information quantity: how different information quantities moderate decision makers' preference for consistent and inconsistent information--
#@ Coder name: ---Bobby den Bezemer---
#@ Coder e-mail: ---bobbydenbezemer@gmail.com---
#@ Type of statistic: ---chi square---
#@ Type of effect-size: ---Cohen's d---
#@ OSF link project: ---https://osf.io/v8vft/---
#@ OSF link replication report: ---https://osf.io/5afur/---
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
library("sas7bdat")
library("dplyr")
library("gmodels")
library("effsize")

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
Data <- getOSFfile("https://osf.io/c9z3d/")
Dataset <- read.sas7bdat(Data) 
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL differences between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
# Filter out participants that did not know answer to the primary dependent variable
excluded <- c(1901775, 1902268, 1902419, 1903277, 1903508, 1903545, 1903573,
              1903817, 1904356, 1904722, 1904780, 1904834, 1905222, 1905269,
              1905391, 1905498, 1906500, 1907320, 1907839, 1907960, 1908232,
              1908540, 1908556, 1908581, 1908720, 1909591, 1909951)
Dataset <- Dataset[!Dataset$X_session_id %in% excluded, ]

# the main statistic is calculated only on control condition participants
Dataset <- Dataset %>%
  filter(focus == "control")
  
##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object
# Note that the authors have taken the Pearson chi-squared test without Yates correction
output <- CrossTable(Dataset$options, Dataset$decision, chisq = TRUE,
                     prop.t = FALSE, prop.c = FALSE, prop.chisq = FALSE)
print(output)
  
##@@ STATISTIC @@##
output$chisq[[1]]
  
##@@ P-VALUE @@##
output$chisq[[3]]
  
##@@ SAMPLE SIZE @@##
nrow(Dataset)
  
##@@ EFFECT SIZE @@##
cor = sqrt(7.095 / 150)
cohen_d = (2 * cor) / (1 - cor^2)

##@@ AGREEMENT WITH AUTHORS @@##
TRUE
  
 #@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---