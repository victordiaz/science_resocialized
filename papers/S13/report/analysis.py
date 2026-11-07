"""S13 analysis: distractor-centroid localisation error vs empirical chance (guessing).
Run from the S13 run directory: .venv/bin/python -I papers/S13/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df, _ = pyreadstat.read_dta("papers/S13/data/d19.dta")
print("rows", df.shape, "subjects", df.subject.nunique(), "missing angle", df.angle.isna().sum())
ex = df[df.ExGuess == "experimental"]; gu = df[df.ExGuess == "guessing"]

def paired(a, b, label):
    d = (a - b).dropna(); n = len(d)
    t, p = stats.ttest_rel(a, b)
    dz = t / np.sqrt(n)
    # 95% CI for dz via noncentral t inversion
    grid = np.linspace(t - 8, t + 8, 16001)
    sf = stats.nct.sf(t, n - 1, grid)            # increasing in nc
    ok = np.isfinite(sf)
    lo_nc = grid[ok][np.argmin(np.abs(sf[ok] - 0.025))]
    hi_nc = grid[ok][np.argmin(np.abs(sf[ok] - 0.975))]
    se = d.std(ddof=1) / np.sqrt(n); q = stats.t.ppf(.975, n - 1)
    w = stats.wilcoxon(a, b)
    print(f"{label}: n={n} mean_a={a.mean():.3f} mean_b={b.mean():.3f} diff={d.mean():.3f} "
          f"95%CI[{d.mean()-q*se:.3f},{d.mean()+q*se:.3f}] t({n-1})={t:.3f} p={p:.4g} "
          f"dz={dz:.3f} 95%CI[{lo_nc/np.sqrt(n):.3f},{hi_nc/np.sqrt(n):.3f}] | Wilcoxon W={w.statistic:.0f} p={w.pvalue:.4g}")
    return t, p, dz, n, d

m = lambda sub: sub.groupby("subject").angle.mean()

# Step 1: manipulation check to identify the distractor code (individual test, test phase)
ind1 = m(ex[(ex.one_vs_four == 1) & (ex.tar_vs_dis == 1)])
ind11 = m(ex[(ex.one_vs_four == 1) & (ex.tar_vs_dis == 11)])
print("\n-- Mapping check: single-dot test-phase error, code 1 vs code 11")
t0, p0, *_ = paired(ind1, ind11, "code1 - code11 (individual)")
dis_code = 1 if ind1.mean() > ind11.mean() else 11
tar_code = 11 if dis_code == 1 else 1
print(f"=> distractor code = {dis_code} (larger single-dot error), target code = {tar_code}; check p={p0:.3g}")

# Step 2: primary test
guess4 = m(gu[gu.one_vs_four == 4])
dis4 = m(ex[(ex.one_vs_four == 4) & (ex.tar_vs_dis == dis_code)])
print("\n-- PRIMARY: distractor centroid (test) minus guessing four-missing")
print("trials per subject: test", ex[(ex.one_vs_four == 4) & (ex.tar_vs_dis == dis_code)].groupby("subject").size().unique(),
      "guess", gu[gu.one_vs_four == 4].groupby("subject").size().unique())
t, p, dz, n, d = paired(dis4, guess4, "PRIMARY dis-centroid - guess4")

print("\n-- Same comparison under the other mapping (sensitivity to the code assignment)")
paired(m(ex[(ex.one_vs_four == 4) & (ex.tar_vs_dis == tar_code)]), guess4, "other-code centroid - guess4")

print("\n-- Secondary")
guess1 = m(gu[gu.one_vs_four == 1])
paired(m(ex[(ex.one_vs_four == 1) & (ex.tar_vs_dis == dis_code)]), guess1, "dis-individual - guess1")
paired(m(ex[(ex.one_vs_four == 1) & (ex.tar_vs_dis == tar_code)]), guess1, "tar-individual - guess1")
paired(m(ex[(ex.one_vs_four == 4) & (ex.tar_vs_dis == tar_code)]), guess4, "tar-centroid - guess4")
paired(m(ex[(ex.one_vs_four == 4) & (ex.tar_vs_dis == tar_code)]), dis4, "tar-centroid - dis-centroid")
# guessing: displays generated as cond 3 vs 4 should not differ
paired(m(gu[gu.condition == 3]), m(gu[gu.condition == 4]), "guess cond3 - cond4")
# robustness: trial-level medians instead of means
med = lambda sub: sub.groupby("subject").angle.median()
paired(med(ex[(ex.one_vs_four == 4) & (ex.tar_vs_dis == dis_code)]), med(gu[gu.one_vs_four == 4]), "ROBUST medians dis-centroid - guess4")

print("\nPer-subject means (dis-centroid, guess4, diff):")
print(pd.DataFrame({"dis_centroid": dis4, "guess4": guess4, "diff": dis4 - guess4}).round(3).to_string())

fig, ax = plt.subplots(figsize=(4.2, 3.6))
for s in dis4.index:
    ax.plot([0, 1], [guess4[s], dis4[s]], color="grey", lw=.8, marker="o", ms=3)
ax.plot([0, 1], [guess4.mean(), dis4.mean()], color="black", lw=2.5, marker="s")
ax.set_xticks([0, 1]); ax.set_xticklabels(["Guessing\n(4 missing)", "Test: distractor\ncentroid"])
ax.set_ylabel("Mean localisation error (deg)"); ax.set_xlim(-.3, 1.3)
fig.tight_layout(); fig.savefig("papers/S13/report/fig1.png", dpi=150)
print("figure saved")
