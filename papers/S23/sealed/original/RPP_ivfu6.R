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
#@ Study Title: Measuring the crowd within
#@ Coder name: Felix Henninger
#@ Coder e-mail: felix.henninger@web.de
#@ Type of statistic: t-test
#@ Type of effect-size: d
#@ OSF link project: https://osf.io/ivfu6/
#@ OSF link replication report: https://osf.io/7kimb/
#
##@@ REQUIRED PACKAGES @@##
library("httr")
library("RCurl")
source("http://sachaepskamp.com/files/OSF/getOSFfile.R") # the getOSFfile function
  
library("dplyr")
library("compute.es")

##@@ DATA LOADING @@##
#@ NOTE: Data must be loaded from OSF directly and NOT rely on any local files.
# (There are data from another condition available, but these are 
# not relevant for the main hypothesis tested here)
# file.immediate <- getOSFfile('https://osf.io/ckw86/')
file.delayed_session_1 <- getOSFfile('https://osf.io/k64yt/')
file.delayed_session_2 <- getOSFfile('https://osf.io/nbkvg/')

#data.immediate <- read.csv(file.immediate, sep='\t', na.strings='NaN')
data.delayed_session_1 <- read.csv(file.delayed_session_1, sep='\t', na.strings='NaN')
data.delayed_session_2 <- read.csv(file.delayed_session_2, sep='\t', na.strings='NaN')
  
##@@ DATA MANIPULATION @@##
#@ NOTE: Include here ALL differences between OSF data and data used in analysis
#@ TIP: You will want to learn all about dplyr for manipulating data.

# Merge the data from both delayed sessions into a single data.frame.
# Data collected at both sessions is now suffixed with '.s1' and '.s2',
# respectively
data.delayed <- merge(
  data.delayed_session_1, data.delayed_session_2,
  by='student_number_simple', suffixes=c('.s1', '.s2')
)

# Filtering ---------------------------------------------------------------

# Compute the number of times the window was defocussed while answering the questions
data.delayed$defocus_total <- data.delayed %>%
  dplyr::select(starts_with('defocus')) %>%
  rowSums()

# Compute the number of questions for which responses are missing
data.delayed$missing_responses <-  data.delayed %>%
  dplyr::select(starts_with('q')) %>%
  is.na %>%
  rowSums()

# Filter data according to exclusion criteria
data.delayed <- data.delayed %>%
  filter(defocus_total == 0, missing_responses == 0, peaking == 'Nee')

# Preprocessing -----------------------------------------------------------

# The response variable of interest were 8 trivia questions, 
# the answers of which are defined here.
correctAnswers <- c(
  6.3, # The area of the USA is what percent of the area of the Pacific Ocean -> 6.3%
  43.3, # What percent of the worlds population lives in either China, India, or the European Union? -> 43.3%
  32.3, # What percent of the worlds airports are in the United States? -> 32.3%
  13.4, # What percent of the worlds roads are in India? -> 13.4%
  53.6, # What percent of the worlds countries have a higher fertility rate than the United states? -> 53.6%
  54.8, # What percent of the worlds telephone lines are in China, USA, or the European Union? -> 54.8%
  26.4, # Saudi Arabia consumes what percentage of the oil it produces? -> 26.4%
  22.4 # What percentage of the worlds countries have a higher life expectancy than the United States? -> 22.4%
)

# The central dependent variable is the mean squared error
# of the responses participants gave to the the questions above

# Given a set of responses, compute a mean squared error (MSE)
calcMSE <- function(q1, q2, q3, q4, q5, q6, q7, q8) {
  answers <- c(q1, q2, q3, q4, q5, q6, q7, q8)
  se <- (answers - correctAnswers)^2
  return(mean(se))
}

# Data pre-processing: Generation of main dependent variable
data.delayed <- data.delayed %>%
  rowwise() %>% 
  # Compute MSEs for the answers provided in the first and second session,
  # and for the mean of both, respectively
  dplyr::mutate(mse.s1 = calcMSE(q1.s1, q2.s1, q3.s1, q4.s1, q5.s1, q6.s1, q7.s1, q8.s1)) %>%
  dplyr::mutate(mse.s2 = calcMSE(q1.s2, q2.s2, q3.s2, q4.s2, q5.s2, q6.s2, q7.s2, q8.s2)) %>%
  dplyr::mutate(mse.mean = calcMSE(
    (q1.s1 + q1.s2) / 2,
    (q2.s1 + q2.s2) / 2,
    (q3.s1 + q3.s2) / 2,
    (q4.s1 + q4.s2) / 2,
    (q5.s1 + q5.s2) / 2,
    (q6.s1 + q6.s2) / 2,
    (q7.s1 + q7.s2) / 2,
    (q8.s1 + q8.s2) / 2
  )) %>%
  # Finally, condense the data into a more manageable format
  dplyr::select(one_of(c('sex', 'age', 'student_number_simple')), starts_with('q'), starts_with('mse')) 

# Data checking -----------------------------------------------------------

table(data.delayed$sex) # sex of participants should be 125 female (vrouwelijk), and 15 male (mannelijk)
mean(data.delayed$age) # mean age should be 22.0 (rounded to one decimal figure)
sd(data.delayed$age) # sd of age should be 3.1 (rounded again)
  
##@@ DATA ANLAYSIS @@##
#@ NOTE: Include a print or summary call on the resulting object
# Central hypothesis: The MSE of the mean estimate shows less error than
# the guess made in the first session alone.
test <- t.test(data.delayed$mse.s1, data.delayed$mse.mean, 
  alternative='greater', paired=TRUE)

print(test)

##@@ STATISTIC @@##
test$statistic

##@@ P-VALUE @@##
test$p.value
  
##@@ SAMPLE SIZE @@##
nrow(data.delayed)

##@@ EFFECT SIZE @@##
n = nrow(data.delayed)
es <- des(test$statistic / sqrt(n), 
  n.1=n, n.2=n, 
  level=95, dig=2, 
  id=NULL, data=NULL, verbose=FALSE
)

es$d
  
##@@ AGREEMENT WITH AUTHORS @@##
TRUE
  
#@ Reason disagreement: None