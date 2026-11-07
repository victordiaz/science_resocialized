#Run prep_dataset.R first. 



#set the working directory to the current file location.


# doing this rigamarole to remove extra spaces from the header of the file 
imtext<-readLines("iat.txt")
imtext[1]<-sub(" ", "", imtext[1])
write(imtext, "temp.csv")

im<-read.csv("temp.csv", sep="\t")

im$block_pairing_definition<-as.character(im$block_pairing_definition)
im$blocname<-NA
im$uncorrected_latency<-im$trial_latency

# this is some custom rearrangement ported from kate's procedure which makes the block numbers always correspond to which group is "good"
#NOTE: There's an off-by-one between the way blocks are referred to in the GNB paper + Kate's code and how they're numbered in the PI output. We are reconciling those so that our variable names are consistent with the former group. 

im$blocname[intersect(grep("Vabbenif/Good", im$block_pairing_definition) , which(im$block_number %in% c(2,5)))]<-"B3"
im$blocname[intersect(grep("Vabbenif/Good", im$block_pairing_definition) , which(im$block_number %in% c(3,6)))]<-"B4"
im$blocname[intersect(grep("Ibbonif/Good", im$block_pairing_definition) , which(im$block_number %in% c(2,5)))]<-"B3"
im$blocname[intersect(grep("Ibbonif/Good", im$block_pairing_definition) , which(im$block_number %in% c(3,6)))]<-"B4"
im$blocname[intersect(grep("Reemolap/Good", im$block_pairing_definition) , which(im$block_number %in% c(2,5)))]<-"B6"
im$blocname[intersect(grep("Reemolap/Good", im$block_pairing_definition) , which(im$block_number %in% c(3,6)))]<-"B7"
im$blocname[intersect(grep("Bosaalap/Good", im$block_pairing_definition) , which(im$block_number %in% c(2,5)))]<-"B6"
im$blocname[intersect(grep("Bosaalap/Good", im$block_pairing_definition) , which(im$block_number %in% c(3,6)))]<-"B7"

# This means that a negative d always corresponds to preferring Laapians over Niffians. 
# Later we will flip the sign for cases where the niffians were the good ones. 

im$tooslow<-im$trial_latency>10000 
im$toofast<-im$trial_latency<400
im$muchtoofast<-im$trial_latency<300
im$session_id<-factor(im$session_id)
iu<-data.frame(sid=im$session_id)

nrow(im)
length(levels(im$session_id))
table(im$toofast)


imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast | im$trial_error) & im$blocname=="B3",]
b3mean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
b3sd<-tapply(imuse$trial_latency, imuse$session_id, sd, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast | im$trial_error) & im$blocname=="B4",]
b4mean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
b4sd<-tapply(imuse$trial_latency, imuse$session_id, sd, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast | im$trial_error) & im$blocname=="B6",]
b6mean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
b6sd<-tapply(imuse$trial_latency, imuse$session_id, sd, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast | im$trial_error) & im$blocname=="B7",]
b7mean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
b7sd<-tapply(imuse$trial_latency, imuse$session_id, sd, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast | im$trial_error) & im$blocname %in% c("B3", "B6"),]
b36sd<-tapply(imuse$trial_latency, imuse$session_id, sd, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast | im$trial_error) & im$blocname %in% c("B4", "B7"),]
b47sd<-tapply(imuse$trial_latency, imuse$session_id, sd, na.rm=T)    
fastpct<-tapply(im$muchtoofast, im$session_id, function(x) {
    sum(x) / (sum(x) + sum(!x))
})

iu<-data.frame(session_id=row.names(b3mean), b3mean=b3mean, b4mean=b4mean, b6mean=b6mean, b7mean=b7mean, fastpct=fastpct, b3sd=b3sd, b6sd=b6sd, b36sd=b36sd, b4sd=b4sd, b7sd=b7sd, b47sd=b47sd)

# get trials per participant
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast | im$trial_error),]
validcorrecttrials<-tapply(imuse$trial_latency, imuse$session_id, length)    

imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast),]
validtrials<-tapply(imuse$trial_latency, imuse$session_id, length)    

imuse<-im[!is.na(im$blocname),]
alltrials<-tapply(imuse$trial_latency, imuse$session_id, length)    

imuse<-im
totallyalltrials<-tapply(imuse$trial_latency, imuse$session_id, length)    


temp4<-data.frame(alltrials=totallyalltrials, session_id=row.names(totallyalltrials))
temp1<-data.frame(trialcnt=alltrials, session_id=row.names(alltrials))
temp2<-data.frame(vtrialcnt=validtrials, session_id=row.names(validtrials))
temp3<-data.frame(vctrialcnt=validcorrecttrials, session_id=row.names(validcorrecttrials))
temp<-merge(temp1, temp2, by="session_id", all=T)
temp5<-merge(temp, temp3, by="session_id", all=T)
trialcnts<-merge(temp5, temp4, by="session_id", all=T)

length(alltrials)
sum(alltrials, na.rm=T)

length(totallyalltrials)
sum(totallyalltrials, na.rm=T)



# im[im$session_id==7579879,][c(1,4,8,11,12,13,14,15,16)]
# this one participant has an NA because they actually did not get a B7 at all, somehow. Or the data are missing. 


# Next, replace error means with block mean + 600ms


im<-merge(im, iu[c("session_id", "b3mean", "b4mean", "b6mean", "b7mean")], by="session_id", all=T)
im$trial_latency[!is.na(im$blocname) & im$trial_error & im$blocname=="B3"]<-
    im$b3mean[!is.na(im$blocname) & im$trial_error & im$blocname=="B3"] + 600
im$trial_latency[!is.na(im$blocname) & im$trial_error & im$blocname=="B4"]<-
    im$b4mean[!is.na(im$blocname) & im$trial_error & im$blocname=="B4"] + 600
im$trial_latency[!is.na(im$blocname) & im$trial_error & im$blocname=="B6"]<-
    im$b6mean[!is.na(im$blocname) & im$trial_error & im$blocname=="B6"] + 600
im$trial_latency[!is.na(im$blocname) & im$trial_error & im$blocname=="B7"]<-
    im$b7mean[!is.na(im$blocname) & im$trial_error & im$blocname=="B7"] + 600


imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast ) & im$blocname=="B3",]
b3cmean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast ) & im$blocname=="B4",]
b4cmean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast ) & im$blocname=="B6",]
b6cmean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
imuse<-im[!is.na(im$blocname) & !(im$tooslow | im$toofast ) & im$blocname=="B7",]
b7cmean<-tapply(imuse$trial_latency, imuse$session_id, mean, na.rm=T)    
temp<-data.frame(session_id=row.names(b3cmean), b3cmean=b3cmean, b4cmean=b4cmean, b6cmean=b6cmean, b7cmean=b7cmean)

iu<-merge(iu, temp, by="session_id", all=T)
iu<-merge(iu, trialcnts, by="session_id", all=T)

# names(iu)
# iu$trialcnt
# iu$vtrialcnt
# iu$vctrialcnt

# what's with the ps who have a trial count other than 120?
nrow(iu)
table(iu$alltrials)
iu$session_id[iu$trialcnt < 80]
# these appear to be ppl who quit partway through but somehow still had their data saved, or whose data was lost for later blocks.

iu$session_id[iu$trialcnt > 200]
im[c(1,2,9,11,12,16)][im$session_id==7632063 & im$block_number==0 & im$trial_number < 5 ,]
names(im)
table(iu$trialcnt)

iu$fastpct10<-0
iu$fastpct10[iu$fastpct >= .1]<-1
iu[c("fastpct", "fastpct10")]
# table(iu$fastpct10)
# names(iu)
# table(iu$trialcnt)

iu$b63diff<-iu$b6cmean-iu$b3cmean
iu$b74diff<-iu$b7cmean-iu$b4cmean
iu$b63d<-iu$b63diff/iu$b36sd
iu$b74d<-iu$b74diff/iu$b47sd
iu$d<-(iu$b63d + iu$b74d)/2
library(Hmisc)
describe(iu$d)

describe(iu$fastpct)

write.csv(iu, "iat_ps_processed.csv", row.names=F)

# delete scores for Ps who were too fast. In this case it's 63 ppl, most of whom had invalid results anyway.
table(is.na(iu$d))
iu$d[iu$fastpct>.1]<-NA
table(is.na(iu$d))

nrow(im)
nrow(iu)
table(im$toofast)
table(im$tooslow)

names(exp)[names(exp)=="d"]<-"pi_d"

# 190 Ps have some data, but not IAT data. ok. 

iu$session_id<-as.numeric(as.character(iu$session_id))
fie<-merge(iu, exp, by="session_id", all=T)
names(fie)

fie$pi_d<-as.numeric(fie$pi_d)


# create group pref variable so that high values = implicit preference for the group that was "good"
fie$imppref<-NA
fie$imppref[!is.na(fie$reemgood) & fie$reemgood]<-fie$d[!is.na(fie$reemgood) & fie$reemgood]*-1
fie$imppref[!is.na(fie$reemgood) & !fie$reemgood]<-fie$d[!is.na(fie$reemgood) & !fie$reemgood]
nrow(fie[is.na(fie$reemgood)!=is.na(fie$rateorig),])
nrow(fie[fie$reemgood==fie$rateorig,])
nrow(fie[fie$reemgood!=fie$rateorig,])

fie$d
table(is.na(fie$lexp))
table(is.na(fie$nexp))
table(is.na(fie$exppref))
nrow(fie)
library(psych)
names(fie)

write.csv(fie, "impex_final_dataset.csv", row.names=F)

# now, create the final dataset by excluding everyone who doesn't have a valid score on both measures. 
nrow(fie)
fin<-fie[!is.na(fie$exppref),]
nrow(fin)
fin<-fin[!is.na(fin$d),]
nrow(fin)
fin<-fin[fin$fastpct10==0,]
nrow(fin)
fin<-fin[fin$alltrials == 200,]
nrow(fin)
sum(fin$vtrialcnt)
sum(table(iu$alltrials[iu$alltrials>200]))

nrow(fin)
sum(fin$alltrials)



