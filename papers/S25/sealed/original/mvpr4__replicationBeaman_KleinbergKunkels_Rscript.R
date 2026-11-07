###prepare working directory and read all output files from folder
rm(list=ls())
setwd('XXX')
file_list <- list.files()
data <- do.call("rbind",lapply(file_list,FUN=function(files) {
    read.table(files,header=TRUE, sep="\t")
}))
#add demographics manually (copied from original output files for reasons of
# data pre-processing)
dem = data.frame(id = rep(c(1:15), each=80),
                 eng = rep(c(6,6,7,10,6,9,7,8,5,9,8,6,8,9,8),each=80),
                 age = rep(c(20,20,20,19,19,20,19,18,23,19,18,21,20,19,20),each=80),
                 gender = rep(c("f","f","f","f","f","m","f","f","m","f","f","f","f","f","f"),each=80),
                 lang = rep(c(rep("NL", 8), "GER", rep("NL", 6)),each=80))
#bind demographics and rawdata
data = cbind(dem, data)
---------------
    ###descriptives    
    mean(data$age); sd(data$age)
mean(data$eng); sd(data$eng)
table(dem$gender)

###proportion correct per subject per language and wordlength
pr = round(as.data.frame(tapply(data$nr_correct, list(data$id, data$list, data$length), mean))/8, 3)

--------------
    ###test statistics
#t-test for proportion correct of English long and English short words (confirmatory)
t.test(pr[,1], pr[,3], paired=T,alternative = "greater")

#calculate d according to Lakens (2013) and calculate 95% CI
t = .4956; n = 15
efd = t/sqrt(n)
library(compute.es)
des(efd, n.1=15, n.2=15, level=95, dig=2, id=NULL, data=NULL)

#add Word Length Effect (wle) to variabel pr
pr$wleEN = round((pr[,1] - pr[,3])/pr[,1],3)
pr$wleNL = round((pr[,2] - pr[,4])/pr[,2],3)

#descr
pr = rbind(pr, apply(pr, 2, mean))
pr = rbind(pr, apply(pr, 2, sd))

#intercorrelations
library("psych")
corr.test(pr)

#t-test for Dutch short words and Dutch long words (exploratory)
t.test(pr[,2], pr[,4], paired=T)

#calculate d according to Lakens (2013) and calculate 95% CI
t = .9857; n = 15
efd = t/sqrt(n)
library(compute.es)
des(efd, n.1=15, n.2=15, level=95, dig=2, id=NULL, data=NULL)

#prepare proxy dataframe in stacked format for overall comparison
proxprox = data.frame("prop" = c(pr[,1], pr[,3], pr[,2], pr[,4]),
                      "length" = rep(c(rep("short", 15), rep("long", 15)),2),
                      "lang" = c(rep("EN", 30), rep("NL", 30)))
tapply(proxprox$prop, proxprox$lang, mean)
tapply(proxprox$prop, proxprox$length, mean)
t.test(proxprox$prop ~ proxprox$length, alternative="greater", paired=T)
t.test(proxprox$prop ~ proxprox$lang,  paired=T)

#plot proportion correct English words
#short
plot(pr[,1], col="red")
#long
points(pr[,3], col="blue")

#plot proportion correct Dutch words
#short
plot(pr[,2], col="red")
#long
points(pr[,4], col="blue")

#plot WLE English
plot(pr[,5], col="red", ylim=c(-.4, .4))
#add WLE Dutch
points(pr[,6], col="blue")

#plot proportion correct over trials after lowess harmonisation
pr1 = split(data, f=data$list)
plot(lowess(tapply(pr1[[1]]$nr_correct, pr1[[1]]$trnr, mean)/8), ylim=c(.5,.65),
     type="l", col="red", frame=F, xlab = "")
lines(lowess(tapply(pr1[[2]]$nr_correct, pr1[[2]]$trnr, mean)/8), ylim=c(.5,.65),
      type="l", col="blue")



#Confounds?: Association demograohics and proportion correct?
v = round(as.data.frame(tapply(data$nr_correct, list(data$list, data$length), sum)), 3)
chisq.test(v, correct=F)


#Exploratory RT analysis
rt1 = round(tapply(data$rt1, list(data$id, data$list), mean), 0)
rt2 = round(tapply(data$rt2, list(data$id, data$list), mean), 0)
rt3 = round(tapply(data$rt3, list(data$id, data$list), mean), 0)
rt4 = round(tapply(data$rt4, list(data$id, data$list), mean), 0)
rt5 = round(tapply(data$rt5, list(data$id, data$list), mean), 0)
rt6 = round(tapply(data$rt6, list(data$id, data$list), mean), 0)
rt7 = round(tapply(data$rt7, list(data$id, data$list), mean), 0)
rt8 = round(tapply(data$rt8, list(data$id, data$list), mean), 0)

plot(rt1[,1], type="l", ylim=c(2000, 25000), col="blue")
lines(rt2[,1], type="l", col="blue")
lines(rt3[,1], type="l", col="blue")
lines(rt4[,1], type="l", col="blue")
lines(rt5[,1], type="l", col="blue")
lines(rt6[,1], type="l", col="blue")
lines(rt7[,1], type="l", col="blue")
lines(rt8[,1], type="l", col="blue")

lines(rt1[,2], type="l", col="red")
lines(rt2[,2], type="l", col="red")
lines(rt3[,2], type="l", col="red")
lines(rt4[,2], type="l", col="red")
lines(rt5[,2], type="l", col="red")
lines(rt6[,2], type="l", col="red")
lines(rt7[,2], type="l", col="red")
lines(rt8[,2], type="l", col="red")

delta2 = rt2-rt1
delta3 = rt3-rt2
delta4 = rt4-rt3
delta5 = rt5-rt4
delta6 = rt6-rt5
delta7 = rt7-rt6
delta8 = rt8-rt7

rt1s = round(tapply(data$rt1, list(data$id, data$list, data$length), mean), 0)
rt2s = round(tapply(data$rt2, list(data$id, data$list, data$length), mean), 0)
rt3s = round(tapply(data$rt3, list(data$id, data$list, data$length), mean), 0)
rt4s = round(tapply(data$rt4, list(data$id, data$list, data$length), mean), 0)
rt5s = round(tapply(data$rt5, list(data$id, data$list, data$length), mean), 0)
rt6s = round(tapply(data$rt6, list(data$id, data$list, data$length), mean), 0)
rt7s = round(tapply(data$rt7, list(data$id, data$list, data$length), mean), 0)
rt8s = round(tapply(data$rt8, list(data$id, data$list, data$length), mean), 0)

prrt1ss = apply(rt1s[,,1], 2, mean)
prrt2ss = apply(rt2s[,,1], 2, mean)
prrt3ss = apply(rt3s[,,1], 2, mean)
prrt4ss = apply(rt4s[,,1], 2, mean)
prrt5ss = apply(rt5s[,,1], 2, mean)
prrt6ss = apply(rt6s[,,1], 2, mean)
prrt7ss = apply(rt7s[,,1], 2, mean)
prrt8ss = apply(rt8s[,,1], 2, mean)

prrt1sl = apply(rt1s[,,2], 2, mean)
prrt2sl = apply(rt2s[,,2], 2, mean)
prrt3sl = apply(rt3s[,,2], 2, mean)
prrt4sl = apply(rt4s[,,2], 2, mean)
prrt5sl = apply(rt5s[,,2], 2, mean)
prrt6sl = apply(rt6s[,,2], 2, mean)
prrt7sl = apply(rt7s[,,2], 2, mean)
prrt8sl = apply(rt8s[,,2], 2, mean)

prarraynr = c(1:8)
prarrayss = c(prrt1ss[1], prrt2ss[1], prrt3ss[1], prrt4ss[1], prrt5ss[1], prrt6ss[1],
              prrt7ss[1], prrt8ss[1])
prarraynlss = c(prrt1ss[2], prrt2ss[2], prrt3ss[2], prrt4ss[2], prrt5ss[2], prrt6ss[2],
                prrt7ss[2],  prrt8ss[2])

prarraysl = c(prrt1sl[1], prrt2sl[1], prrt3sl[1], prrt4sl[1], prrt5sl[1], prrt6sl[1],
              prrt7sl[1], prrt8sl[1])
prarraynlsl = c(prrt1sl[2], prrt2sl[2], prrt3sl[2], prrt4sl[2], prrt5sl[2], prrt6sl[2],
                prrt7sl[2],  prrt8sl[2])

prrt1 = apply(rt1, 2, mean)
prrt2 = apply(rt2, 2, mean)
prrt3 = apply(rt3, 2, mean)
prrt4 = apply(rt4, 2, mean)
prrt5 = apply(rt5, 2, mean)
prrt6 = apply(rt6, 2, mean)
prrt7 = apply(rt7, 2, mean)
prrt8 = apply(rt8, 2, mean)

t.test(rt1[,2], rt2[,2], paired=T, alternative="less")
t.test(rt2[,2], rt3[,2], paired=T, alternative="less")
t.test(rt3[,2], rt4[,2], paired=T, alternative="less")
t.test(rt4[,2], rt5[,2], paired=T, alternative="less")
t.test(rt5[,2], rt6[,2], paired=T, alternative="less")
t.test(rt6[,2], rt7[,2], paired=T, alternative="less")
t.test(rt7[,2], rt8[,2], paired=T, alternative="less")
t.test(rt8[,1], rt8[,2], paired=T)


prarray = c(prrt1[1], prrt2[1], prrt3[1], prrt4[1], prrt5[1], prrt6[1], prrt7[1],
            prrt8[1])
prarraynl = c(prrt1[2], prrt2[2], prrt3[2], prrt4[2], prrt5[2], prrt6[2], prrt7[2],
              prrt8[2])
prarraynr = c(1:8)
plot(prarraynr, prarray, type="l", col="blue", frame=F, xlab="Word",
     ylab="Time to response", ylim=c(4000, 17000),
     main="Reaction Time per Language Version and Word")
points(prarraynr, prarraynl,  type = "l", col="red")
legend("topleft", c("English", "Dutch"), col=c("blue", "red"), lty=1, cex=.7)


plot(prarraynr, prarray, type="l", col="blue", frame=F, xlab="Word",
     ylab="Time to response", ylim=c(4000, 17000),
     main="Reaction Time per Language Version and Word")
points(prarraynr, prarraynl,  type = "l", col="red")
points(prarraynr, prarrayss,  type = "l", col="blue", lty=2)
points(prarraynr, prarraynlss,  type = "l", col="red", lty=2)
points(prarraynr, prarraysl,  type = "l", col="blue", lty=3)
points(prarraynr, prarraynlsl,  type = "l", col="red", lty=3)

legend("right", c("English", "Dutch"), col=c("blue", "red"), lty=1, cex=.7)


all = rbind(delta2, delta3)
all = rbind(all, delta4)
all = rbind(all, delta5)
all = rbind(all, delta6)
all = rbind(all, delta7)
all = rbind(all, delta8)

all_EN = as.data.frame(all[,1])
all_NL = as.data.frame(all[,2])

all_EN$word = rep(2:8, each=15)
all_NL$word = rep(2:8, each=15)

names(all_EN) = list("EN", "word")
names(all_NL) = list("NL", "word")
plot(tapply(all_EN$EN, all_EN$word, mean), type="p", col="blue")
points(tapply(all_NL$NL, all_NL$word, mean), type="p", col="red")