"""Row.6 (node atgp5): paired t-test, RT to correct rejections vs RT to misses.
Key test written from the replication report and RPP_atgp5.R before opening data:
  two-sided paired t-test of per-participant mean identification RT for
  correct rejections (new word judged new) vs misses (old word judged new);
  N.R = 32; table t(31) = 2.40, p = .023, d = .424 (d = t/sqrt(n)).
Run with: .venv/bin/python -I reproduce.py  (from this folder or any folder)
"""
import os, math
import pandas as pd, numpy as np
from scipy import stats
import pyreadstat

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "download", "Data")

# 1. The aggregate file the audit script reads (OSF btr65)
agg = pd.read_csv(os.path.join(D, "Agg_priming_ANOVA.dat"), sep="\t", encoding="utf-8-sig")
print("Agg_priming_ANOVA.dat shape:", agg.shape, "columns:", list(agg.columns))
print("NA per column:", agg.isna().sum().to_dict())
cr, miss = agg["meanRT_cr"].astype(float), agg["meanRT_miss"].astype(float)
n = len(agg)
t, p = stats.ttest_rel(cr, miss)
diff = cr - miss
dz = diff.mean() / diff.std(ddof=1)
print(f"\n[aggregate file] n={n}  mean CR={cr.mean():.2f}  mean miss={miss.mean():.2f}  mean diff (CR-miss)={diff.mean():.2f} ms, SEM={diff.std(ddof=1)/math.sqrt(n):.2f}")
print(f"[aggregate file] paired t({n-1}) = {t:.4f}, p = {p:.6f}, dz = mean/sd = {dz:.4f}, t/sqrt(n) = {t/math.sqrt(n):.4f}")
print(f"[aggregate file] participants with CR slower than miss: {(diff>0).sum()} of {n}")

# 2. Independent check from the trial-level file: aggregate it myself.
raw, meta = pyreadstat.read_sav(os.path.join(D, "Analysedaten_1.sav"))
print("\nAnalysedaten_1.sav shape:", raw.shape, " unique vpnum:", raw["vpnum"].nunique())
test = raw[(raw["phase"] == 2)]
print("test-phase trials:", len(test), " of which correctly identified (word_korrekt==1):", int((test["word_korrekt"] == 1).sum()))
# The protocol says misidentification trials at study or test are excluded.
# I build three aggregations and compare each with the shipped aggregate file.
test = test[test["SDT_category"].isin([1, 2, 3, 4])].copy()   # code 0 is unlabelled (3 trials, no old/new category)
print("test trials with a labelled SDT category (1-4):", len(test))
study_bad = set(zip(*raw[(raw["phase"] == 1) & (raw["word_korrekt"] == 0)][["vpnum", "word"]].values.T))
print("study-phase misidentified trials:", len(study_bad))
test["study_bad"] = [(v, w) in study_bad for v, w in zip(test["vpnum"], test["word"])]
labels = meta.variable_value_labels["SDT_category"]
aggi = agg.set_index("vpnum")
variants = {
    "A: all labelled test trials (no identification filter)": test,
    "B: test misidentifications excluded": test[test["word_korrekt"] == 1],
    "C: test and study misidentifications excluded (protocol text)": test[(test["word_korrekt"] == 1) & (~test["study_bad"])],
}
for name, sub in variants.items():
    g = sub.groupby(["vpnum", "SDT_category"])["tresp"].mean().unstack()
    g.columns = [labels[c] for c in g.columns]
    if g[["correct rejection", "miss"]].isna().any(axis=1).any():
        print(f"    [{name}] participants with no trial in CR or miss, dropped: {list(g.index[g[['correct rejection','miss']].isna().any(axis=1)])}")
        g = g.dropna(subset=["correct rejection", "miss"])
    tt, pp = stats.ttest_rel(g["correct rejection"], g["miss"])
    nn = len(g)
    dcr = (g["correct rejection"] - aggi["meanRT_cr"]).abs()
    dmi = (g["miss"] - aggi["meanRT_miss"]).abs()
    print(f"[{name}] trials={len(sub)} n={nn}  paired t({nn-1}) = {tt:.4f}, p = {pp:.6f}, t/sqrt(n) = {tt/math.sqrt(nn):.4f}")
    print(f"    vs shipped aggregate: participants matching exactly CR {int((dcr<1e-6).sum())}/32, miss {int((dmi<1e-6).sum())}/32; max abs diff CR {dcr.max():.2f} ms, miss {dmi.max():.2f} ms")
