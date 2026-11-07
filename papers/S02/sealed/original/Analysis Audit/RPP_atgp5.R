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
#@ A single-system account of the relationship between priming, recognition, and fluency.
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: t test
#@ Type of effect-size: Cohen's D
#@ OSF link project: https://osf.io/atgp5/
#@ OSF link replication report: https://osf.io/yc2fe/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("compute.es")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

#Option to download SPSS data file to tab delimited text (.dat). 
#Download dat data file as no need for file conversion for reading into R
file <- getOSFfile("https://osf.io/btr65/")
berry.data <- read.table(file, sep="\t", header=TRUE) 

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

#Paired t-test between RTs for correct rejections and RTs for misses
berryt.test <- with(berry.data, t.test( meanRT_cr, meanRT_miss, alternative="two.sided", 
                       paired=TRUE))
print(berryt.test)

##@@ STATISTIC @@##
berryt.test$statistic 

##@@ P-VALUE @@##
berryt.test$p.value

##@@ SAMPLE SIZE @@##
nrow(berry.data)

##@@ EFFECT SIZE @@##
t = berryt.test$statistic
n = nrow(berry.data)
efd = t/sqrt(n)

effectSize <- des(efd, n.1=n, n.2=n, level=95, dig=2, id=NULL, data=NULL)
effectSize$d  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---