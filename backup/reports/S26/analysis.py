"""S26: 2x2 between-groups ANOVA on group-mean pool-B contribution. Run from the S26 run dir:
.venv/bin/python -I papers/S26/report/analysis.py"""
import hashlib, json, numpy as np, pandas as pd, pyreadstat
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
D = "papers/S26/data/"
man = json.load(open(D + "MANIFEST.json"))
for f in ["d04.sav", "d05.sav"]:
    h = hashlib.sha256(open(D + f, "rb").read()).hexdigest()
    print(f, "sha256 ok" if h == man["files"][f]["sha256"] else "SHA MISMATCH")

ind, _ = pyreadstat.read_sav(D + "d05.sav")
print("individual rows:", len(ind))
print("missing GivePool_B:", ind.GivePool_B.isna().sum(), "| missing conditions:",
      ind[["Condition_Game", "Condition_Communication"]].isna().any(axis=1).sum())
print("GivePool_B range:", ind.GivePool_B.min(), ind.GivePool_B.max())
chk = ind.groupby("Group_Num").agg(n=("GivePool_B", "size"),
        ng=("Condition_Game", "nunique"), nc=("Condition_Communication", "nunique"))
print("groups:", len(chk), "| sizes:", chk.n.value_counts().to_dict(),
      "| condition-consistent:", bool((chk.ng == 1).all() and (chk.nc == 1).all()))

g = ind.groupby("Group_Num").agg(B=("GivePool_B", "mean"), W=("GivePool_W", "mean"),
        game=("Condition_Game", "first"), comm=("Condition_Communication", "first")).reset_index()
g["game"] = g.game.map({1: "one-pool", 2: "two-pool"})
g["comm"] = g.comm.map({1: "none", 2: "comm"})
print("\nCell counts:\n", pd.crosstab(g.game, g.comm))
print("\nCell means (SD) of group-mean GivePool_B (tokens of 10):")
print(g.groupby(["game", "comm"]).B.agg(["mean", "std", "count"]).round(3))
print("\nGame marginal means:", g.groupby("game").B.agg(["mean", "std", "count"]).round(3).to_dict())

# cross-check with d04 aggregate
agg, _ = pyreadstat.read_sav(D + "d04.sav")
m = g.merge(agg[["Group_Num", "Pool_B_Percent"]], on="Group_Num")
print("\nmax |group mean*10 - d04 Pool_B_Percent|:", round(float((m.B * 10 - m.Pool_B_Percent).abs().max()), 3))

# PRIMARY: 2x2 ANOVA, Type III with sum contrasts
mod = smf.ols("B ~ C(game, Sum) * C(comm, Sum)", data=g).fit()
a = anova_lm(mod, typ=3)
print("\nPRIMARY ANOVA (Type III):\n", a.round(4))
ss_g = a.loc["C(game, Sum)", "sum_sq"]; ss_e = a.loc["Residual", "sum_sq"]
F = a.loc["C(game, Sum)", "F"]; p = a.loc["C(game, Sum)", "PR(>F)"]; df2 = int(a.loc["Residual", "df"])
pe2 = ss_g / (ss_g + ss_e)

def ncp_ci(F, d1, d2, level=0.95):
    from scipy.optimize import brentq
    lo_t, hi_t = 1 - (1 - level) / 2, (1 - level) / 2
    f = lambda nc, t: stats.ncf.cdf(F, d1, d2, nc) - t if nc > 0 else stats.f.cdf(F, d1, d2) - t
    lo = 0.0 if stats.f.cdf(F, d1, d2) < lo_t else brentq(lambda x: f(x, lo_t), 1e-9, 1000)
    hi = 0.0 if stats.f.cdf(F, d1, d2) < hi_t else brentq(lambda x: f(x, hi_t), 1e-9, 1000)
    N = d1 + d2 + 1  # total groups (here d1=1 for one effect; N = df_error + 4 cells)
    return lo, hi
lo, hi = ncp_ci(F, 1, df2)
Ntot = len(g)
ci = (lo / (lo + Ntot), hi / (hi + Ntot))
diff = g[g.game == "two-pool"].B.mean() - g[g.game == "one-pool"].B.mean()
mse = ss_e / df2
se = np.sqrt(mse * (1 / 20 + 1 / 20)); tcrit = stats.t.ppf(.975, df2)
print(f"\nKEY: game main effect F(1, {df2}) = {F:.3f}, p = {p:.4g}, partial eta^2 = {pe2:.3f} "
      f"[95% CI {ci[0]:.3f}, {ci[1]:.3f}]")
print(f"Two-pool minus one-pool difference in group-mean tokens to B = {diff:.3f} "
      f"[95% CI {diff - tcrit*se:.3f}, {diff + tcrit*se:.3f}] (ANOVA MSE); in % of endowment: {diff*10:.1f} points")
print("Direction two-pool < one-pool:", diff < 0)

# Robustness
a1 = anova_lm(smf.ols("B ~ C(game) * C(comm)", data=g).fit(), typ=1)
print("\nType I ANOVA (check):\n", a1.round(4))
x1 = g[g.game == "one-pool"].B; x2 = g[g.game == "two-pool"].B
print("\nWelch t (game, ignoring comm):", stats.ttest_ind(x2, x1, equal_var=False))
print("Mann-Whitney (game):", stats.mannwhitneyu(x2, x1, alternative="two-sided"))
m["pct"] = m.Pool_B_Percent
print("\nANOVA on d04 Pool_B_Percent:\n", anova_lm(smf.ols("pct ~ C(game, Sum)*C(comm, Sum)",
      data=m.merge(g[["Group_Num"]], on="Group_Num")).fit(), typ=3).round(4))
print("\nLevene (4 cells):", stats.levene(*[d.B for _, d in g.groupby(["game", "comm"])]))
print("Shapiro on residuals:", stats.shapiro(mod.resid))
# Individual level, cluster-robust by group
ind["game"] = ind.Condition_Game.map({1: "one-pool", 2: "two-pool"}); ind["comm"] = ind.Condition_Communication
ri = smf.ols("GivePool_B ~ C(game, Sum)*C(comm, Sum)", data=ind).fit(cov_type="cluster", cov_kwds={"groups": ind.Group_Num})
print("\nIndividual-level OLS, group-clustered SE (game term):",
      ri.params.filter(like="game").round(3).to_dict(), ri.pvalues.filter(like="game").round(4).to_dict())
# Not the key test: pool W, two-pool game only, comm vs none
w = g[g.game == "two-pool"]
print("\n(Secondary) Pool W by communication, two-pool only:", w.groupby("comm").W.mean().round(3).to_dict(),
      stats.ttest_ind(w[w.comm == "comm"].W, w[w.comm == "none"].W))

# Figure
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5, 3.2))
for i, (gm, col) in enumerate([("one-pool", "#555"), ("two-pool", "#c44")]):
    for j, cm in enumerate(["none", "comm"]):
        y = g[(g.game == gm) & (g.comm == cm)].B.values * 10
        xpos = j + (i - .5) * .3
        ax.scatter(np.full(len(y), xpos) + np.random.default_rng(1).uniform(-.05, .05, len(y)), y, s=12, color=col, alpha=.6)
        ax.errorbar(xpos + .08, y.mean(), yerr=stats.sem(y) * stats.t.ppf(.975, len(y) - 1), fmt="o", color=col,
                    capsize=3, label=gm if j == 0 else None)
ax.set_xticks([0, 1]); ax.set_xticklabels(["No communication", "Communication"])
ax.set_ylabel("% of endowment to pool B (group)"); ax.set_ylim(-5, 105); ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig("papers/S26/report/fig1.png", dpi=150)
print("\nfigure written")
