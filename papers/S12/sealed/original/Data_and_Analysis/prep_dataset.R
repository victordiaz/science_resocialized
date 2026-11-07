# this file reshapes and merges all of the datasets except for the IAT into one and sets some important flags. 
# It does not perform any exclusions except for seriously corrupted records. 


ie<-read.csv("explicit.txt", sep = "\t")
library("reshape2")
ie$ukey<-paste0(ie$session_id, ie$question_name)
dups<-table(ie$ukey)[table(ie$ukey)>1]
nrow(ie)
#these duplicates 1) are rare, 2) make no sense, and 3) in some cases may be from a completely different study! Remove. 
ie<-ie[!ie$ukey %in% rownames(dups),]
nrow(ie)

eie<-dcast(ie, session_id ~ question_name, value.var="question_response")
ses<-read.csv("sessions.txt", sep="\t")

sts<-read.csv("sessionTasks.txt", sep="\t")
sts$task_id<-as.character(sts$task_id)
cnds<-sts[grep("^cnd", sts$task_id),][c("session_id", "task_id", "session_date", "user_id")]
names(cnds)[2]<-"cond"

iats<-sts[grep("(BI|RV)(Boy|Girl)[AB][12]*_?", sts$task_id),][c("session_id", "task_id")]
names(iats)[2]<-"iat"

nrow(cnds)
nrow(iats)

cnds<-merge(cnds, iats, by="session_id", all=T)

cndnames<-unique(cnds$cond)
cndnames<-cndnames[order(cndnames)]
reemgood<-c(rep(c(1,1,1,1,0,0,0,0),2))
rateorig<-c(rep(1,8),rep(0,8))
swap<-rep(c(0,1),8)
sex<-rep(c(1,1,0,0),4)
fupcond<-c(rep(c("odd", "odd", "even", "even"), 4))
codes<-data.frame(cond=cndnames, rateorig=rateorig, reemgood=reemgood, sex=sex, swap=swap, fupcond=fupcond)
cnds<-merge(cnds, codes, by="cond")

eie<-merge(eie, cnds,  by="session_id")

names(eie)<-tolower(names(eie))

for(var in c("friendly", "like", "likeable", "popular", "pleasant", "responsible")){
    for(pers in c("v", "b", "r", "i")){
        pvar<-paste0(pers, var)
        eie[,pvar]<-as.numeric(eie[,pvar])
    }
}
#ignore warnings, they're just about NAs

eie$reemleft[grep("[yl]A", eie$iat)]<-1
eie$reemleft[grep("[yl]B", eie$iat)]<-0

eie$date<-strptime(eie$session_date, format="%d%b%Y %H:%M:%S")

# the instructions were reversed for some conditions (i.e., it said "press E for vabbenif" even though V was on the right and they had to press I)
# this was fixed with the source push on 12/08
eie$instructions_correct<-0
eie$instructions_correct[eie$date>strptime("2014-12-09 00:00:00", format="%Y-%m-%d")]<-1
eie$instructions_correct[-grep("RVGirlB", eie$iat)]<-1

#feedback was reversed (at end of study, ppl were told they preferred the wrong person) in all IAT setups ending in A
# This was fixed with the source push on 12/18.
eie$feedback_correct<-1
eie$feedback_correct[grep("[yl]A", eie$iat)]<-0
eie$feedback_correct[eie$date>strptime("2014-12-19 00:00:00", format="%Y-%m-%d")]<-1

names(eie)[names(eie)=="sex.y"]<-"target_sex"


# finally, merge in demographics

dem<-read.csv("demographics.txt", sep="\t")
dem<-dem[1:3]
dem$uid<-paste0(dem$user_id, dem$characteristic)
z<-table(dem$uid)

# ONE PARTICIPANT has duplicate demographics. 
dups<-row.names(z[z>1])
for(dup in dups) {
    dem<-dem[-which(dem$uid==dup)[1],]
}

deme<-dcast(dem, "user_id ~ characteristic", value.var="value")
head(deme$user_id)
head(eie$user_id)
duid<-deme$user_id
euid<-eie$user_id
length(duid)
length(euid)
sum(euid %in% duid)
euid[!euid %in% duid]




# okay, they're all there (except one, whose id is -1 and has no data.)
names(deme)[names(deme)=="sex"]<-"demog_sex"
exp<-merge(eie, deme, by="user_id", all.x=T)
# compute explicit scores
# we will exclude people who did not respond to all questions, so DON'T use na.rm
exp$rexp<-rowMeans(exp[c("rfriendly", "rlike", "rlikeable", "rpleasant", "rpopular", "rresponsible")])
exp$iexp<-rowMeans(exp[c("ifriendly", "ilike", "ilikeable", "ipleasant", "ipopular", "iresponsible")])
exp$bexp<-rowMeans(exp[c("bfriendly", "blike", "blikeable", "bpleasant", "bpopular", "bresponsible")])
exp$vexp<-rowMeans(exp[c("vfriendly", "vlike", "vlikeable", "vpleasant", "vpopular", "vresponsible")])
exp[c("rfriendly", "rlike", "rlikeable", "rpleasant", "rpopular", "rresponsible", "rexp")][1:20,]

#even though some people did the IAT multiple times, they did not do the explicit part of the study multiple times.
z<-table(exp$user_id)
z[z>1]


exp$lexp<-ifelse(is.na(exp$rexp), exp$bexp, exp$rexp)
exp$nexp<-ifelse(is.na(exp$iexp), exp$vexp, exp$iexp)
sum(is.na(exp$lexp))
sum(is.na(exp$nexp))

exp$exppref<-ifelse(exp$reemgood, exp$lexp-exp$nexp, exp$nexp-exp$lexp)
summary(lm(exppref ~ reemgood, data=exp))

exp$expgood<-ifelse(exp$reemgood, exp$lexp, exp$nexp)
exp$expbad<-ifelse(exp$reemgood, exp$nexp, exp$lexp)


exp$lpref<-exp$lexp-exp$nexp
summary(lm(lpref ~ reemgood, data=exp))
describe(exp$exppref)
