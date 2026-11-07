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
#@ Study Title: Multiple roles for time in short-term memory: Evidence from serial recall of order and timing.
#@ Coder name: John Hodsoll
#@ Coder e-mail: john.hodsoll@kcl.ac.uk
#@ Type of statistic: t
#@ Type of effect-size: d
#@ OSF link project: https://osf.io/swrhy/
#@ OSF link replication report: https://osf.io/tqf2u/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")

source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.

#Data available in csv format

file <- getOSFfile("https://osf.io/i4syx/")
farr.data <- read.csv(file, header=T) 

##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL difference between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.


perTrial = 6
trials = 80
latencyIndex = 16

# How many subjects?
nSubj = dim(farr.data)[1]/trials

# Get only the timing trials with Rhythm. == 1, or only order with Rhythm == 0
# For the target analysis the relevant trials are Rhythm==1
rhythm = 1
d = subset(farr.data, Rhythm. == rhythm)

# Grab grouped and ungrouped data to average separately
nogroup = subset(d, Grouped. == 0)
group = subset(d, Grouped. == 1)

# Get the average latencies, like so:
# d[,"Out.sec.1"] produces a vector of 1st latencies, in subject blocks.
# Then we make a matrix whose columns each contain one subject's 1st latencies.
# Average over each column with colMeans to get a vector of subjects' average 1st latencies.
# Do that for latencies 1 through 6.
# Now rearrange them to get another matrix, "latencies"
# "latencies" now has subjects as rows, and average latencies 1 through 6 as columns

nogrouplatencies = data.frame(colMeans(matrix(data = nogroup[,"Out.sec.1"], ncol = nSubj)),
                              colMeans(matrix(data = nogroup[,"Out.sec.2"], ncol = nSubj)),
                              colMeans(matrix(data = nogroup[,"Out.sec.3"], ncol = nSubj)),
                              colMeans(matrix(data = nogroup[,"Out.sec.4"], ncol = nSubj)),
                              colMeans(matrix(data = nogroup[,"Out.sec.5"], ncol = nSubj)),
                              colMeans(matrix(data = nogroup[,"Out.sec.6"], ncol = nSubj)))

grouplatencies = data.frame(colMeans(matrix(data = group[,"Out.sec.1"], ncol = nSubj)),
                            colMeans(matrix(data = group[,"Out.sec.2"], ncol = nSubj)),
                            colMeans(matrix(data = group[,"Out.sec.3"], ncol = nSubj)),
                            colMeans(matrix(data = group[,"Out.sec.4"], ncol = nSubj)),
                            colMeans(matrix(data = group[,"Out.sec.5"], ncol = nSubj)),
                            colMeans(matrix(data = group[,"Out.sec.6"], ncol = nSubj)))

# set up dataframe, with subj number, index, avg latency
f = data.frame(subj = rep(1:nSubj, each=perTrial),
               index = 1:perTrial,
               grouped = rep(0:1, each=nSubj*perTrial),
               avgLatency = c(as.vector(t(nogrouplatencies)),as.vector(t(grouplatencies))))
f = transform(f, index=factor(index))
f = transform(f, subj=factor(subj))


##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or sumarry call on the resulting object

a1 = aov(avgLatency ~ (index*grouped) + Error(subj / (index*grouped)), data=f)
summ.a1 <- summary(a1)


#Here SS for interaction term is the same. 

##@@ STATISTIC @@##
#F from interaction term
summ.a1[["Error: subj:index:grouped"]][[1]][["F value"]][[1]]

##@@ P-VALUE @@##
summ.a1[["Error: subj:index:grouped"]][[1]][["Pr(>F)"]][[1]]

##@@ SAMPLE SIZE @@##
nSubj

##@@ EFFECT SIZE @@##
sumsq.error <- summ.a1[["Error: subj:index:grouped"]][[1]][["Sum Sq"]][[2]]
sumsq.effect <- summ.a1[["Error: subj:index:grouped"]][[1]][["Sum Sq"]][[1]]

effect.size <- sumsq.effect / (sumsq.effect + sumsq.error)
print(effect.size)  
##@@ AGREEMENT WITH AUTHORS @@##

TRUE

#@ Reason disagreement: ---ENTER WHY YOU BELIEVE RESULTS DISAGREE (ONLY IF RELEVANT)---