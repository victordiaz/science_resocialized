library(car)
library(ez)

datafile = "OSF-Farrell-results-csv.csv"

input = read.csv(datafile, header=T)
perTrial = 6
trials = 80
latencyIndex = 16

# How many subjects?
nSubj = dim(input)[1]/trials

# Get only the timing trials with Rhythm. == 1, or only order with Rhythm == 0
rhythm = 0
d = subset(input, Rhythm. == rhythm)

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


# run the ANOVA
a1 = aov(avgLatency ~ (index*grouped) + Error(subj / (index*grouped)), data=f)

# generate plot
with(f, interaction.plot(index, grouped, avgLatency, type="b"))

# this does the same thing, but with the car package, just to test
m = lm(avgLatency~ (index*grouped) + Error(subj / (index*grouped)), data=f)
a2 = Anova(m)

# Ideally, we'd have a Greenhouse-Geisser correction at this point
# But for now that is an eternal "TODO"

# For each subject, fit a quadratic to 2 3 5 6 in grouped, ungrouped conditions

item = 3 # which item to exclude and look at deviation of - MODIFY ME to look at fourth item instead

x = 2:6
x = x[x != item]
ngToFit = nogrouplatencies[x]
gToFit = grouplatencies[x]

participants = unique(nogroup["Subject"])

devs_ng = rep(0, nrow(participants)) # fill these in later
devs_g = rep(0, nrow(participants))

col = paste("Out.sec.", item, sep="")

for(i in 1:nrow(participants)) {
	participant = participants[i,]
	yn =  unlist(ngToFit[i,])
	fitng = lm(yn ~ poly(x, 2))
	yg =  unlist(gToFit[i,])
	fitg = lm(yg ~ poly(x, 2))

	# what's the predicted nth item?
	png = predict(fitng, data.frame(x=item))
	pg = predict(fitg, data.frame(x=item))

	# For each subject, grab the average deviation of item n in grouped, ungrouped conditions
	fourths_ng = nogroup[c("Subject", col)]
	sub_ng = subset(fourths_ng, Subject==participant)[col]
	devs_ng[i] = mean(unlist(sub_ng - png))

	fourths_g = group[c("Subject", col)]
	sub_g = subset(fourths_g, Subject==participant)[col]
	devs_g[i] = mean(unlist(sub_g - pg))
}

print(paste("Done. Rhythm condition:", rhythm, " Item removed:", item))
# Run a t-test on these 30-odd item-4 averages between grouped and ungrouped conditions
result = t.test(x=devs_g, y=devs_ng, paired=TRUE)

cohens_d = (mean(devs_g) - mean(devs_ng)) / sqrt((sd(devs_g)^2 + sd(devs_ng)^2) / 2.0)

##### Accuracy #####
o = subset(input, Rhythm. == 0)
o = subset(o, Subject!= 1 & Subject!= 2 & Subject!= 3 & Subject!= 5 & Subject!= 6) # no data here

nogroup = subset(o, Grouped. == 0)
group = subset(o, Grouped. == 1)

subjIds = unique(o["Subject"])
nSubj = dim(subjIds)[1]

ng_correct = (nogroup[28:33]==nogroup[34:39])
g_correct = (group[28:33]==group[34:39])

nogroupaccuracies = data.frame(colMeans(matrix(data = ng_correct[,1], ncol = nSubj)),
			colMeans(matrix(data = ng_correct[,2], ncol = nSubj)),
			colMeans(matrix(data = ng_correct[,3], ncol = nSubj)),
			colMeans(matrix(data = ng_correct[,4], ncol = nSubj)),
			colMeans(matrix(data = ng_correct[,5], ncol = nSubj)),
			colMeans(matrix(data = ng_correct[,6], ncol = nSubj)))

groupaccuracies = data.frame(colMeans(matrix(data = g_correct[,1], ncol = nSubj)),
			colMeans(matrix(data = g_correct[,2], ncol = nSubj)),
			colMeans(matrix(data = g_correct[,3], ncol = nSubj)),
			colMeans(matrix(data = g_correct[,4], ncol = nSubj)),
			colMeans(matrix(data = g_correct[,5], ncol = nSubj)),
			colMeans(matrix(data = g_correct[,6], ncol = nSubj)))


# set up another dataframe, with subj number, index, accuracy
g = data.frame(subj = rep(unlist(subjIds), each=perTrial),
	index = 1:perTrial,
	grouped = rep(0:1, each=nSubj*perTrial),
	avgAccuracy = c(as.vector(t(nogroupaccuracies )),as.vector(t(groupaccuracies ))))
g = transform(g, index=factor(index))
g = transform(g, subj=factor(subj))

# run the ANOVA
a3 = aov(avgAccuracy ~ (index*grouped) + Error(subj / (index*grouped)), data=g)

# generate plot
with(g, interaction.plot(index, grouped, avgAccuracy, type="b"))



#### FIDDLING with EZ ####

a4 = ezANOVA(data=f, dv=.(avgLatency), wid=.(subj), within=.(index,grouped))

