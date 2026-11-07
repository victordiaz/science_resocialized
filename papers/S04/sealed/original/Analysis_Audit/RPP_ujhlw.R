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
#@ Study Title: Multidimensional Visual Statistical Learning. 
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: t test
#@ Type of effect-size: Cohen's D
#@ OSF link project: https://osf.io/ujhlw/
#@ OSF link replication report: https://osf.io/ktnmc/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("R.matlab")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

#Data available in MATLAB .mat format
#Function to extract relevant information
ext_info <- function(i, s.list){
  
  x <- data.frame(cbind(i, unlist(s.list[[1]][[1]]), unlist(s.list[[1]][[4]])))
  names(x) <- c("subject", "correct", "type")
  return(x)
}

zip <- getOSFfile("https://osf.io/mfeq5/")

dir <- "TurkFiles"
unzip(zip, exdir = dir)

#Data files are matlab mat files and so use R.matlab package
file_list <- list.files(dir, pattern = "\\.mat", full.names = TRUE)
data <- do.call("rbind",lapply(file_list,FUN=function(files) {
  (ext_info(files, readMat(files)))
}))



##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

#ext_info returns data as factors so transform correct to numeric (0 - incorrect, 1 - correct)
data <- transform(data, correct=as.numeric(correct)-1)

p.cor <- with(data[data$type=="real",], tapply(correct, subject, mean, na.rm=TRUE))


##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

#Paired t-test between RTs for correct rejections and RTs for misses
turk.t.test <- t.test( p.cor, mu = 0.5, alternative="two.sided") 
print(turk.t.test)

##@@ STATISTIC @@##
turk.t.test$statistic 

##@@ P-VALUE @@##
turk.t.test$p.value

##@@ SAMPLE SIZE @@##
nrow(p.cor)

##@@ EFFECT SIZE @@##
t = turk.t.test$statistic
n = nrow(p.cor)

#For one sample t-test (from Lakens2013)
efd = t/sqrt(n)
print(efd)

##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---