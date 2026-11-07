"""S02 analysis: misses vs correct rejections in identification RT.
Run from the run directory: .venv/bin/python -I papers/S02/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
from scipy.optimize import brentq

D = "papers/S02/data/"

def dz_ci(t, n, level=.95):
    """Noncentral-t CI for dz in a paired design."""
    df = n - 1
    a = (1 - level) / 2
    lo = brentq(lambda d: stats.nct.sf(t, df, d * np.sqrt(n)) - a, -10, 10)
    hi = brentq(lambda d: stats.nct.cdf(t, df, d * np.sqrt(n)) - a, -10, 10)
    return lo, hi

def paired(cr, miss, label):
    d = cr - miss
    n = len(d)
    t, p = stats.ttest_rel(cr, miss)
    se = d.std(ddof=1) / np.sqrt(n)
    tc = stats.t.ppf(.975, n - 1)
    dz = t / np.sqrt(n)
    lo, hi = dz_ci(t, n)
    w = stats.wilcoxon(cr, miss)
    print(f"--- {label}")
    print(f"n = {n}; mean CR = {cr.mean():.1f} (SD {cr.std(ddof=1):.1f}); mean miss = {miss.mean():.1f} (SD {miss.std(ddof=1):.1f})")
    print(f"mean diff CR - miss = {d.mean():.2f} ms, SD diff = {d.std(ddof=1):.2f}, 95% CI [{d.mean()-tc*se:.2f}, {d.mean()+tc*se:.2f}]")
    print(f"t({n-1}) = {t:.3f}, p (two-sided) = {p:.4f}; dz = {dz:.3f}, 95% CI [{lo:.3f}, {hi:.3f}]")
    print(f"participants with CR > miss: {(d>0).sum()}/{n}; Wilcoxon W = {w.statistic:.1f}, p = {w.pvalue:.4f}")
    return dict(n=n, t=t, p=p, dz=dz, lo=lo, hi=hi, diff=d.mean(), dlo=d.mean()-tc*se, dhi=d.mean()+tc*se)

# ---------- primary: d07.dat aggregate file ----------
a = pd.read_csv(D + "d07.dat", sep="\t", encoding="utf-8-sig")
print("d07 shape", a.shape); print(a.describe().round(1).to_string())
print("missing in key cols:", a[["meanRT_cr", "meanRT_miss"]].isna().sum().to_dict())
prim = paired(a.meanRT_cr, a.meanRT_miss, "PRIMARY: d07.dat, paired t, meanRT_cr vs meanRT_miss")

# ---------- checks: trial-level d14.sav ----------
tr, _ = pyreadstat.read_sav(D + "d14.sav")
test = tr[tr.phase == 2].copy()
print("\ntest trials per participant:", test.groupby("vpnum").size().unique())
print(pd.crosstab([test.word_type, test.rating], test.SDT_category, dropna=False))
# verify which SDT code is which cell by reproducing d07 means
m = test[test.SDT_category > 0].groupby(["vpnum", "SDT_category"]).tresp.mean().unstack()
for col in ["meanRT_hit", "meanRT_cr", "meanRT_fa", "meanRT_miss"]:
    match = {c: np.allclose(m[c].values, a[col].values, equal_nan=True) for c in m.columns}
    print(col, "matches SDT code:", [c for c, v in match.items() if v])

# ---------- robustness: protocol identification filter on trials ----------
study = tr[tr.phase == 1]
bad_study = set(zip(study.vpnum[study.word_korrekt == 0], study.word[study.word_korrekt == 0]))
test["bad_study"] = [(v, w) in bad_study for v, w in zip(test.vpnum, test.word)]
print("\nstudy-phase misidentifications:", (study.word_korrekt == 0).sum(),
      "| test-phase misidentifications:", (test.word_korrekt == 0).sum(),
      "| studied test words misidentified at study:", test.bad_study.sum(),
      "| test trials with tresp >= 3750 (no response):", (test.tresp >= 3750).sum())
# check study words are found at test
sw = study[study.word_type.notna()]
print("studied (non-filler) words per participant found among test old items:",
      sorted(set(sw.groupby('vpnum').word.apply(lambda s: s.isin(test.loc[(test.vpnum==s.name)&(test.word_type==0),'word']).sum()))))

def cellmeans(df):
    g = df[df.SDT_category.isin([2, 4])].groupby(["vpnum", "SDT_category"]).tresp
    m = g.mean().unstack(); k = g.size().unstack()
    return m, k

f1 = test[(test.word_korrekt == 1) & (~test.bad_study)]
m1, k1 = cellmeans(f1)
print("trials per participant after filter: miss min/median", k1[4].min(), k1[4].median(), "| CR min/median", k1[2].min(), k1[2].median())
ok = m1.dropna()
r1 = paired(ok[2], ok[4], "ROBUSTNESS A: trial-level, identification filter (protocol)")
f2 = f1[f1.tresp < 3750]
m2, _ = cellmeans(f2); ok2 = m2.dropna()
r2 = paired(ok2[2], ok2[4], "ROBUSTNESS B: as A, plus no-response trials (tresp >= 3750) dropped")
# per-participant medians instead of means (unfiltered, as d07)
m3 = test[test.SDT_category.isin([2, 4])].groupby(["vpnum", "SDT_category"]).tresp.median().unstack().dropna()
r3 = paired(m3[2], m3[4], "ROBUSTNESS C: per-participant median RT, no filter")
print("\nmiss trials per participant (unfiltered): min", test[test.SDT_category==4].groupby('vpnum').size().min(),
      "median", test[test.SDT_category==4].groupby('vpnum').size().median())

# ---------- figure ----------
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    for c, mi in zip(a.meanRT_cr, a.meanRT_miss):
        ax.plot([0, 1], [mi, c], color="0.7", lw=.8)
    ax.plot([0, 1], [a.meanRT_miss.mean(), a.meanRT_cr.mean()], "k-o", lw=2)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Miss", "Correct rejection"]); ax.set_xlim(-.3, 1.3)
    ax.set_ylabel("Mean identification RT (ms)"); fig.tight_layout()
    fig.savefig("papers/S02/report/fig1.png", dpi=150); print("figure written")
except ImportError:
    print("matplotlib not available; no figure")
