"""S01: hand-washing after a disgust clip and moral wrongness ratings (d12.sav).
Run from the S01 run directory:  .venv/bin/python -I papers/S01/report/analysis.py
"""
import os
import numpy as np, pandas as pd, pyreadstat
from scipy import stats, optimize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "d12.sav")
ITEMS = ["Dog", "Trolley", "Wallet", "Plane", "Resume", "Kitten"]

df, meta = pyreadstat.read_sav(DATA)
print("Rows in file:", len(df))
print("Condition counts (all):", df["Condition"].value_counts().sort_index().to_dict())

# check stored DV against recomputed mean
recomp = df[ITEMS].mean(axis=1)
print("Max |stored mean_vignettes - recomputed|:", float((df["mean_vignettes"] - recomp).abs().max()))

# exclusions (pre-registered)
made = df["Madeup_dummy"] == 1
err = df["Exp_Error"] == 1
print("Madeup_dummy==1:", int(made.sum()), " Exp_Error==1:", int(err.sum()),
      " both:", int((made & err).sum()), " either:", int((made | err).sum()))
d = df[~(made | err)].dropna(subset=["mean_vignettes", "Condition"]).copy()
print("N after exclusions:", len(d))
print("Excluded by condition:", df[made | err]["Condition"].value_counts().sort_index().to_dict())


def cohen_d_ci(x1, x0, level=0.95):
    n1, n0 = len(x1), len(x0)
    sp = np.sqrt(((n1 - 1) * x1.var(ddof=1) + (n0 - 1) * x0.var(ddof=1)) / (n1 + n0 - 2))
    dd = (x1.mean() - x0.mean()) / sp
    df_ = n1 + n0 - 2
    k = np.sqrt(1 / n1 + 1 / n0)
    t_obs = dd / k
    a = (1 - level) / 2
    lo_nc = optimize.brentq(lambda nc: stats.nct.sf(t_obs, df_, nc) - a, t_obs - 10, t_obs + 10)
    hi_nc = optimize.brentq(lambda nc: stats.nct.cdf(t_obs, df_, nc) - a, t_obs - 10, t_obs + 10)
    se = np.sqrt((n1 + n0) / (n1 * n0) + dd ** 2 / (2 * (n1 + n0)))
    return dd, (lo_nc * k, hi_nc * k), (dd - 1.96 * se, dd + 1.96 * se)


def describe(sub, label):
    g0 = sub.loc[sub.Condition == 0, "mean_vignettes"]
    g1 = sub.loc[sub.Condition == 1, "mean_vignettes"]
    t, p = stats.ttest_ind(g1, g0, equal_var=True)
    F, pF = stats.f_oneway(g1, g0)
    dd, ci, ci_n = cohen_d_ci(g1.values, g0.values)
    print(f"\n== {label} ==")
    print(f"No wash (0): n={len(g0)} M={g0.mean():.3f} SD={g0.std(ddof=1):.3f}")
    print(f"Wash    (1): n={len(g1)} M={g1.mean():.3f} SD={g1.std(ddof=1):.3f}")
    print(f"Mean diff (wash - no wash) = {g1.mean() - g0.mean():.3f}")
    print(f"ANOVA F(1, {len(sub) - 2}) = {F:.3f}, p = {pF:.4f};  t({len(sub) - 2}) = {t:.3f}, p = {p:.4f}")
    print(f"Cohen's d (pooled, wash - no wash) = {dd:.3f}, 95% CI noncentral-t [{ci[0]:.3f}, {ci[1]:.3f}], normal-approx [{ci_n[0]:.3f}, {ci_n[1]:.3f}]")
    return g0, g1


# PRIMARY
print("\n######## PRIMARY TEST ########")
g0, g1 = describe(d, "Primary: pre-registered exclusions, ANOVA of mean_vignettes by Condition")
lev = stats.levene(g1, g0, center="mean")
print(f"Levene F = {lev.statistic:.3f}, p = {lev.pvalue:.4f}")
print("Shapiro p (no wash, wash):", round(stats.shapiro(g0).pvalue, 4), round(stats.shapiro(g1).pvalue, 4))

# ROBUSTNESS
print("\n######## ROBUSTNESS (not the conclusion) ########")
w = stats.ttest_ind(g1, g0, equal_var=False)
print(f"Welch t = {w.statistic:.3f}, p = {w.pvalue:.4f}")
u = stats.mannwhitneyu(g1, g0, alternative="two-sided")
print(f"Mann-Whitney U = {u.statistic:.1f}, p = {u.pvalue:.4f}")
print(f"One-sided Student t p (wash < no wash) = {stats.ttest_ind(g1, g0, alternative='less').pvalue:.4f}")
describe(df.dropna(subset=["mean_vignettes", "Condition"]), "No exclusions (N=132)")
describe(d[d.Final_Rating == 0], "Pre-registered exclusions + Final_Rating == 0 (no suspicion)")
print("\nPer-item (pre-registered exclusions), wash - no wash:")
for it in ITEMS:
    a, b = d.loc[d.Condition == 1, it], d.loc[d.Condition == 0, it]
    t, p = stats.ttest_ind(a, b)
    print(f"  {it:8s} M0={b.mean():.2f} M1={a.mean():.2f} diff={a.mean() - b.mean():+.2f} t({len(a) + len(b) - 2})={t:+.2f} p={p:.3f}")
print("\nDisgusted rating by condition (manipulation context):",
      d.groupby("Condition")["Disgusted"].agg(["mean", "std", "count"]).round(2).to_dict())

# figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=150)
rng = np.random.default_rng(1)
for i, (g, lab) in enumerate([(g0, "No hand-washing"), (g1, "Hand-washing")]):
    ax.scatter(i + rng.uniform(-0.12, 0.12, len(g)), g, s=9, alpha=0.45, color="grey")
    se = g.std(ddof=1) / np.sqrt(len(g))
    ax.errorbar(i + 0.25, g.mean(), yerr=1.96 * se, fmt="o", color="black", capsize=4)
ax.set_xticks([0, 1]); ax.set_xticklabels([f"No hand-washing\n(n={len(g0)})", f"Hand-washing\n(n={len(g1)})"])
ax.set_ylabel("Mean wrongness (1-7), six vignettes"); ax.set_xlim(-0.5, 1.6)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig1.png"))
print("\nFigure written: fig1.png")
