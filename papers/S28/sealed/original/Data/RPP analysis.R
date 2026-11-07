################################################################################################################### 
# Title: RPP analysis
# Author: David Reinhard (reinhard@email.virginia.edu)
# Creation Date: Mon Jan  5 11:34:16 2015
# Last Edit: Fri Feb  6 12:48:10 2015
###################################################################################################################

###################################################################################################################
# Set up
###################################################################################################################

dat_full <- read.csv("RPP data.csv") # All participants that completed the study.
dat <- subset(dat_full, discard == 0) # Eligible participants for analysis. 

###################################################################################################################
# Packages and functions used
###################################################################################################################

source('functions.R') # Reads in 'functions.R' file. Used for the "summarySE" function.
require(car) # Used for ANOVA.
require(ggplot2) # Used for ggplot graphing.

###################################################################################################################
# Actual sample statistics
###################################################################################################################

# Gender of participants that completed the study.
table(dat_full$gender)

# Gender of eligible participants.
table(dat$gender)

###################################################################################################################
# Confirmatory Analysis
###################################################################################################################

# Correlation between aggression questions 
cor.test(dat$Q5, dat$Q8)

# Aggressiveness score by semantic priming condition
t.test(aggressivenessScore ~ puzzleCondition, dat, var.equal = T)
summarySE(dat, measurevar = "aggressivenessScore", groupvars = "puzzleCondition")

# Aggressiveness score by processing style condition
options(contrasts=c("contr.sum", "contr.poly"))
aov_processingAggressive <- aov(aggressivenessScore ~ mapCondition, dat)
Anova(aov_processingAggressive, type = "III")

summarySE(dat, measurevar = "aggressivenessScore", groupvars = "mapCondition")

# Target analysis: Interaction between processing style and semantic priming
options(contrasts=c("contr.sum", "contr.poly"))
aov_target <- aov(aggressivenessScore ~ mapCondition*puzzleCondition, dat)
Anova(aov_target, type = "III")

print(table_aggression.map.puzzle <- summarySE(dat, measurevar = "aggressivenessScore", groupvars = c("mapCondition", "puzzleCondition")))

ggplot(table_aggression.map.puzzle, aes(x=mapCondition, y=aggressivenessScore, fill=puzzleCondition)) + 
  geom_bar(stat="identity", position = position_dodge()) +
  geom_errorbar(aes(ymin=aggressivenessScore-se, ymax=aggressivenessScore+se), width=.2, position = position_dodge(.9)) + 
  labs(x = "Processing style", y = "Aggressiveness Score") +
  theme(text = element_text(size = 16)) +
  scale_fill_discrete(name="Semantic\nPriming")

###################################################################################################################
# Exploratory Analysis
###################################################################################################################

# Interaction between processing style and semantic priming on Question 5
options(contrasts=c("contr.sum", "contr.poly"))
aov_q5.interaction <- aov(Q5 ~ mapCondition*puzzleCondition, dat)
Anova(aov_q5.interaction, type = "III")

# Interaction between processing style and semantic priming on Question 8
options(contrasts=c("contr.sum", "contr.poly"))
aov_q5.interaction <- aov(Q8 ~ mapCondition*puzzleCondition, dat)
Anova(aov_q5.interaction, type = "III")

# Match between condition and reported processing style
table(dat$conditionMatch)

# Interaction between reported processing style and semantic priming
dat_focus.interaction <- subset(dat, PID != "22")
options(contrasts=c("contr.sum", "contr.poly"))
aov_focus.interaction <- aov(aggressivenessScore ~ focusCondition*puzzleCondition, dat_focus.interaction)
Anova(aov_focus.interaction, type = "III")

