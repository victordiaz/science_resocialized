"""S05 analysis: measure x target x SOA fixed-effects ANOVA on 720 values."""
import pandas as pd, numpy as np, subprocess, textwrap
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from scipy import stats, optimize

d = pd.read_csv("papers/S05/data/d04.csv")
d.columns = ["y", "measure", "target", "SOA", "subject"]
print("rows", len(d), "missing", int(d.isna().sum().sum()))
print("levels:", {c: sorted(d[c].unique().tolist()) for c in ["measure", "target", "SOA", "subject"]})
print("cell counts unique:", d.groupby(["measure", "target", "SOA"]).size().unique())
print("\nMeans by measure x target (over SOA, subjects):")
print(d.pivot_table(index="measure", columns="target", values="y", aggfunc="mean").round(4))
print("\nCell means measure x target x SOA:")
print(d.pivot_table(index=["measure", "target"], columns="SOA", values="y", aggfunc="mean").round(3).to_string())

# Primary: full factorial fixed-effects ANOVA, Type III, sum contrasts
m = smf.ols("y ~ C(measure, Sum) * C(target, Sum) * C(SOA, Sum)", data=d).fit()
a = anova_lm(m, typ=3)
print("\nPRIMARY: Type III ANOVA (fixed effects, participant not in model)")
print(a.round(5).to_string())
key = [i for i in a.index if i.count(":") == 2][0]
F = a.loc[key, "F"]; df1 = int(a.loc[key, "df"]); df2 = int(a.loc["Residual", "df"]); p = a.loc[key, "PR(>F)"]
pes = a.loc[key, "sum_sq"] / (a.loc[key, "sum_sq"] + a.loc["Residual", "sum_sq"])

def ncp_ci(F, df1, df2, level=0.95):
    lo_t, hi_t = (1 + level) / 2, (1 - level) / 2
    f = lambda nc, q: stats.ncf.cdf(F, df1, df2, nc) - q
    lo = 0.0 if f(0, lo_t) < 0 else optimize.brentq(f, 0, 1e4, args=(lo_t,))
    hi = 0.0 if f(0, hi_t) < 0 else optimize.brentq(f, 0, 1e4, args=(hi_t,))
    N = df1 + df2 + 1
    return lo / (lo + N), hi / (hi + N)
lo, hi = ncp_ci(F, df1, df2)
print(f"\nThree-way measure x target x SOA: F({df1}, {df2}) = {F:.3f}, p = {p:.3g}, partial eta^2 = {pes:.4f}, 95% CI [{lo:.4f}, {hi:.4f}]")

# Check 1: within-measure z-scored values (scale check)
d["z"] = d.groupby("measure")["y"].transform(lambda s: (s - s.mean()) / s.std())
az = anova_lm(smf.ols("z ~ C(measure, Sum) * C(target, Sum) * C(SOA, Sum)", data=d).fit(), typ=3)
kz = [i for i in az.index if i.count(":") == 2][0]
print(f"\nCHECK z-scored within measure: three-way F({int(az.loc[kz,'df'])}, {int(az.loc['Residual','df'])}) = {az.loc[kz,'F']:.3f}, p = {az.loc[kz,'PR(>F)']:.3g}")

# Check 2: per-measure target x SOA interaction (fixed effects)
print("\nCHECK per measure, target x SOA (fixed-effects, Type III):")
for mv, g in d.groupby("measure"):
    ag = anova_lm(smf.ols("y ~ C(target, Sum) * C(SOA, Sum)", data=g).fit(), typ=3)
    k = "C(target, Sum):C(SOA, Sum)"
    print(f"  measure {mv}: F({int(ag.loc[k,'df'])}, {int(ag.loc['Residual','df'])}) = {ag.loc[k,'F']:.3f}, p = {ag.loc[k,'PR(>F)']:.3g}")

# Check 3: repeated-measures ANOVA with participant (R aov, Error strata)
r = textwrap.dedent("""
d <- read.csv('papers/S05/data/d04.csv'); names(d) <- c('y','measure','target','SOA','subject')
for (v in c('measure','target','SOA','subject')) d[[v]] <- factor(d[[v]])
s <- summary(aov(y ~ measure*target*SOA + Error(subject/(measure*target*SOA)), data=d))
print(s[['Error: subject:measure:target:SOA']])
d$z <- ave(d$y, d$measure, FUN=function(x) (x-mean(x))/sd(x))
s2 <- summary(aov(z ~ measure*target*SOA + Error(subject/(measure*target*SOA)), data=d))
cat('z-scored:\\n'); print(s2[['Error: subject:measure:target:SOA']])
""")
print("\nCHECK repeated-measures ANOVA (R aov with Error strata), three-way stratum:")
print(subprocess.run(["/opt/homebrew/bin/Rscript", "-e", r], capture_output=True, text=True).stdout)
