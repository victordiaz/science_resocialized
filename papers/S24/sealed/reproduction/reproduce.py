"""Row.19 (node gcj7x): reproduce the replication's key statistic from raw data.

Key test as the audit script RPP_gcj7x.R defines it, written before running:
  data: 'Proportion correct wide 2.sav' (OSF n87dw), one row per subject,
        columns subject, listtype (between: long-short / short-long),
        correct, intrusion, new (proportion correct per probe type).
  model: mixed ANOVA, type-3 SS, DV = proportion correct,
         between = listtype, within = probe type (3 levels), wid = subject.
  term: row 2 of ezANOVA's detailed table = the listtype main effect.
  exclusions: none in the script (all 21 rows).
  expected (table): F(1,19)=3.661, p=0.071, partial eta^2 = .162.
Written independently: the between-subjects main effect in a mixed design
equals a one-way ANOVA on each subject's mean over the within levels (scaled),
and pingouin.mixed_anova is used as a second route.
"""
import sys
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
import pingouin as pg

path = "download/r2zcn__Proportion correct wide 2.sav"
df, meta = pyreadstat.read_sav(path)
print("raw shape:", df.shape, "columns:", list(df.columns))
print(df.groupby("listtype").size().to_string())

# Route 1: one-way ANOVA on subject means across the three probe types
df["m"] = df[["correct", "intrusion", "new"]].mean(axis=1)
g = [x["m"].values for _, x in df.groupby("listtype")]
F, p = stats.f_oneway(*g)
k = 3
grand = df["m"].mean()
ss_b = sum(len(x) * (x.mean() - grand) ** 2 for x in g) * k
ss_w = sum(((x - x.mean()) ** 2).sum() for x in g) * k
print(f"\nRoute 1 (subject means): F(1,{len(df)-2}) = {F:.4f}, p = {p:.5f}, pes = {ss_b/(ss_b+ss_w):.4f}")

# Route 2: full mixed ANOVA in long format
long = df.melt(id_vars=["subject", "listtype"], value_vars=["correct", "intrusion", "new"],
               var_name="probetype", value_name="pc")
aov = pg.mixed_anova(data=long, dv="pc", between="listtype", within="probetype",
                     subject="subject", effsize="np2", correction=False)
pd.set_option("display.width", 200)
print("\nRoute 2 (pingouin mixed_anova):\n", aov.round(5).to_string())

# Alternative plausible test (the effect text names NEW probes only):
gn = [x["new"].values for _, x in df.groupby("listtype")]
Fn, pn = stats.f_oneway(*gn)
print(f"\nAlternative, new probes only, listtype: F(1,{len(df)-2}) = {Fn:.4f}, p = {pn:.5f}")
print("cell means (new):", df.groupby("listtype")["new"].mean().round(4).to_dict())
print("cell means (all probes):", df.groupby("listtype")["m"].mean().round(4).to_dict())
