"""S28 analysis. Run from the S28 run directory: .venv/bin/python -I papers/S28/report/analysis.py"""
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from scipy import stats, optimize
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import os
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 10)
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, "..", "data", "d09.csv"))
print("rows:", len(d))
chk = (d.Q5 + d.Q8) / 2
print("aggressivenessScore == (Q5+Q8)/2 mismatches:", int((~np.isclose(chk, d.aggressivenessScore)).sum()))
print("discard==1:", int((d.discard == 1).sum()), "| missing DV:", int(d.aggressivenessScore.isna().sum()))
a = d[(d.discard != 1) & d.aggressivenessScore.notna()].copy()
print("N analysed:", len(a))

def anova(df, label):
    m = smf.ols("aggressivenessScore ~ C(mapCondition, Sum) * C(puzzleCondition, Sum)", data=df).fit()
    t3 = anova_lm(m, typ=3); t2 = anova_lm(smf.ols("aggressivenessScore ~ C(mapCondition) * C(puzzleCondition)", data=df).fit(), typ=2)
    print(f"\n== {label} (N={len(df)}) type III ==\n", t3.round(4)); print("type II\n", t2.round(4))
    return t3
t3 = anova(a, "PRIMARY")
row = [i for i in t3.index if ":" in i][0]
SSi, df1, F, p = t3.loc[row, "sum_sq"], int(t3.loc[row, "df"]), t3.loc[row, "F"], t3.loc[row, "PR(>F)"]
SSr, df2 = t3.loc["Residual", "sum_sq"], int(t3.loc["Residual", "df"])
pe = SSi / (SSi + SSr)
# CI for partial eta^2 by inverting noncentral F
def lam_for(q):
    f = lambda L: stats.ncf.cdf(F, df1, df2, L) - q
    return 0.0 if f(0) < 0 else optimize.brentq(f, 0, 500)
lo, hi = lam_for(0.975), lam_for(0.025)
N = len(a)
ci = (lo / (lo + N), hi / (hi + N))
print(f"\nPRIMARY interaction: F({df1}, {df2}) = {F:.3f}, p = {p:.4f}, partial eta^2 = {pe:.4f}, 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]")

print("\nCell means")
cm = a.groupby(["mapCondition", "puzzleCondition"]).aggressivenessScore.agg(["count", "mean", "std"])
print(cm.round(3))
print("\nSimple effects of puzzle (Aggression - Neutral) within map condition (Welch t)")
for mc in ["Global", "Control", "Local"]:
    s = a[a.mapCondition == mc]; x = s[s.puzzleCondition == "Aggression"].aggressivenessScore; y = s[s.puzzleCondition == "Neutral"].aggressivenessScore
    t = stats.ttest_ind(x, y, equal_var=False)
    sp = np.sqrt(((len(x)-1)*x.var() + (len(y)-1)*y.var())/(len(x)+len(y)-2))
    print(f"{mc}: diff = {x.mean()-y.mean():.3f}, t = {t.statistic:.3f}, df = {t.df:.1f}, p = {t.pvalue:.4f}, d = {(x.mean()-y.mean())/sp:.3f}")
# planned contrast: Local vs (Global+Control) on prime effect, from the full model
m = smf.ols("aggressivenessScore ~ C(mapCondition):C(puzzleCondition) - 1", data=a).fit()
print("\ncell-model params:", list(m.params.index))
w = {}
for mc, c in [("Global", .5), ("Control", .5), ("Local", -1)]:
    for pc, s in [("Aggression", 1), ("Neutral", -1)]:
        w[f"C(mapCondition)[{mc}]:C(puzzleCondition)[{pc}]"] = c * s
L = np.array([w[k] for k in m.params.index])
print("Contrast Local vs Global+Control on prime effect:", m.t_test(L))

print("\n== Robustness: rank-transformed DV ==")
a["rk"] = a.aggressivenessScore.rank()
print(anova_lm(smf.ols("rk ~ C(mapCondition, Sum) * C(puzzleCondition, Sum)", data=a).fit(), typ=3).round(4))
anova(d[d.aggressivenessScore.notna()], "Robustness: discard==1 kept")

fig, ax = plt.subplots(figsize=(5, 3.4))
order = ["Global", "Control", "Local"]
for pc, mk in [("Aggression", "o-"), ("Neutral", "s--")]:
    mu = [cm.loc[(mc, pc), "mean"] for mc in order]; se = [cm.loc[(mc, pc), "std"]/np.sqrt(cm.loc[(mc, pc), "count"]) for mc in order]
    ax.errorbar(order, mu, yerr=se, fmt=mk, capsize=3, label=f"{pc} puzzle")
ax.set_ylabel("Aggressiveness score (1-9)"); ax.set_xlabel("Map condition"); ax.legend(); ax.set_title("Cell means ± 1 SE")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig1.png"), dpi=150)
print("figure saved")
