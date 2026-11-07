"""Row.110 (node 7dyp5): 2 (stimulus category, within: friendly vs sexually interested; DV =
per-category sensitivity ln(alpha)) x 2 (participant gender, between) mixed ANOVA;
key statistic = gender x category interaction.
Written from the replication report and RPP_7dyp5.R before opening data:
  data = 2015.01.08 Farris ASA.sav, columns 22:23 = Sens_Friend, Sens_SI; no exclusions;
  N.R = 144; table F(1,142) = 1.19, p = .28, partial eta^2 = .008.
For a two-level within factor the interaction F equals the one-way between-groups F on the
difference score (Friend - SI); the gender main effect equals the one-way F on the mean (x2 scaling cancels).
"""
import os
import pandas as pd, numpy as np
from scipy import stats
import pyreadstat
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)
HERE = os.path.dirname(os.path.abspath(__file__))
df, meta = pyreadstat.read_sav(os.path.join(HERE, "download", "Data", "2015.01.08 Farris ASA.sav"))
print("shape:", df.shape, " columns 22:23 (1-based):", list(df.columns[21:23]))
print("unique ID:", df["ID"].nunique(), " NA in key columns:", int(df[["ID", "Gender", "Sens_Friend", "Sens_SI"]].isna().sum().sum()))
df["G"] = df["Gender"].map(meta.variable_value_labels["Gender"])
df["PT"] = df["Pres_time"].map(meta.variable_value_labels["Pres_time"])
print("gender counts:", df["G"].value_counts().to_dict(), " presentation time:", df["PT"].value_counts().to_dict())
print("means by gender:\n", df.groupby("G")[["Sens_Friend", "Sens_SI"]].agg(["mean", "std"]).round(4))

n = len(df); k = 2
diff = df["Sens_Friend"] - df["Sens_SI"]
groups = [diff[df["G"] == g] for g in ("Male", "Female")]
F, p = stats.f_oneway(*groups)
ss_b = sum(len(g) * (g.mean() - diff.mean()) ** 2 for g in groups)
ss_w = sum(((g - g.mean()) ** 2).sum() for g in groups)
print(f"\n[key] gender x category interaction: F(1,{n-k}) = {F:.4f}, p = {p:.6f}, partial eta^2 = {ss_b/(ss_b+ss_w):.4f}")
print(f"      mean (Friend - SI): Male {groups[0].mean():.4f}, Female {groups[1].mean():.4f}")

# cross-check with pingouin mixed_anova on long data
try:
    import pingouin as pg
    long = df.melt(id_vars=["ID", "G"], value_vars=["Sens_Friend", "Sens_SI"], var_name="cat", value_name="sens")
    print("\npingouin mixed_anova:\n", pg.mixed_anova(data=long, dv="sens", within="cat", subject="ID", between="G"))
except Exception as e:
    print("pingouin failed:", e)

# the second plausible test: gender main effect on positive-affect sensitivity (mean of the two)
m = (df["Sens_Friend"] + df["Sens_SI"]) / 2
F2, p2 = stats.f_oneway(m[df["G"] == "Male"], m[df["G"] == "Female"])
print(f"\n[other] gender main effect on mean positive-affect sensitivity: F(1,{n-k}) = {F2:.4f}, p = {p2:.6f}")

# full factorial model the report ran first: affect (pos/neg) x intent (present/absent) within,
# gender x presentation time between, type III; the three-way gender x affect x intent term
# is the type III gender effect on the double-difference contrast.
dd = (df["Sens_SI"] - df["Sens_Friend"]) - (df["Sens_Rej"] - df["Sens_Sad"])
df["dd"] = dd
a = anova_lm(smf.ols("dd ~ C(G, Sum) * C(PT, Sum)", data=df).fit(), typ=3)
print("\n[full model] type III on the affect x intent contrast; the C(G) row is gender x affect x intent:\n", a)
