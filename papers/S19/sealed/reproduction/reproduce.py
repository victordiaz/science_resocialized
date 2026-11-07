"""Row.10 (node vmipw): independent reproduction of the replication's key test.

Key test (replication report, Analysis Plan + Results): 3 (Notation: Arabic, Indian,
Mixed; within) x 2 (numerical difference: small, large; within) x 2 (task order; between)
mixed ANOVA on per-participant mean RT of CORRECT "different" responses in the numerical
same-different task. Effect of interest: main effect of numerical difference (Distance).

Exclusions (Codes.docx filter + report): RT < 200 or RT > 2500 dropped; participant 24
dropped; distracting trials (Distraction == 1, digits 3-7) dropped; "same" pairs
(Distance == 0) dropped; and, per the report ("means of reaction time (RT) of correct
responses"), error trials (correct == 0) dropped.

A 2-level within factor in a mixed design: its F equals the squared t for the intercept of
an OLS regression of each participant's contrast score D_i = sum over notations of
(small - large) on effect-coded Order (type 3, unweighted). The error MS of the
Participant x Distance stratum is SS_resid(D) / (sum of squared contrast weights = 6) / df.
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

BASE = "data/findings/Row.10/download"
raw = pd.read_csv(f"{BASE}/Data/Numerical_task.csv")
order = pd.read_csv(f"{BASE}/Data/Order.csv")
print("raw trials:", raw.shape, "participants:", raw.participant.nunique())
print("Order.csv:", order.shape, "participants:", sorted(order.participant)[:3], "...")

def distance_test(df, label):
    cell = df.groupby(["participant", "Notation", "Distance"]).RT.mean().unstack(["Notation", "Distance"])
    cell = cell.dropna()
    D = sum(cell[(n, 1)] - cell[(n, 2)] for n in (1, 2, 3))
    d = pd.DataFrame({"D": D}).join(order.set_index("participant"))
    d["o"] = np.where(d.Order == 1, 1.0, -1.0)  # effect coding -> type 3 intercept
    m = smf.ols("D ~ o", data=d).fit()
    t = m.tvalues["Intercept"]; F = t ** 2; df2 = int(m.df_resid)
    p = stats.f.sf(F, 1, df2)
    mse = m.ssr / 6 / df2
    SS_eff = F * mse
    peta = SS_eff / (SS_eff + m.ssr / 6)
    small = np.mean([cell[(n, 1)].mean() for n in (1, 2, 3)])
    large = np.mean([cell[(n, 2)].mean() for n in (1, 2, 3)])
    print(f"\n[{label}] n participants = {len(d)} (Order 1: {(d.Order==1).sum()}, Order 2: {(d.Order==2).sum()}); trials used = {len(df)}")
    print(f"  mean RT small = {small:.2f} ms, large = {large:.2f} ms")
    print(f"  Distance main effect: F(1,{df2}) = {F:.3f}, p = {p:.3g}, MSE = {mse:.3f}, partial eta^2 = {peta:.3f}")
    return F, df2, p, mse, peta, len(d)

base = raw.merge(order, on="participant")  # inner merge drops participant 24 (absent from Order.csv)
common = base[(base.RT >= 200) & (base.RT <= 2500) & (base.participant != 24)
              & (base.Distraction != 1) & (base.Distance != 0)]
print("rows after filter (no correctness rule):", len(common),
      "| equals filter_$==1 count:", int((raw["filter_$"] == 1).sum()))

key = distance_test(common[common.correct == 1], "KEY: correct trials only (report)")
alt = distance_test(common, "AUDIT-SCRIPT PATH: all trials, correct and error")

# cross-check against the replication's own aggregated file
try:
    import pyreadstat
    sav, _ = pyreadstat.read_sav(f"{BASE}/x/raw/Raw Data/SDV_RTs.sav")
    print("\nSDV_RTs.sav (replication's aggregate):", sav.shape, list(sav.columns))
except Exception as e:
    print("SDV_RTs.sav not read:", e)

# The audit's own saved output (ANOVA table.png) shows F(1,29)=42.58, MSE=3520.779.
# Its MSE equals the all-trials path above; its F equals the type-2 (n-weighted grand mean)
# test of Distance, not type 3. Shown here so the gap is explained on the page.
def distance_type2(df, label):
    cell = df.groupby(["participant", "Notation", "Distance"]).RT.mean().unstack(["Notation", "Distance"]).dropna()
    D = sum(cell[(n, 1)] - cell[(n, 2)] for n in (1, 2, 3))
    g = order.set_index("participant").Order.loc[D.index]
    sse = ((D - D.groupby(g).transform("mean")) ** 2).sum()
    F = len(D) * D.mean() ** 2 / (sse / (len(D) - 2))
    print(f"[type 2, {label}] F(1,{len(D)-2}) = {F:.3f}, p = {stats.f.sf(F,1,len(D)-2):.3g}, MSE = {sse/6/(len(D)-2):.3f}")

print()
distance_type2(common[common.correct == 1], "correct trials only")
distance_type2(common, "all trials")
