"""S18: achievement-word priming and implicit sequence learning. Run: .venv/bin/python -I papers/S18/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df, meta = pyreadstat.read_sav("papers/S18/data/d07.sav")
print("rows in file:", len(df))
print(pd.crosstab(df["Include1"], df["Condition"], margins=True))

df["learn"] = (df["R1Mean"] + df["R2Mean"]) / 2 - df["FSMean"]   # card definition: random minus fixed
assert np.allclose(df["learn"].dropna(), -df.loc[df["learn"].notna(), "Learning"])

d = df[df["Include1"] == 0].copy()
a = d.loc[d["Condition"] == 1, "learn"].dropna().values   # achievement words
c = d.loc[d["Condition"] == 2, "learn"].dropna().values   # control
print(f"\nAfter exclusions: n_ach={len(a)}, n_ctl={len(c)}, total={len(a)+len(c)}")
print("Excluded (Include1==1) reasons:")
print(df.loc[df["Include1"] == 1, ["Condition", "Excludetechknowledge", "Exclude1", "Include1Reason"]].assign(
    Include1Reason=lambda x: x.Include1Reason.replace("", "(none given)")).value_counts().to_string())

for nm, x in [("achievement", a), ("control", c)]:
    print(f"{nm}: mean={x.mean():.2f} sd={x.std(ddof=1):.2f} median={np.median(x):.2f} n={len(x)}")

# PRIMARY: Student t-test, equal variances, two-sided, achievement minus control
t, p = stats.ttest_ind(a, c, equal_var=True)
n1, n2 = len(a), len(c); df_t = n1 + n2 - 2
sp = np.sqrt(((n1-1)*a.var(ddof=1) + (n2-1)*c.var(ddof=1)) / df_t)
diff = a.mean() - c.mean()
dcoh = diff / sp
se_d = np.sqrt((n1+n2)/(n1*n2) + dcoh**2/(2*(n1+n2)))
z = stats.norm.ppf(.975)
se_diff = sp*np.sqrt(1/n1+1/n2); tc = stats.t.ppf(.975, df_t)
print(f"\nPRIMARY Student t({df_t}) = {t:.3f}, p = {p:.4f}")
print(f"mean difference (ach - ctl) = {diff:.2f} ms, 95% CI [{diff-tc*se_diff:.2f}, {diff+tc*se_diff:.2f}]")
print(f"Cohen's d (pooled SD = {sp:.2f}) = {dcoh:.3f}, 95% CI [{dcoh-z*se_d:.3f}, {dcoh+z*se_d:.3f}]")

# Robustness (not the basis of the conclusion)
tw, pw = stats.ttest_ind(a, c, equal_var=False)
print(f"\nWelch t = {tw:.3f}, p = {pw:.4f}")
u, pu = stats.mannwhitneyu(a, c, alternative="two-sided")
print(f"Mann-Whitney U = {u:.1f}, p = {pu:.4f}")
print(f"Levene p = {stats.levene(a, c).pvalue:.4f}")
allx = np.concatenate([a, c]); t1, p1 = stats.ttest_1samp(allx, 0)
print(f"Manipulation check, learning > 0 overall: mean={allx.mean():.2f}, t({len(allx)-1})={t1:.2f}, p={p1:.2g}")
# median-based learning score
d["medlearn"] = -d["MedLearn"]
tm, pm = stats.ttest_ind(d.loc[d.Condition == 1, "medlearn"].dropna(), d.loc[d.Condition == 2, "medlearn"].dropna())
print(f"Median-RT learning score: t = {tm:.3f}, p = {pm:.4f}")
# all participants with valid RT data, ignoring the first-79 cut and awareness exclusions
allv = df[df["learn"].notna()]
ta, pa = stats.ttest_ind(allv.loc[allv.Condition == 1, "learn"], allv.loc[allv.Condition == 2, "learn"])
print(f"All with RT data (n={len(allv)}): t = {ta:.3f}, p = {pa:.4f}")

fig, ax = plt.subplots(figsize=(4.5, 3.2))
ax.boxplot([a, c], tick_labels=["Achievement words", "Control"], widths=.5)
rng = np.random.default_rng(1)
for i, x in enumerate([a, c], 1):
    ax.scatter(i + rng.uniform(-.12, .12, len(x)), x, s=8, alpha=.5)
    ax.plot([i-.25, i+.25], [x.mean()]*2, color="k", lw=2)
ax.axhline(0, color="grey", lw=.6, ls=":")
ax.set_ylabel("Learning score (ms)\nrandom minus fixed-sequence RT")
fig.tight_layout(); fig.savefig("papers/S18/report/fig1.png", dpi=150)
print("figure written: papers/S18/report/fig1.png")
