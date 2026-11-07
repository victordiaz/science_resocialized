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
#@ Study Title:  Priming Addition Facts with Semantic Relations.
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: F
#@ Type of effect-size: partial eta squared
#@ OSF link project: https://osf.io/sqim7/
#@ OSF link replication report: https://osf.io/irgbs/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
library("foreign")
library("reshape2")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

#Data available in csv format

file <- getOSFfile("https://osf.io/c3zid/")
bass.data <- read.spss(file, to.data.frame=TRUE) 

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

#Data has rows 50 to 320 of missing data
bass.data <- bass.data[1:49,]

#Data in spss wide format - reshape
bass.long <- melt(bass.data, 
                  id.vars="id",
                  measure.vars=c("avg_time_sum_ac", 
                                 "avg_time_neutral_ac",
                                 "avg_time_sum_mu",
                                 "avg_time_neutral_mu"),
                  variable.name="cond",
                  value.name="RT")

bass.long$prime <- 1
bass.long$prime[grep("mu", bass.long$cond)] <- 2 
bass.long <- transform(bass.long, prime=factor(prime, labels=c("ac", "mu")))

bass.long$sum <- 1
bass.long$sum[grep("neu", bass.long$cond)] <- 2 
bass.long <- transform(bass.long, sum=factor(sum, labels=c("sum", "neutral")))

bass.long <- transform(bass.long, id=factor(id))


##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

bass.aov1 = aov(RT ~ (prime*sum) + Error(id / (prime*sum)), data=bass.long)
summ.a1 <- summary(bass.aov1)

#As ANOVA balanced type 1 and 3 SS will be the same. 

##@@ STATISTIC @@##
#F from interaction term
summ.a1[["Error: id:prime:sum"]][[1]][["F value"]][[1]]

##@@ P-VALUE @@##
summ.a1[["Error: id:prime:sum"]][[1]][["Pr(>F)"]][[1]]

##@@ SAMPLE SIZE @@##
nrow(bass.data)

##@@ EFFECT SIZE @@##
sumsq.error <- summ.a1[["Error: id:prime:sum"]][[1]][["Sum Sq"]][[2]]
sumsq.effect <- summ.a1[["Error: id:prime:sum"]][[1]][["Sum Sq"]][[1]]

effect.size <- sumsq.effect / (sumsq.effect + sumsq.error)
print(effect.size)  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---