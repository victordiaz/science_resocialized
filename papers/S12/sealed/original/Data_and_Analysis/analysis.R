# First run prep_dataset.R and then iatscoring.R. 


# reliabilities for explicit measure
library(psych)
alpha(fin[c("rfriendly", "rlike", "rlikeable", "rpleasant", "rpopular", "rresponsible")])
alpha(fin[c("vfriendly", "vlike", "vlikeable", "vpleasant", "vpopular", "vresponsible")])
alpha(fin[c("bfriendly", "blike", "blikeable", "bpleasant", "bpopular", "bresponsible")])
alpha(fin[c("ifriendly", "ilike", "ilikeable", "ipleasant", "ipopular", "iresponsible")])

mean(fie$lexp, na.rm=T)
tapply(fin$exppref,  fin$rateorig, psych::describe)


# here it is! The test of difference between the explicit rating groups
t<-t.test(fin$exppref[fin$rateorig==0], fin$exppref[fin$rateorig==1])
t
# now for implicit preference
tapply(fin$imppref,  fin$rateorig, psych::describe)
tapply(fin$imppref,  fin$rateorig, Hmisc::describe)
t<-t.test(fin$imppref[fin$rateorig==0], fin$imppref[fin$rateorig==1])
t
# t = -6.3092, df = 3511.101, p-value = 3.154e-10
# alternative hypothesis: true difference in means is not equal to 0
# 95 percent confidence interval:
#     -0.13152842 -0.06916222
# sample estimates:
#     mean of x  mean of y 
# 0.04983945 0.15018477 


# now let's re-run those excluding the participants who got incorrect IAT instructions (not as bad as it sounds; see the paper for details)
finn<-fin[fin$instructions_correct==1,]
nrow(fin) - nrow(finn)
table(fin$cond, fin$instructions_correct)
t<-t.test(fin$exppref[fin$rateorig==0], fin$exppref[fin$rateorig==1])
t
t<-t.test(fin$imppref[fin$rateorig==0], fin$imppref[fin$rateorig==1])
t
nrow(fin[fin$rateorig==1 & fin$instructions_correct==1,])
nrow(fin[fin$rateorig==1,])
t.test(fin$exppref[fin$rateorig==1 & fin$instructions_correct==1], fin$exppref[fin$rateorig==1 & fin$instructions_correct==0])
t.test(fin$imppref[fin$rateorig==1 & fin$instructions_correct==1], fin$imppref[fin$rateorig==1 & fin$instructions_correct==0])

# exploratory: Does the new-target group preference differ from zero?
t.test(fin$imppref[fin$rateorig==0])
t.test(fin$exppref[fin$rateorig==0])
names(fin)
head(fin[c("chb", "chg", "shb", "shg")])

table(fin$chb, fin$cond, fin$instructions_correct)


# demographics
# see codebook at http://peoplescience.org/node/113
# get gender, age, ethnicity, race, residence

#deme is the table with demographics for everyone who signed up for the study.
table(deme$demog_sex)

deme$country<-deme$residence
deme$country[!is.na(deme$residence) & deme$residence=="sm"]<-deme$citizenship[!is.na(deme$residence) & deme$residence=="sm"]
table(deme$country, useNA="always")
cntry<-table(deme$country, useNA="always") / sum(table(deme$country, useNA="always"))
cntry[cntry>.01]

deme$birthyear<-as.numeric(deme$birthyear)
deme$age = 2014-deme$birthyear
deme$age[!is.na(deme$birthmonth) & deme$birthmonth>=11]<-deme$age[!is.na(deme$birthmonth) & deme$birthmonth>=11]-1
psych::describe(deme$age)

eth<-table(deme$ethnicityomb)
eth/sum(eth)

rac<-table(deme$raceomb)
racp<-rac/sum(rac)
racp[racp>.01]

# now just the completers

fin$country<-fin$residence
fin$country[!is.na(fin$residence) & fin$residence=="sm"]<-fin$citizenship[!is.na(fin$residence) & fin$residence=="sm"]
table(fin$country, useNA="always")
cntry<-table(fin$country, useNA="always") / sum(table(fin$country, useNA="always"))
cntry[cntry>.01]

fin$birthyear<-as.numeric(fin$birthyear)
fin$age = 2014-fin$birthyear
fin$age[!is.na(fin$birthmonth) & fin$birthmonth>=11]<-fin$age[!is.na(fin$birthmonth) & fin$birthmonth>=11]-1
psych::describe(fin$age)

eth<-table(fin$ethnicityomb)
eth/sum(eth)

rac<-table(fin$raceomb)
racp<-rac/sum(rac)
racp[racp>.01]




fin$country<-fin$residence
fin$country[!is.na(fin$residence) & fin$residence=="sm"]<-fin$citizenship[!is.na(fin$residence) & fin$residence=="sm"]
table(fin$country, useNA="always")
cntry<-table(fin$country, useNA="always") / sum(table(fin$country, useNA="always"))
cntry[cntry>.01]

# .    f    m 
# 29 2242 1325 

fin$birthyear<-as.numeric(fin$birthyear)
fin$age = 2014-fin$birthyear
fin$age[!is.na(fin$birthmonth) & fin$birthmonth>=11]<-fin$age[!is.na(fin$birthmonth) & fin$birthmonth>=11]-1
psych::describe(fin$age)

eth<-table(fin$ethnicityomb)
eth/sum(eth)

rac<-table(fin$raceomb)
racp<-rac/sum(rac)
racp[racp>.01]

# manipulation check. did they correctly identify the pictures?

table(fin$chb, fin$cond, fin$instructions_correct)
table(fin$chg, fin$cond, fin$instructions_correct)
table(fin$shb, fin$cond, fin$instructions_correct)
table(fin$shg, fin$cond, fin$instructions_correct)


chbresps<- c(3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2)
chgresps<- c(1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4)
shbresps<- c(4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1)
shgresps<- c(2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3)

names(chbresps)<-codes$cond
names(shbresps)<-codes$cond
names(chgresps)<-codes$cond
names(shgresps)<-codes$cond

fin$chb_correctresp<-chbresps[fin$cond]
fin$chg_correctresp<-chgresps[fin$cond]
fin$shb_correctresp<-shbresps[fin$cond]
fin$shg_correctresp<-shgresps[fin$cond]

fin$chb_correct <- ifelse(fin$chb == fin$chb_correctresp, 1, 0)
fin$shb_correct <- ifelse(fin$shb == fin$shb_correctresp, 1, 0)
fin$chg_correct <- ifelse(fin$chg == fin$chg_correctresp, 1, 0)
fin$shg_correct <- ifelse(fin$shg == fin$shg_correctresp, 1, 0)
fin$manipchk_score<-fin$chb_correct + fin$chg_correct + fin$shb_correct + fin$shg_correct
table(fin$manipchk_score)
table(fin$manipchk_score, fin$cond)

t<-t.test(fin$exppref[fin$rateorig==0 & fin$manipchk_score == 4], fin$exppref[fin$rateorig==1 & fin$manipchk_score == 4])
t
t<-t.test(fin$imppref[fin$rateorig==0 & fin$manipchk_score == 4], fin$imppref[fin$rateorig==1 & fin$manipchk_score == 4])
t


# Manipulation check: Did the target information affect explicit attitudes?
t.test(fin$expgood[fin$rateorig==1], fin$expbad[fin$rateorig==1], paired=T)
psych::describe(fin$expgood[fin$rateorig==1])
psych::describe(fin$expbad[fin$rateorig==1])
psych::describe(fin$exppref[fin$rateorig==1])
t.test(fin$expgood[fin$rateorig==1] - fin$expbad[fin$rateorig==1])
psych::describe(fin$exppref[fin$rateorig==1])
# for within-ss, d is just the diff over the sd of the diff, right?



# alternate analysis: directly compare implicit-explicit diff for new vs old

fin$exppref.std<-(fin$exppref - mean(fin$exppref))/sd(fin$exppref)
fin$imppref.std<-(fin$imppref - mean(fin$imppref))/sd(fin$imppref)
temp<-fin[c("session_id", "imppref.std", "exppref.std", "rateorig", "reemgood", "swap", "target_sex")]
library(reshape2)
altfin<-melt(temp, measure.vars=c("imppref.std", "exppref.std"))
head(altfin)
altfin$explicit<-ifelse(altfin$variable=="imppref.std", 0, 1)
summary(lm(value ~ rateorig * explicit, data=altfin))
altfin$ratenew = 1-altfin$rateorig

fit<-aov(value ~ (rateorig * explicit) + Error(session_id/(explicit)) + rateorig, data=altfin)
fit
summary(fit)
head(altfin[c("rateorig", "ratenew")])

fit<-aov(value ~ (ratenew * explicit) + Error(session_id/(explicit)) + ratenew, data=altfin)
fit
summary(fit)

psych::describe(altfin$value[altfin$explicit==0 & altfin$rateorig==1])
psych::describe(altfin$value[altfin$explicit==1 & altfin$rateorig==1])
psych::describe(altfin$value[altfin$explicit==0 & altfin$rateorig==0])
psych::describe(altfin$value[altfin$explicit==1 & altfin$rateorig==0])

# Test for differences based on target sex, group appearance, and which group had the well-behaved individual.

fit<-lm(exppref ~ rateorig*reemgood*target_sex*swap, data=fin)
summary(fit)

fit<-lm(imppref ~ rateorig*reemgood*target_sex*swap, data=fin)
summary(fit)

fit0<-lm(imppref ~ rateorig, data=fin)
summary(fit0)
fit1<-lm(imppref ~ rateorig*target_sex, data=fin)
summary(fit1)
fit2<-lm(imppref ~ rateorig*reemgood, data=fin)
summary(fit2)
fit3<-lm(imppref ~ rateorig*swap, data=fin)
summary(fit3)
fit12<-lm(imppref ~ rateorig*target_sex*reemgood, data=fin)
summary(fit12)
fit13<-lm(imppref ~ rateorig*swap*reemgood, data=fin)
summary(fit13)





# ok

# Df Sum Sq Mean Sq F value Pr(>F)    
# rateorig               1    717   716.8 498.210 <2e-16 ***
# target_sex             1      3     2.9   2.002  0.157    
# rateorig:target_sex    1      3     2.8   1.938  0.164    

fit<-aov(exppref ~ rateorig * reemgood, data=fin)
summary(fit)
# Df Sum Sq Mean Sq F value  Pr(>F)    
# rateorig             1    717   716.8 499.198 < 2e-16 ***
# reemgood             1     13    13.0   9.043 0.00266 ** 
# rateorig:reemgood    1      3     2.9   2.031 0.15418    

fit<-aov(exppref ~ rateorig * swap, data=fin)
summary(fit)
# Df Sum Sq Mean Sq F value  Pr(>F)    
# rateorig         1    717   716.8 498.694 < 2e-16 ***
# swap             1     10     9.7   6.754 0.00939 ** 
# rateorig:swap    1      1     1.0   0.681 0.40931    
# Residuals     3593   5165     1.4                    


fit<-aov(imppref ~ rateorig * target_sex, data=fin)
summary(fit)

fit<-aov(imppref ~ rateorig * reemgood, data=fin)
summary(fit)

fit<-aov(imppref ~ rateorig * swap, data=fin)
summary(fit)



