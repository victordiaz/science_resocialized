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
# Data should be loaded directly from OSF. Try to do this using OSF2R.
# If OSF2R is not installed install it via these codes: 
# install_packages("devtools")
# library("devtools")
# install_github("sachaepskamp/OSF2R")
#
# For any questions, please contact me at sacha.epskamp@gmail.com
#
##@@ GENERAL INFORMATION @@##
#@ Study Title: Modeling Distributions of Immediate Memory Effects: No Strategies Needed?
#@ Coder name: Sacha Epskamp
#@ Coder e-mail: sacha.epskamp@gmail.com
#@ Type of statistic: t-test
#@ Type of effect-size: d
#@ OSF link project: https://osf.io/6n3bm/
#@ OSF link replication report: https://osf.io/a6mje/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
# Download zip file:
zip <- getOSFfile("https://osf.io/srnvg/")

# Unzip to directory:
dir <- "BeamerFiles"
unzip(zip, exdir = dir) 

# Read files:
file_list <- list.files(dir, pattern = "\\.txt", full.names = TRUE)
data <- do.call("rbind",lapply(file_list,FUN=function(files) {
  read.table(files,header=TRUE, sep="\t")
}))
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.
#add demographics manually (copied from original output files for reasons of
# data pre-processing)
dem = data.frame(id = rep(c(1:15), each=80),
                 eng = rep(c(6,6,7,10,6,9,7,8,5,9,8,6,8,9,8),each=80),
                 age = rep(c(20,20,20,19,19,20,19,18,23,19,18,21,20,19,20),each=80),
                 gender = rep(c("f","f","f","f","f","m","f","f","m","f","f","f","f","f","f"),each=80),
                 lang = rep(c(rep("NL", 8), "GER", rep("NL", 6)),each=80))
#bind demographics and rawdata
data = cbind(dem, data)
###proportion correct per subject per language and wordlength
pr = round(as.data.frame(tapply(data$nr_correct, list(data$id, data$list, data$length), mean))/8, 3)
  
##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object
Result <- t.test(pr[,1], pr[,3], paired=T,alternative = "greater")
print(Result)

##@@ STATISTIC @@##
Result$statistic

##@@ P-VALUE @@##
Result$p.value

##@@ SAMPLE SIZE @@##
nrow(pr)

##@@ EFFECT SIZE @@##
#calculate d according to Lakens (2013) and calculate 95% CI
t = Result$statistic
n = nrow(pr)
efd = t/sqrt(n)
library("compute.es")
effectSize <- des(efd, n.1=n, n.2=n, level=95, dig=2, id=NULL, data=NULL)
effectSize$d


##@@ AGREEMENT WITH AUTHORS @@##
TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---

