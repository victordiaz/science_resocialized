"""S20 analysis: AC vs MU x sum vs neutral interaction on correct-RT cell means.
Run from the run directory: .venv/bin/python -I papers/S20/report/analysis.py"""
import hashlib, numpy as np, pandas as pd, pyreadstat
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = "papers/S20/data/"
h = {f: hashlib.sha256(open(D + f, "rb").read()).hexdigest() for f in ["d02.sav", "d04.sav"]}
print("sha256:", h, "identical:", h["d02.sav"] == h["d04.sav"])
df, _ = pyreadstat.read_sav(D + "d02.sav")
print("rows in file:", len(df))
df = df.dropna(how="all")
print("rows with any data:", len(df))
cells = ["avg_time_sum_ac", "avg_time_neutral_ac", "avg_time_sum_mu", "avg_time_neutral_mu"]
miss = df[cells].isna().any(axis=1)
print("rows with a missing cell mean (dropped):", int(miss.sum()))
df = df[~miss].copy()
n = len(df); print("N analysed:", n)

# check that the stored cell means relate to stored aggregates
print("check avg_sum == mean(sum_ac,sum_mu):", np.allclose(df.avg_sum, df[["avg_time_sum_ac","avg_time_sum_mu"]].mean(axis=1)))
print("check avg_AC == mean(sum_ac,neutral_ac):", np.allclose(df.avg_AC, df[["avg_time_sum_ac","avg_time_neutral_ac"]].mean(axis=1)))
print("\nTrials per cell (total / correct):")
for c in ["sum_ac","neutral_AC","sum_mu","neutral_MU"]:
    print(f"  {c}: total mean {df['no_'+c].mean():.2f} range {df['no_'+c].min():.0f}-{df['no_'+c].max():.0f}")
print("Error % per cell:", df[["error_sum_ac","error_neutral_ac","error_sum_mu","error_neutral_mu"]].mean().round(2).to_dict())

print("\nCell means (ms) and SD:")
print(df[cells].agg(["mean","std"]).round(1).to_string())

sAC = df.avg_time_sum_ac - df.avg_time_neutral_ac
sMU = df.avg_time_sum_mu - df.avg_time_neutral_mu
Dd = sAC - sMU

def onesample(x, label):
    x = np.asarray(x); k = len(x); m = x.mean(); sd = x.std(ddof=1); se = sd/np.sqrt(k)
    t = m/se; p = 2*stats.t.sf(abs(t), k-1); ci = m + np.array([-1,1])*stats.t.ppf(.975,k-1)*se
    dz = m/sd
    # CI for dz via noncentral t inversion
    from scipy.optimize import brentq
    lo = brentq(lambda nc: stats.nct.sf(t, k-1, nc) - .025, -50, 50)
    hi = brentq(lambda nc: stats.nct.cdf(t, k-1, nc) - .025, -50, 50)
    print(f"{label}: mean {m:.1f} ms, SD {sd:.1f}, 95% CI [{ci[0]:.1f}, {ci[1]:.1f}], t({k-1}) = {t:.3f}, p = {p:.4f}, dz = {dz:.3f} [{lo/np.sqrt(k):.3f}, {hi/np.sqrt(k):.3f}]")
    return t, p, dz

print("\n=== PRIMARY: word pair x target interaction ===")
t, p, dz = onesample(Dd, "D = (sum-neutral)_AC - (sum-neutral)_MU")
F = t**2
# MSE for interaction in 2x2 RM ANOVA: SS_effect = n*(mean D)^2/4 ; MSE = var(D)/4
mse = Dd.var(ddof=1)/4
ss_eff = n*Dd.mean()**2/4; ss_err = Dd.var(ddof=1)*(n-1)/4
pe2 = ss_eff/(ss_eff+ss_err)
print(f"Interaction F(1, {n-1}) = {F:.3f}, p = {p:.4f}, MSE = {mse:.1f}, partial eta^2 = {pe2:.3f}")
print("Direction predicted (mean D > 0):", Dd.mean() > 0)

print("\n=== Cross-check with full RM ANOVA (statsmodels AnovaRM) ===")
from statsmodels.stats.anova import AnovaRM
long = df[["id"]+cells].melt(id_vars="id", var_name="cell", value_name="rt")
long["pair"] = long.cell.str[-2:]; long["target"] = long.cell.str.split("_").str[2]
print(AnovaRM(long, "rt", "id", within=["pair","target"]).fit().anova_table.round(4).to_string())

print("\n=== Secondary checks ===")
onesample(sAC, "sum-neutral slowing after AC")
onesample(sMU, "sum-neutral slowing after MU")
w = stats.wilcoxon(Dd); print(f"Wilcoxon signed-rank on D: W = {w.statistic:.0f}, p = {w.pvalue:.4f}")
z = (Dd - Dd.mean())/Dd.std(ddof=1); keep = z.abs() <= 3
print("outliers |z|>3 on D:", int((~keep).sum()))
if (~keep).sum(): onesample(Dd[keep], "D without |z|>3")
print("share of participants with D > 0:", round((Dd > 0).mean(), 3))

fig, ax = plt.subplots(figsize=(4.2, 3.2))
m = df[cells].mean(); se = df[cells].std(ddof=1)/np.sqrt(n)
for lab, a, b, mk in [("AC (same category)", "avg_time_sum_ac", "avg_time_neutral_ac", "o"), ("MU (unrelated)", "avg_time_sum_mu", "avg_time_neutral_mu", "s")]:
    ax.errorbar([0,1], [m[b], m[a]], yerr=[se[b], se[a]], marker=mk, capsize=3, label=lab)
ax.set_xticks([0,1]); ax.set_xticklabels(["neutral target", "sum target"])
ax.set_ylabel("mean correct RT (ms), ±1 SE"); ax.legend(frameon=False, fontsize=8); ax.set_xlim(-.3, 1.3)
fig.tight_layout(); fig.savefig("papers/S20/report/fig1.png", dpi=150)
print("\nfigure written: papers/S20/report/fig1.png")
