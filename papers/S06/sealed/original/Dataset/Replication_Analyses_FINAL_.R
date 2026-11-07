#Replication Analyses FINAL

repdatalong=read.csv("~/Dropbox/Replication Stuff/JenniferData/Data New/Merged Data/repdatalong.csv", header=T)

#check/examine datafile
length(unique(repdatalong$ID))#75
head(repdatalong)
unique(repdatalong$GENDER)

#Recode GENDER
repdatalong$GENDER <- factor(ifelse(repdatalong$GENDER=="f"|repdatalong$GENDER=="F", "F", "M"))

length(which(repdatalong$GENDER=="F"))/length(repdatalong$GENDER)
length(which(repdatalong$HiLoCat == "HighIMSHighEMS"))/length(repdatalong$HiLoCat)

#Remove unnecessary first variable
repdatalong=repdatalong[,-1]
repdatalong[order(repdatalong$ID),]


head(repdatalong)

#repdatalong=na.omit(repdatalong)

#Descriptive Statistics
tapply(repdatalong$PD, list(repdatalong$TrialType, repdatalong$HiLoCat), length)

#         HighIMSHighEMS HighIMSLowEMS
#Black                29            46
#Flankers             29            46
#White                29            46

sum(tapply(repdatalong$PD, list(repdatalong$TrialType, repdatalong$HiLoCat), length)[1,])

#75

tapply(repdatalong$PD, list(repdatalong$TrialType, repdatalong$HiLoCat), mean)
tapply(repdatalong$PD, list(repdatalong$TrialType, repdatalong$HiLoCat), sd)


tapply(repdatalong$PD, list(repdatalong$Task, repdatalong$HiLoCat), mean)
tapply(repdatalong$PD, list(repdatalong$Task, repdatalong$HiLoCat), sd)


#########################
# Confirmatory Analysis #
#########################

Fit = aov(PD~factor(HiLoCat)*factor(Task)+Error(factor(ID)/factor(Task)), repdatalong)
summary(Fit)

#Error: factor(ID)
#                Df Sum Sq Mean Sq F value Pr(>F)
#factor(HiLoCat)  1  0.118 0.11792   1.454  0.232
#Residuals       73  5.920 0.08109               
#
#Error: factor(ID):factor(Task)
#                             Df Sum Sq Mean Sq F value Pr(>F)
#factor(Task)                  1 0.0118 0.01183   0.505  0.480
#factor(HiLoCat):factor(Task)  1 0.0101 0.01014   0.432  0.513
#Residuals                    73 1.7115 0.02345               
#
#Error: Within
#          Df Sum Sq  Mean Sq F value Pr(>F)
#Residuals 75 0.4044 0.005392      

########################
# EXPLORATORY ANALYSES #
########################

##############################
# Descriptives for Tables     #
# (Exploratory Vars)          #
###############################

#Read in weapons file
weapons <- read.csv(file="~/Dropbox/Replication Stuff/JenniferData/Data New/Weapons Flankers Separate/weapons.csv")

weapons$absRT <- abs(weapons$rt)
weapons$Prime <- as.factor(ifelse(weapons$TrialType == "WhiteGun" | weapons$TrialType == "WhiteTool", "White", "Black"))
weapons$Target <- as.factor(ifelse(weapons$TrialType == "WhiteGun" | weapons$TrialType == "BlackGun", "Gun", "Tool"))


#Read in Error Rate Datasets
weaponsErrorRateDF <- read.csv(file="~/Dropbox/Replication Stuff/JenniferData/Data New/Error Rate Data for Exploratory/weaponsErrorRateDF.csv", header=T)
flankersErrorRateDF <- read.csv(file="~/Dropbox/Replication Stuff/JenniferData/Data New/Error Rate Data for Exploratory/flankersErrorRateDF.csv", header=T)


with(weapons, tapply(absRT, list(Prime, Target), mean))

#           Gun     Tool
#Black 405.1443 440.7902
#White 414.3815 444.7245

with(weapons, tapply(absRT, list(Prime, Target), sd))
#           Gun     Tool
#Black 69.05155 75.20556
#White 70.90255 75.56741


with(weaponsErrorRateDF, tapply(ErrorRate, list(Prime, Target), mean))
#            Gun      Tool
#Black 0.1418518 0.1520121
#White 0.2013958 0.1191623

with(weaponsErrorRateDF, tapply(ErrorRate, list(Prime, Target), sd))
#            Gun       Tool
#Black 0.1234172 0.13519611
#White 0.1425600 0.09164887

with(flankersErrorRateDF, tapply(ErrorRate, TrialType, mean))

#  Congruent Incongruent 
# 0.02141778  0.31007238 

with(flankersErrorRateDF, tapply(ErrorRate, TrialType, sd))

#  Congruent Incongruent 
# 0.03144393  0.15928717 


#####################################
####Weapons absolute RT analysis#####
#####################################

summary(aov(absRT~Prime*Target+Error(factor(ID)/(Prime+Target)), weapons))

#Error: factor(ID)
#              Df   Sum Sq Mean Sq F value Pr(>F)  
#Prime          1   140114  140114   0.940 0.3345  
#Target         1   999159  999159   6.701 0.0109 *
#Prime:Target   1    85973   85973   0.577 0.4493  
#Residuals    109 16251931  149100                 
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

#Error: factor(ID):Prime
#              Df Sum Sq Mean Sq F value   Pr(>F)    
#Prime          1 230383  230383  34.539 4.54e-08 ***
#Target         1  34792   34792   5.216   0.0243 *  
#Prime:Target   1   4100    4100   0.615   0.4347    
#Residuals    110 733718    6670                     
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
#
#Error: factor(ID):Target
#              Df  Sum Sq Mean Sq F value Pr(>F)    
#Target         1 5531099 5531099 418.341 <2e-16 ***
#Prime:Target   1   20799   20799   1.573  0.212    
#Residuals    111 1467587   13222                   
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
#
#Error: Within
#                Df   Sum Sq Mean Sq F value  Pr(>F)   
#Prime:Target     1    33226   33226   7.526 0.00609 **
#Residuals    20396 90050397    4415                   
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

#Within error term is clear ... but these results are a bit wonky. Let's cross-reference with a few other analyses...


#Confirm above results using mixed model framework...
library(nlme)
mem.mod2=lme(absRT ~ Prime + Target + Prime:Target, random=(~1 | ID),  method="ML", data=weapons,  cor=corCompSymm(), na.action=na.omit)
summary(mem.mod2)

#Linear mixed-effects model fit by maximum likelihood
# Data: weapons 
#       AIC      BIC    logLik
#  233580.7 233636.2 -116783.3

#Random effects:
# Formula: ~1 | ID
#        (Intercept) Residual
#StdDev:    29.50612 66.90001

#Correlation Structure: Compound symmetry
# Formula: ~1 | ID 
# Parameter estimate(s):
#          Rho 
#-4.325426e-19 
#Fixed effects: absRT ~ Prime + Target + Prime:Target 
                         Value Std.Error    DF   t-value p-value
#(Intercept)           404.4363  2.929070 20620 138.07671  0.0000
#PrimeWhite              9.2251  1.313968 20620   7.02080  0.0000
#TargetTool             35.2806  1.316234 20620  26.80419  0.0000
#PrimeWhite:TargetTool  -5.1149  1.858697 20620  -2.75187  0.0059
# Correlation: 
#                      (Intr) PrmWht TrgtTl
#PrimeWhite            -0.225              
#TargetTool            -0.225  0.501       
#PrimeWhite:TargetTool  0.159 -0.707 -0.708

#Standardized Within-Group Residuals:
#        Min          Q1         Med          Q3         Max 
#-3.45327304 -0.63787674 -0.07644895  0.55740297  5.31116567 

#Number of Observations: 20736
#Number of Groups: 113 


#Squared t values ...

#7.02080^2
#49.29163

(-2.75187)^2
#718.4646

26.80419^2
#7.572788

#Similar, but not identical, to above. Pattern of significance is consistent.



#Another Check on this general pattern ... run the mean absolute reaction times by task.
#(This way each person has four repeated measurements: black gun, black tool, white gun, white tool,
#rather than many repetitions of each).


#Create table
weaponsTrialMeans <- with(weapons, tapply(absRT, list(ID, TrialType), mean))
#save as data frame
weaponsTrialMeans <- data.frame(weaponsTrialMeans)

#Original columnn names
colnames(weaponsTrialMeans)
#"BlackGun"  "BlackTool" "WhiteGun"  "WhiteTool"

#Change colnames for reshape
colnames(weaponsTrialMeans) <- paste("Trial", 1:4, sep=".")

#Add ID var for reshape
weaponsTrialMeans$ID <- 1:nrow(weaponsTrialMeans)

#reshape
weaponsMeansLong <- reshape(weaponsTrialMeans, varying = paste("Trial", 1:4, sep="."), idvar="ID", timevar="TrialType", direction="long")


#Relabel/recode key vars
weaponsMeansLong$ID <- as.factor(weaponsMeansLong$ID)
weaponsMeansLong$Prime <- as.factor(ifelse(weaponsMeansLong$TrialType == 1 | weaponsMeansLong$TrialType == 2, "Black", "White"))
weaponsMeansLong$Target <- as.factor(ifelse(weaponsMeansLong$TrialType == 1 | weaponsMeansLong$TrialType == 3, "Gun", "Tool"))
colnames(weaponsMeansLong)[3] = "absRT"


#Key test:

summary(aov(absRT~Prime*Target + Error(ID/(Prime+Target)), weaponsMeansLong))

#Error: ID
#           Df Sum Sq Mean Sq F value Pr(>F)
#Residuals 112 408444    3647               

#Error: ID:Prime
#           Df Sum Sq Mean Sq F value   Pr(>F)    
#Prime       1   5639    5639   29.57 3.19e-07 ***
#Residuals 112  21355     191                     
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

#Error: ID:Target
#           Df Sum Sq Mean Sq F value Pr(>F)    
#Target      1 119600  119600   414.4 <2e-16 ***
#Residuals 112  32321     289                   
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

#Error: Within
#              Df Sum Sq Mean Sq F value Pr(>F)  
#Prime:Target   1    582   581.8   3.957 0.0491 *
#Residuals    112  16469   147.0                 
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1


#Opting to report this one .... seems most sensible, although pattern of significance is same for key interaction across all versions of the analysis.


########################################
### Analyses of Error Rates By Trial ###
########################################

#Weapons Task

summary(aov(ErrorRate~Prime*Target+Error(ID/(Prime+Target)), weaponsErrorRateDF))

#Error: ID
#           Df Sum Sq Mean Sq F value Pr(>F)
#Residuals 112  4.457  0.0398               

#Error: ID:Prime
#           Df Sum Sq  Mean Sq F value Pr(>F)  
#Prime       1 0.0201 0.020130   6.346 0.0132 *
#Residuals 112 0.3553 0.003172                 
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

#Error: ID:Target
#           Df Sum Sq Mean Sq F value   Pr(>F)    
#Target      1 0.1467 0.14675   15.84 0.000123 ***
#Residuals 112 1.0380 0.00927                     
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

#Error: Within
#              Df Sum Sq Mean Sq F value  Pr(>F)    
#Prime:Target   1 0.2412  0.2412   24.13 3.1e-06 ***
#Residuals    112 1.1195  0.0100                    
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1


#Flankers Task

summary(aov(ErrorRate~TrialType+Error(ID/factor(TrialType)), flankersErrorRateDF))

#Error: ID
#           Df Sum Sq Mean Sq F value Pr(>F)
#Residuals 105  1.564  0.0149               

#Error: ID:factor(TrialType)
#           Df Sum Sq Mean Sq F value Pr(>F)    
#TrialType   1  4.416   4.416   385.1 <2e-16 ***
#Residuals 105  1.204   0.011                   
#---
#Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1



