library(foreign)
library(plyr)

orig_data <- read.spss(file = "/Users/Courtney/Desktop/Melvin.sav", to.data.frame = T)

means <- c(mean(orig_data$chf.mu), mean(orig_data$clf.mu), mean(orig_data$dhf.mu), mean(orig_data$dlf.mu))
sds <- c(sd(orig_data$chf.mu), sd(orig_data$clf.mu), sd(orig_data$dhf.mu), sd(orig_data$dlf.mu))
cor_matrix <- matrix(c(cor(orig_data$chf.mu, orig_data$chf.mu), cor(orig_data$chf.mu, orig_data$clf.mu), cor(orig_data$chf.mu, orig_data$dhf.mu), cor(orig_data$chf.mu, orig_data$dlf.mu), 
                       cor(orig_data$clf.mu, orig_data$chf.mu), cor(orig_data$clf.mu, orig_data$clf.mu), cor(orig_data$clf.mu, orig_data$dhf.mu), cor(orig_data$clf.mu, orig_data$dlf.mu), 
                       cor(orig_data$dhf.mu, orig_data$chf.mu), cor(orig_data$dhf.mu, orig_data$clf.mu), cor(orig_data$dhf.mu, orig_data$dhf.mu), cor(orig_data$dhf.mu, orig_data$dlf.mu), 
                       cor(orig_data$dlf.mu, orig_data$chf.mu), cor(orig_data$dlf.mu, orig_data$clf.mu), cor(orig_data$dlf.mu, orig_data$dhf.mu), cor(orig_data$dlf.mu,orig_data$dlf.mu)))