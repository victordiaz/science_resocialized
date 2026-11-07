# S06 analysis. Run from the S06 run directory:
#   /opt/homebrew/bin/Rscript papers/S06/report/analysis.R > papers/S06/report/analysis.out
d <- read.csv("papers/S06/data/d11.csv", stringsAsFactors = FALSE)
cat("Rows:", nrow(d), " IDs:", length(unique(d$ID)), " missing PD:", sum(is.na(d$PD)), "\n")
print(table(d$HiLoCat, d$Task))
cat("Participants per group:\n"); print(table(d$HiLoCat[!duplicated(d$ID)]))
d$ID <- factor(d$ID); d$Group <- factor(d$HiLoCat, levels = c("HighIMSLowEMS","HighIMSHighEMS"))
d$Task <- factor(d$Task, levels = c("Weapons","Flankers"))

# Consistency check against wide file d12
w <- read.csv("papers/S06/data/d12.csv")
cat("d12 rows:", nrow(w), "\n")
m <- merge(w, d[d$Task=="Weapons" & d$TrialType=="Black", c("ID","PD")], by="ID")
cat("max |d12 weaponsBlack - d11|:", max(abs(m$weaponsPDControlBlack - m$PD)), "\n")

cat("\n== Descriptives: mean (SD) PD by Group x Task (Weapons rows pooled) ==\n")
print(aggregate(PD ~ Group + Task, d, function(x) c(mean=mean(x), sd=sd(x), n=length(x))))
cat("\nBy Group x TrialType:\n")
d$Cell <- ifelse(d$Task=="Weapons", paste0("Weapons-", d$TrialType), "Flankers")
print(aggregate(PD ~ Group + Cell, d, function(x) round(c(mean=mean(x), sd=sd(x)),4)))

cat("\n== PRIMARY: aov(PD ~ Group * Task + Error(ID/Task)) ==\n")
fit <- aov(PD ~ Group * Task + Error(ID/Task), data = d)
s <- summary(fit); print(s)
st <- s[["Error: ID:Task"]][[1]]; rn <- trimws(rownames(st))
iF <- st[rn=="Group:Task","F value"]; idf1 <- st[rn=="Group:Task","Df"]; idf2 <- st[rn=="Residuals","Df"]
ip <- st[rn=="Group:Task","Pr(>F)"]
ssi <- st[rn=="Group:Task","Sum Sq"]; ssr <- st[rn=="Residuals","Sum Sq"]
pes <- ssi/(ssi+ssr)
# CI for partial eta^2 via noncentral F (lambda inversion)
ncp_ci <- function(Fv, df1, df2, conf) {
  a <- (1-conf)/2
  f <- function(l, p) pf(Fv, df1, df2, ncp=l) - p
  lo <- if (pf(Fv, df1, df2) < 1-a) 0 else uniroot(f, c(0, 1000), p=1-a)$root
  hi <- if (pf(Fv, df1, df2) < a) 0 else uniroot(f, c(0, 1000), p=a)$root
  c(lo, hi)
}
toeta <- function(l, df1, df2) l/(l+df1+df2+1)
ci90 <- toeta(ncp_ci(iF, idf1, idf2, .90), idf1, idf2)
ci95 <- toeta(ncp_ci(iF, idf1, idf2, .95), idf1, idf2)
cat(sprintf("\nGroup x Task: F(%d, %d) = %.3f, p = %.4f, partial eta^2 = %.4f, 90%% CI [%.3f, %.3f], 95%% CI [%.3f, %.3f]\n",
            idf1, idf2, iF, ip, pes, ci90[1], ci90[2], ci95[1], ci95[2]))

# Direction: per-participant Weapons mean, Flankers; difference score
wm <- aggregate(PD ~ ID + Group, d[d$Task=="Weapons",], mean); names(wm)[3] <- "W"
fl <- d[d$Task=="Flankers", c("ID","PD")]; names(fl)[2] <- "F"
pp <- merge(wm, fl, by="ID"); pp$diff <- pp$W - pp$F
gm <- aggregate(cbind(W,F,diff) ~ Group, pp, mean); print(gm)
gW <- gm$W[1]-gm$W[2]; gF <- gm$F[1]-gm$F[2]
cat(sprintf("Group difference (HI/LE - HI/HE): Weapons %.4f, Flankers %.4f; interaction contrast %.4f\n", gW, gF, gW-gF))

cat("\n== CHECK 1: 2x2 mixed ANOVA on Weapons mean vs Flankers ==\n")
long2 <- rbind(data.frame(ID=pp$ID, Group=pp$Group, Task="Weapons", PD=pp$W),
               data.frame(ID=pp$ID, Group=pp$Group, Task="Flankers", PD=pp$F))
long2$Task <- factor(long2$Task)
print(summary(aov(PD ~ Group * Task + Error(ID/Task), data = long2)))
tt <- t.test(diff ~ Group, data = pp, var.equal = TRUE)
cat(sprintf("Equivalent t on (Weapons mean - Flankers): t(%d) = %.3f, p = %.4f, mean diff (HI/LE - HI/HE) = %.4f, 95%% CI [%.4f, %.4f]\n",
            as.integer(tt$parameter), tt$statistic, tt$p.value, -diff(tt$estimate), tt$conf.int[1], tt$conf.int[2]))

cat("\n== CHECK 2: simple group effects per task (Welch) ==\n")
for (v in c("W","F")) { t2 <- t.test(pp[[v]] ~ pp$Group)
  cat(sprintf("%s: t(%.1f) = %.3f, p = %.4f, diff = %.4f\n", v, t2$parameter, t2$statistic, t2$p.value, -diff(t2$estimate))) }
for (tt2 in c("Black","White")) { x <- d[d$Task=="Weapons" & d$TrialType==tt2,]; t2 <- t.test(PD ~ Group, x)
  cat(sprintf("Weapons-%s: t(%.1f) = %.3f, p = %.4f, diff = %.4f\n", tt2, t2$parameter, t2$statistic, t2$p.value, -diff(t2$estimate))) }

cat("\n== CHECK 3: nonparametric, Wilcoxon on difference score ==\n")
print(wilcox.test(diff ~ Group, data = pp, exact = FALSE))

png("papers/S06/report/fig1.png", width = 900, height = 600, res = 130)
se <- function(x) sd(x)/sqrt(length(x))
mm <- rbind(tapply(pp$W, pp$Group, mean), tapply(pp$F, pp$Group, mean))
ss <- rbind(tapply(pp$W, pp$Group, se), tapply(pp$F, pp$Group, se))
b <- barplot(mm, beside = TRUE, ylim = c(0, 1), names.arg = c("High int / low ext", "High int / high ext"),
             legend.text = c("Gun/tool (Weapons, mean of Black & White)", "Race-neutral (Flankers)"),
             args.legend = list(x = "topright", bty = "n", cex = .8), ylab = "PD control estimate", col = c("grey35","grey75"))
arrows(b, mm-ss, b, mm+ss, angle = 90, code = 3, length = .04)
dev.off()
