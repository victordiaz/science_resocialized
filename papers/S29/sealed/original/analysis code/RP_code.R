setwd("your_directory_here")
data <- read.csv("rp.csv", header=TRUE)
library(plyr)
library(ez)
library(ggplot2)
library(outliers)
options(contrasts=c("contr.sum","contr.poly"))

#ERN EPS correlation, narrowed to one trial type for appropriate DF
cor.test(data[data$startle_type=="error",]$ERN,data[data$startle_type=="error",]$EPS)



#mean errors made
mean(data[data$startle_type=="error",]$errors)

#standard deviation errors made
sd(data[data$startle_type=="error",]$errors)

########
#correlation analysis
###########
 dfdata <- data[data$startle_type=="error",]
> plot <- ggplot(dfdata, aes(x=ERN, y=EPS))
> plot <- plot + geom_point(shape=19) + geom_smooth(method=lm, se=FALSE)
> plot


##########################################################################