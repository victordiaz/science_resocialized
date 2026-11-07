import numpy as np, pandas as pd
from scipy import stats
import os
here = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(here, "..", "data", "d07.csv"), low_memory=False)
print("rows", len(df))
for c in ["exppref","d","fastpct10","alltrials","rateorig","imppref"]:
    print(c, "NA:", df[c].isna().sum())
steps = [("exppref NA", lambda x: x["exppref"].notna()),
         ("d NA", lambda x: x["d"].notna()),
         ("fastpct10 == 1", lambda x: x["fastpct10"] != 1),
         ("alltrials != 200", lambda x: x["alltrials"] == 200),
         ("rateorig NA", lambda x: x["rateorig"].notna()),
         ("imppref NA", lambda x: x["imppref"].notna())]
s = df
for name, f in steps:
    keep = s[f(s)]
    print(f"exclude {name}: {len(s)-len(keep)} -> {len(keep)} left")
    s = keep
print("N analysed", len(s))
print("rateorig counts", s["rateorig"].value_counts().to_dict())
new = s.loc[s.rateorig == 0, "imppref"].values
orig = s.loc[s.rateorig == 1, "imppref"].values
for lab, v in [("new pair (rateorig 0)", new), ("original pair (rateorig 1)", orig)]:
    t1 = stats.ttest_1samp(v, 0)
    print(f"{lab}: n={len(v)} mean={v.mean():.4f} sd={v.std(ddof=1):.4f} vs0 t={t1.statistic:.2f} p={t1.pvalue:.3g}")
# primary: Welch
w = stats.ttest_ind(new, orig, equal_var=False)
n1, n2 = len(new), len(orig)
v1, v2 = new.var(ddof=1), orig.var(ddof=1)
dfw = (v1/n1 + v2/n2)**2 / ((v1/n1)**2/(n1-1) + (v2/n2)**2/(n2-1))
diff = new.mean() - orig.mean()
se = np.sqrt(v1/n1 + v2/n2)
tc = stats.t.ppf(.975, dfw)
print(f"PRIMARY Welch t({dfw:.1f}) = {w.statistic:.3f}, p = {w.pvalue:.3g}; mean diff (new-orig) = {diff:.4f} [{diff-tc*se:.4f}, {diff+tc*se:.4f}]")
sp = np.sqrt(((n1-1)*v1 + (n2-1)*v2)/(n1+n2-2))
d = diff/sp
sed = np.sqrt((n1+n2)/(n1*n2) + d**2/(2*(n1+n2)))
print(f"Cohen d (pooled) = {d:.3f}, 95% CI [{d-1.96*sed:.3f}, {d+1.96*sed:.3f}]")
# TOST at +/-0.2 d
lo, hi = -0.2*sp, 0.2*sp
tl = (diff-lo)/se; th = (diff-hi)/se
p_tost = max(1-stats.t.cdf(tl, dfw), stats.t.cdf(th, dfw))
print(f"TOST +/-0.2 d: p = {p_tost:.3g}")
# robustness
st = stats.ttest_ind(new, orig)
print(f"Student t({n1+n2-2}) = {st.statistic:.3f}, p = {st.pvalue:.3g}")
mw = stats.mannwhitneyu(new, orig)
print(f"Mann-Whitney U = {mw.statistic:.0f}, p = {mw.pvalue:.3g}")
print("ratio of means new/orig", new.mean()/orig.mean())
# companion: self-report
en = s.loc[s.rateorig == 0, "exppref"]; eo = s.loc[s.rateorig == 1, "exppref"]
we = stats.ttest_ind(en, eo, equal_var=False)
print(f"self-report exppref: new mean={en.mean():.3f} orig mean={eo.mean():.3f}; Welch t={we.statistic:.2f} p={we.pvalue:.3g}")
# figure
# assignment balance check
print("raw rateorig counts", df["rateorig"].value_counts(dropna=False).to_dict())
print("binomial test of analysed group sizes vs 50/50: p =", f"{stats.binomtest(int((s.rateorig==1).sum()), len(s)).pvalue:.3g}")
print("exclusion rate by group (among rows with rateorig):",
      (df.groupby('rateorig').apply(lambda g: 1 - g.index.isin(s.index).mean())).round(3).to_dict())
# figure
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(4.5, 3.2))
ms = [new.mean(), orig.mean()]
ci = [stats.t.ppf(.975, len(v)-1)*v.std(ddof=1)/np.sqrt(len(v)) for v in (new, orig)]
ax.bar([0, 1], ms, yerr=ci, capsize=6, color=["#8aa6c1", "#3b6a94"], width=0.55)
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks([0, 1]); ax.set_xticklabels([f"New pair\n(n={len(new)})", f"Original pair\n(n={len(orig)})"])
ax.set_ylabel("imppref (mean, 95% CI)")
fig.tight_layout(); fig.savefig(os.path.join(here, "fig1.png"), dpi=200)
print("figure written fig1.png")
