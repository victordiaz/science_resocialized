"""S30: Gender x category (friendly vs sexually interested) interaction on ln(alpha)."""
import numpy as np, pandas as pd, pyreadstat, pingouin as pg
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

df, meta = pyreadstat.read_sav("papers/S30/data/d02.sav")
print("rows:", len(df))
df["sex"] = df.Gender.map({1.0: "Male", 2.0: "Female"})
df["pt"] = df.Pres_time.map({1.0: "500ms", 2.0: "3000ms"})
keep = df.dropna(subset=["sex", "Sens_Friend", "Sens_SI"]).copy()
print("excluded for missing key data:", len(df) - len(keep))
print(keep.sex.value_counts().to_dict(), keep.pt.value_counts().to_dict())
keep["diff"] = keep.Sens_Friend - keep.Sens_SI

print("\nDescriptives (mean, sd, n):")
print(keep.groupby("sex")[["Sens_Friend", "Sens_SI", "diff"]].agg(["mean", "std", "count"]).round(4).T)

# PRIMARY: mixed ANOVA
long = keep.melt(id_vars=["ID", "sex"], value_vars=["Sens_Friend", "Sens_SI"], var_name="cat", value_name="lnalpha")
aov = pg.mixed_anova(data=long, dv="lnalpha", within="cat", between="sex", subject="ID", effsize="np2")
print("\nPRIMARY mixed ANOVA:\n", aov.round(5).to_string())

# equivalent one-way ANOVA on diff
m, f = keep.loc[keep.sex == "Male", "diff"], keep.loc[keep.sex == "Female", "diff"]
F, p = stats.f_oneway(m, f)
n = len(keep); dfe = n - 2
np2 = F / (F + dfe)
print(f"\nOne-way ANOVA on diff: F(1,{dfe}) = {F:.4f}, p = {p:.5f}, partial eta2 = {np2:.4f}")

# 95% CI for partial eta2 via noncentral F inversion
from scipy.optimize import brentq
def ncp_ci(F, d1, d2, conf=.95):
    a = (1 - conf) / 2
    def f(l, target): return stats.ncf.cdf(F, d1, d2, l) - target if l > 0 else stats.f.cdf(F, d1, d2) - target
    lo = 0.0 if stats.f.cdf(F, d1, d2) < 1 - a else brentq(lambda l: f(l, 1 - a), 1e-9, 1000)
    hi = 0.0 if stats.f.cdf(F, d1, d2) < a else brentq(lambda l: f(l, a), 1e-9, 1000)
    N = d1 + d2 + 1
    return lo / (lo + N), hi / (hi + N)
lo, hi = ncp_ci(F, 1, dfe)
print(f"partial eta2 95% CI: [{lo:.4f}, {hi:.4f}]")

md = m.mean() - f.mean()
se = np.sqrt(m.var(ddof=1)/len(m) + f.var(ddof=1)/len(f))
tt = stats.ttest_ind(m, f, equal_var=False)
print(f"Mean diff (Male - Female) in Friend-SI gap: {md:.4f}, Welch t = {tt.statistic:.3f}, p = {tt.pvalue:.5f}")
d = pg.compute_effsize(m, f, eftype="cohen")
print(f"Cohen's d on diff: {d:.3f}, 95% CI {pg.compute_esci(d, len(m), len(f))}")
rng = np.random.default_rng(30)
bs = [rng.choice(m.values, len(m)).mean() - rng.choice(f.values, len(f)).mean() for _ in range(10000)]
print("bootstrap 95% CI for mean diff:", np.round(np.percentile(bs, [2.5, 97.5]), 4))
print("Mann-Whitney on diff:", stats.mannwhitneyu(m, f))

print("\nSecondary: gender effect per category (Welch t):")
for c in ["Sens_Friend", "Sens_SI", "Sens_Sad", "Sens_Rej"]:
    a, b = keep.loc[keep.sex == "Male", c], keep.loc[keep.sex == "Female", c]
    r = stats.ttest_ind(a, b, equal_var=False)
    print(f"  {c}: M={a.mean():.4f} F={b.mean():.4f} M-F={a.mean()-b.mean():.4f} t={r.statistic:.3f} p={r.pvalue:.5f} d={pg.compute_effsize(a,b,eftype='cohen'):.3f}")

print("\nRobustness: diff ~ sex * pt (type III):")
mod = smf.ols("diff ~ C(sex, Sum) * C(pt, Sum)", data=keep).fit()
print(sm.stats.anova_lm(mod, typ=3).round(5))

fig, ax = plt.subplots(figsize=(4.5, 3.2))
for sx, mk in [("Male", "o"), ("Female", "s")]:
    g = keep[keep.sex == sx]
    mu = [g.Sens_Friend.mean(), g.Sens_SI.mean()]
    ci = [1.96 * g.Sens_Friend.std() / np.sqrt(len(g)), 1.96 * g.Sens_SI.std() / np.sqrt(len(g))]
    ax.errorbar([0, 1], mu, yerr=ci, marker=mk, capsize=4, label=f"{sx} (n={len(g)})")
ax.set_xticks([0, 1]); ax.set_xticklabels(["Friendly", "Sexually interested"])
ax.set_ylabel("ln(α) discrimination (mean ± 95% CI)"); ax.legend(); fig.tight_layout()
fig.savefig("papers/S30/report/fig1.png", dpi=150)
print("figure saved")

# power of the interaction test for given partial eta2 (noncentral F, lambda = f2 * N)
for e in [0.02, 0.05, 0.06]:
    lam = e / (1 - e) * n
    crit = stats.f.ppf(0.95, 1, dfe)
    print(f"power at partial eta2={e}: {1 - stats.ncf.cdf(crit, 1, dfe, lam):.3f}")
