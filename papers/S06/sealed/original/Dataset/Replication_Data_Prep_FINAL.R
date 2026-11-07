#Replication Data Prep FINAL

flankers <- read.csv("~/Dropbox/Replication Stuff/JenniferData/Flanker.csv", header=T)
head(flankers)

#Remove NA rows
flankers<-flankers[!is.na(flankers$subject),]

weapons <- read.csv("~/Dropbox/Replication Stuff/JenniferData/Weapons.csv", header=T)

#Remove NA rows
weapons <- weapons[!is.na(weapons$subject),]

#labels from previous output from DMDX utils

# [1] "subj"    "desc"    "itemN"   "trial"   "rt"      "error"   "prevRT"  "prevERR" "prevYES" "itemERR" "subjERR" "ID"

#current labels
colnames(flankers)
colnames(weapons)

#[1] "subject" "ID"      "item"    "RT"


#Change colnames to be consistent with previous analyses from utils.
colnames(flankers)[1] = "subj" 
colnames(weapons)[1] = "subj"

colnames(flankers)[3] = "itemN"
colnames(weapons)[3] =  "itemN"

colnames(flankers)[4] = "rt"
colnames(weapons)[4] = "rt"


#Remove test trials (trials performed by researchers/staff but logged by DMDX - not actual subjects)
flankers <- flankers[flankers$ID != "jesse" & flankers$ID !="No ID",]
weapons <- weapons[weapons$ID !="0x5" & weapons$ID != "No ID",]


#Save intermediate Datasets
write.csv(weapons, "~/Dropbox/Replication Stuff/JenniferData/Data New/No Character IDs/weaponsIDNew")
write.csv(flankers, "~/Dropbox/Replication Stuff/JenniferData/Data New/No Character IDs/flankersIDNew")

#Read in intermediate datasets (necessary for minor reasons concerning treating numeric vectors appropriately after removing previous character strings)
flankers <- read.csv("~/Dropbox/Replication Stuff/JenniferData/Data New/No Character IDs/flankersIDNew", header=T)
weapons <- read.csv("~/Dropbox/Replication Stuff/JenniferData/Data New/No Character IDs/weaponsIDNew", header=T)

#Remove superfluous first column added to .csv files
flankers <- flankers[,-1]
weapons <- weapons[,-1]


#Identify task in data set
weapons$Task = rep("weapons", nrow(weapons))
flankers$Task = rep("flankers", nrow(flankers))


#Get rid of nonessential trials
weapons = weapons[weapons$itemN <601,]
unique(weapons$itemN) #check

flankers = flankers[flankers$itemN != 999,]
unique(flankers$itemN) #check


#Add trial type
weapons$TrialType = ifelse(weapons$itemN <=86, "WhiteGun", ifelse(weapons$itemN <= 166, "BlackGun", ifelse(weapons$itemN <= 246, "WhiteTool", "BlackTool")))


flankers$TrialType = ifelse(flankers$itemN == 1, "CongruentRight", ifelse(flankers$itemN == 2, "CongruentLeft", ifelse(flankers$itemN == 3, "IncongruentLeft", ifelse(flankers$itemN == 4, "IncongruentRight", ifelse(flankers$itemN == 5, "NoGoLeft", "NoGoRight")))))

#Remove No-Go trials
flankers = flankers[flankers$itemN <5,]

#Create Congruent/Incongruent Flankers Variable
flankers$CongruentIncongruent = ifelse(flankers$TrialType == "CongruentRight" | flankers$TrialType == "CongruentLeft", "Congruent", "Incongruent" )

flankers[,c("TrialType", "CongruentIncongruent")]

#Create Error Vectors (based on sign of response, as indicated by Amodio and confirmed by DMDX documentation)
weapons$subjERR = ifelse(weapons$rt <0, 1, 0)
flankers$subjERR = ifelse(flankers$rt <0, 1, 0)

length(unique(weapons$ID)) #113
length(unique(flankers$ID)) #118

#-------------------#
# Manual Exclusions	#
#-------------------#
range(flankers$rt)
#[1] -1200  1200

range(weapons$rt)
#[1] -2000.00  1977.13

#exclude trials below 250 mil and above 1500
flankers <- flankers[abs(flankers$rt) > 250 & abs(flankers$rt) < 1500,]


weapons <- weapons[abs(weapons$rt) > 250 & abs(weapons$rt) < 1500,]


#Source data cleaning functions
#These are same basic data cleaning functions written by one of the authors of this replication (Hayes)
#Please contact me directly to request a copy of the functions used here.

source("~/Dropbox/Mac Documents/274/PSYC274 Fall 2011/Finalized_Labs_for_PSYC274/Function Writing/TH Functions Complete.R")

#Absolute value RT variables
weapons$absRT <- abs(weapons$rt)
flankers$absRT <- abs(flankers$rt)

#Remove Outliers Greater Than 3 SDs within experimental group
#(Note: Can also ignore grouping and remove outliers, and I believe this also leads to a similar pattern of results)

weaponsOUT <- OutByGroup(weapons, groups = "TrialType", cutoff=3, Subset="absRT")
length(weaponsOUT$Out.ID$absRT.RM) #251

#Retrieve full data set with outliers removed
weapons=OutByGroup(weapons, groups = "TrialType", cutoff=3, Subset="absRT")$FullData

#absRT scores are set equal to absRT with outliers removed (.RM)
weapons$absRT <- weapons$absRT.RM
weapons <- weapons[!is.na(weapons$absRT),]
weapons$absRT.RM <- NULL

length(OutByGroup(flankers,"TrialType", 3, "absRT")$Out.ID$absRT.RM) #0
which(flankers$rt == -1200)
flankers <- flankers[abs(flankers$rt) != 1200, ]
length(OutByGroup(flankers,"TrialType", 3, "absRT")$Out.ID$rt.RM) #0


flankers <- OutByGroup(flankers,"TrialType", 3, "absRT")$FullData
flankers$absRT <-flankers$absRT.RM
flankers$absRT.RM <- NULL
flankers <- flankers[!is.na(flankers$absRT),]


#Remove cases with > 85% error rates in Incongruent Flankers Trials

Incongruent <- flankers[flankers$CongruentIncongruent == "Incongruent", ]
IncongruentErrors <- round(tapply(Incongruent$subjERR, Incongruent$ID, function(x) length(which(x==1))/length(x)),2)
IncongruentErrors
length(IncongruentErrors)#107
length(which(IncongruentErrors > .85))#1
which(IncongruentErrors > .85)
#112 
# 96 

flankers <- flankers[flankers$ID != 112, ]


#ID.rm<-as.numeric(names(IncongruentErrors)[which(IncongruentErrors > .85)])

#?match

#which(flankers$ID %in% ID.rm)

#sort(unique(flankers$ID[flankers$ID %in% ID.rm==F]))

#flankers<-flankers[flankers$ID %in% ID.rm==F,]

#weapons$ID %in% ID.rm

#sort(unique(weapons$ID[weapons$ID %in% ID.rm==F]))

#remove identical cases from weapons
#weapons <- weapons[weapons$ID %in% ID.rm==F,]

length(unique(weapons$ID)) #113
length(unique(flankers$ID)) #106

colnames(flankers)
colnames(weapons)


weapons$absRT <- NULL
flankers$absRT <- NULL

colnames(flankers)
colnames(weapons)

#-----------------------------------#
#	COMPUTE PD CONTROL ESTIMATES	#
#-----------------------------------#

#Change the name to correspond to a previous script
#This corresponds to names automatically given to DMDX utils.

weapons$error <- weapons$subjERR
weapons$subjERR <- NULL

flankers$error <- flankers$subjERR
flankers$subjERR <- NULL

#####################
#	Weapons Task	#
#####################

#Compute Total Error (Error coded 0/1, so sum of the vector in each cell = total error in that cell)
weaponsTotalError = tapply(weapons$error, list(weapons$ID, weapons$TrialType), sum, na.rm=T)
weaponsTotalError

#Double check
length(which(is.na(weapons$error)))
length(which(is.na(flankers$error)))

#
weaponsNumTrials = t(table(weapons$TrialType, weapons$ID))
weaponsTotalAccuracy = weaponsNumTrials - weaponsTotalError

#check
weaponsTotalError + weaponsTotalAccuracy == weaponsNumTrials #TRUE

#Compute Error Rate and Accuracy
weaponsErrorRate = weaponsTotalError/weaponsNumTrials
weaponsAccuracyRate = weaponsTotalAccuracy/weaponsNumTrials

#Checks 
all.equal(weaponsAccuracyRate[,1],  (1-weaponsErrorRate)[,1])
#[1] TRUE
all.equal(weaponsAccuracyRate[,2],  (1-weaponsErrorRate)[,2])
#[1] TRUE
all.equal(weaponsAccuracyRate[,3],  (1-weaponsErrorRate)[,3])
#[1] TRUE
all.equal(weaponsAccuracyRate[,4],  (1-weaponsErrorRate)[,4])
#[1] TRUE
 

#Compute PD Estimates as described by Amodio source article, and also Payne (2001)
weaponsPDControlBlack = weaponsAccuracyRate[,"BlackGun"] - weaponsErrorRate[,"BlackTool"]
weaponsPDControlBlack #check

weaponsPDControlWhite = weaponsAccuracyRate[,"WhiteGun"] - weaponsErrorRate[,"WhiteTool"]
weaponsPDControlWhite

#Check - ensure that row numbers and IDs align (including skipped)
#(It does, since the table() function sorted by ID, above)
cbind(sort(unique(weapons$ID)), weaponsPDControlBlack, weaponsPDControlWhite)

#Create PD file
weaponsPD = cbind(sort(unique(weapons$ID)), weaponsPDControlBlack, weaponsPDControlWhite)
#Rename ID variable
colnames(weaponsPD)[1] = "ID"
head(weaponsPD)
#Convert to Data Frame
weaponsPD = data.frame(weaponsPD)

#####################
#	Flankers Task   #
#####################

#Compute Total Error
flankersTotalError = tapply(flankers$error, list(flankers$ID, flankers$CongruentIncongruent), sum, na.rm=T)
flankersTotalError

#Double check
length(which(is.na(weapons$error)))
length(which(is.na(flankers$error)))

#Compute Total Number of Trials
flankersNumTrials = t(table(flankers$CongruentIncongruent, flankers$ID))
flankersNumTrials

#Compute Total Accuracy
flankersTotalAccuracy = flankersNumTrials - flankersTotalError

#check
flankersTotalError + flankersTotalAccuracy == flankersNumTrials #TRUE


#Compute Error and Accuracy Rates
flankersErrorRate = flankersTotalError/flankersNumTrials
flankersAccuracyRate = flankersTotalAccuracy/flankersNumTrials

#Checks
all.equal(flankersAccuracyRate[,1],  (1-flankersErrorRate)[,1])
#[1] TRUE
all.equal(flankersAccuracyRate[,2],  (1-flankersErrorRate)[,2])
#[1] TRUE
 
#Compute PD Control Estimates
#PAYNE (2001)
#C = Congruent - Incongruent
flankersPDControl = flankersAccuracyRate[,"Congruent"] - flankersErrorRate[,"Incongruent"]
flankersPDControl

#Check
#Once again, this aligns since IDs have been previously sorted by table function
cbind(sort(unique(flankers$ID)),flankersPDControl)

flankersPD = cbind(sort(unique(flankers$ID)),flankersPDControl)
colnames(flankersPD)[1] = "ID"

flankersPD = data.frame(flankersPD)
head(flankersPD)

#-------------------------------------#
#	MERGE WEAPONS PD AND FLANKERS PD  #
#-------------------------------------#

#Merge weapons and flankers PD dataframes into one dataframe
PD = merge(weaponsPD, flankersPD, "ID", all.x=T, all.y=T)
sort(weaponsPD$ID) %in% PD$ID


#Some checks to ensure the merging was accurate
PD$ID %in% sort(weaponsPD$ID)

PD[PD$ID %in% sort(weaponsPD$ID),]
PD[PD$ID %in% sort(flankersPD$ID),]

weaponsPD[,2:3] == PD[PD$ID %in% sort(weaponsPD$ID),2:3] #TRUE
flankersPD[,2] == PD[PD$ID %in% sort(flankersPD$ID), 4] #TRUE


#Import IMS/EMS Dataset
ims.ems=read.csv("~/Dropbox/Replication Stuff/replicationcrap/Replication study.csv", header=T)

head(ims.ems)
colnames(ims.ems)

#Q1.1 =15, Q1.23=37
#Q2.1 = 39, Q2.19 = 57
#Q3.1 = 59, Q3.10 = 68

#subset necessar vars
ims.ems=ims.ems[,c("PARTICIPANT..", "IMS", "EMS", "EMS.Cat..1.high.2.low.", "GENDER")]

#Rename  Important Columns
colnames(ims.ems)[1] = "ID"
colnames(ims.ems)[4] = "EMSCat" #1 high, 2 low

#Subset to only include High IMS/High EMS and High IMS/Low EMS Folks
ims.ems$HiLoCat = ifelse(is.na(ims.ems$EMSCat), NA, ifelse(ims.ems$EMSCat==1, "HighIMSHighEMS", "HighIMSLowEMS"))

#Which IDs from original prescreen survey are not in current data set?
ims.ems$ID %in% PD$ID==F
which(ims.ems$ID %in% PD$ID==F)

#Subsetting....
flag=ims.ems$ID %in% PD$ID==T

#Only matching IDs, please...
ims.ems=ims.ems[flag, ]


#Merge original prescreen survey (ims.ems) with PD dataset
repdata=merge(ims.ems, PD, "ID", all.x=T, all.y=T)

all.equal(repdata$weaponsPDControlBlack, PD$weaponsPDControlBlack) #true
all.equal(repdata$weaponsPDControlWhite, PD$weaponsPDControlWhite) #true
all.equal(repdata$flankersPDControl, PD$flankersPDControl) #true


length(unique(repdata$ID))
#[1] 119

#Get rid of missing values
repdata=na.omit(repdata)
length(unique(repdata$ID))
#[1] 76

#Save resulting Data File.
write.csv(repdata, "~/Dropbox/Replication Stuff/JenniferData/Data New/Merged Data/repdatawideNAOMIT.csv")



#NOW, to reshape for the long file for repeated measures analyses ....

head(repdata) #Okay, forget columns 2:4
repdata=repdata[,-c(2:4)]
colnames(repdata)

#rename for reshape function
#PD.1 ... PD.N notation because the reshape function breaks things up using the "."

colnames(repdata)[4:6] = paste("PD", 1:3, sep=".") #PD.1 = Black, PD.2 = White, PD.3 = Flankers
colnames(repdata)

repdatalong=reshape(repdata, varying = c("PD.1", "PD.2", "PD.3"), idvar="ID", timevar="Measure", direction="long")

head(repdatalong)

#Add Trial Type and Task Variables
repdatalong$TrialType = ifelse(repdatalong$Measure == 1, "Black", ifelse(repdatalong$Measure == 2, "White", "Flankers"))
repdatalong$Task = ifelse(repdatalong$TrialType == "Flankers", "Flankers", "Weapons")

#Some checks thaat this was conducting correctly
all.equal(repdata$PD.1, repdatalong[repdatalong$TrialType == "Black", "PD"])#TRUE

all.equal(repdata$PD.2, repdatalong[repdatalong$TrialType == "White", "PD"])#TRUE

all.equal(repdata$PD.3, repdatalong[repdatalong$TrialType == "Flankers", "PD"])#TRUE

#Save longfile
write.csv(repdatalong, "~/Dropbox/Replication Stuff/JenniferData/Data New/Merged Data/repdatalong.csv")

#################################################
# Additional Data Prep for Exploratory Analyses #
#################################################

write.csv(weapons, file="~/Dropbox/Replication Stuff/JenniferData/Data New/Weapons Flankers Separate/weapons.csv")
write.csv(flankers, file="~/Dropbox/Replication Stuff/JenniferData/Data New/Weapons Flankers Separate/flankers.csv")

weaponsErrorRateDF <- as.data.frame(weaponsErrorRate)
flankersErrorRateDF <- as.data.frame(flankersErrorRate)

colnames(weaponsErrorRateDF) <- c("ID", "TrialType", "ErrorRate")
colnames(flankersErrorRateDF) <- c("ID", "TrialType", "ErrorRate")

weaponsErrorRateDF$Prime <- as.factor(ifelse(weaponsErrorRateDF$TrialType == "WhiteGun" | weaponsErrorRateDF$TrialType == "WhiteTool", "White", "Black"))
weaponsErrorRateDF$Target <- as.factor(ifelse(weaponsErrorRateDF$TrialType == "WhiteGun" | weaponsErrorRateDF$TrialType == "BlackGun", "Gun", "Tool"))



