"""Row.81 (node xse7q): independent reproduction of the replication's key test.

Key test (writeup "Primary finding", Table 4 last block; RPP_xse7q.R): 2 (role: victim=0 /
perpetrator=1) x 2 (message: acceptance=0 / empowerment=1) between-subjects ANOVA on
AvgWillingReconcileTime2 (willingness to reconcile after the message, mean of 10 items).
Key statistic: the role x message interaction. Cases with a missing DV or missing factor
code are dropped (listwise); no other exclusions.
Also shown, as the second plausible test the writeup reports: the Time x Role x Message
term of the mixed ANOVA (Time1 vs Time2 willingness), which is NOT the key test.
"""
import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from scipy import stats

F_SAV = "data/findings/Row.81/download/Data, codebook, and syntax/Shnabel & Nadler Rep Data - for OSF upload 2.23.2015.sav"
df, meta = pyreadstat.read_sav(F_SAV, apply_value_formats=False)
print("raw:", df.shape)
cols = ["VictimOrPerpV0P1", "AcceptOrEmpowerA0E1", "AvgWillingReconcileTime2"]
print("missing per column:", df[cols].isna().sum().to_dict())
d = df.dropna(subset=cols).copy()
d["role"] = d.VictimOrPerpV0P1.astype(int); d["msg"] = d.AcceptOrEmpowerA0E1.astype(int)
print("n after listwise deletion:", len(d))
print("cell n and means (role x msg):")
print(d.groupby(["role", "msg"]).AvgWillingReconcileTime2.agg(["count", "mean", "std"]).round(3))

for typ in (1, 3):
    m = smf.ols("AvgWillingReconcileTime2 ~ C(role, Sum) * C(msg, Sum)", data=d).fit()
    a = anova_lm(m, typ=typ)
    row = a.loc["C(role, Sum):C(msg, Sum)"]
    F, p = row["F"], row["PR(>F)"]; ss = row["sum_sq"]; sse = a.loc["Residual", "sum_sq"]
    print(f"\n[type {typ}] role x message: F(1,{int(m.df_resid)}) = {F:.3f}, p = {p:.4f}, partial eta^2 = {ss/(ss+sse):.4f}")

# Second plausible test (not the key test): Time x Role x Message in the mixed ANOVA.
d2 = df.dropna(subset=cols + ["AvgWillingReconcileTime1"]).copy()
d2["diff"] = d2.AvgWillingReconcileTime2 - d2.AvgWillingReconcileTime1
d2["role"] = d2.VictimOrPerpV0P1.astype(int); d2["msg"] = d2.AcceptOrEmpowerA0E1.astype(int)
m2 = smf.ols("diff ~ C(role, Sum) * C(msg, Sum)", data=d2).fit()
a2 = anova_lm(m2, typ=3).loc["C(role, Sum):C(msg, Sum)"]
print(f"\n[not key] mixed ANOVA Time x Role x Message (via change score): F(1,{int(m2.df_resid)}) = {a2['F']:.4f}, p = {a2['PR(>F)']:.3f}, n = {len(d2)}")
