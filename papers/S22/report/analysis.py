"""S22 analysis: 4th-latency deviation from quadratic trend, grouped vs ungrouped, timing task."""
import numpy as np, pandas as pd
from scipy import stats
import pingouin as pg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "..", "data", "d03.csv"))
L = [f"Out sec {i}" for i in range(1, 7)]
print("rows", len(df), "subjects", df.Subject.nunique())
print("trials per subject x task x instruction:")
print(df.groupby(["Rhythm?", "Grouped?"]).size().rename("n_rows"))
cell = df.groupby(["Subject", "Rhythm?", "Grouped?"]).size()
print("cell counts min/max:", cell.min(), cell.max())

tim = df[df["Rhythm?"] == 1].copy()
print("missing latencies in timing trials:", int(tim[L].isna().sum().sum()))
print("non-positive latencies in timing trials:", int((tim[L] <= 0).sum().sum()))
print("latency summary (timing trials):")
print(tim[L].describe().round(3).to_string())

means = tim.groupby(["Subject", "Grouped?"])[L].mean()

def deviation(row):
    y = row.values
    x = np.array([2, 3, 5, 6]); yy = y[[1, 2, 4, 5]]
    c = np.polyfit(x, yy, 2)
    return y[3] - np.polyval(c, 4)

dev = means.apply(deviation, axis=1).unstack("Grouped?")
dev.columns = ["ungrouped", "grouped"]
print("\nDeviation of 4th latency from quadratic trend (s), per condition:")
print(dev.describe().round(4).to_string())

diff = dev.grouped - dev.ungrouped
t, p = stats.ttest_rel(dev.grouped, dev.ungrouped)
n = len(diff)
d_av = diff.mean() / np.sqrt((dev.grouped.var(ddof=1) + dev.ungrouped.var(ddof=1)) / 2)
d_z = diff.mean() / diff.std(ddof=1)
se = diff.std(ddof=1) / np.sqrt(n)
ci_md = diff.mean() + np.array([-1, 1]) * stats.t.ppf(0.975, n - 1) * se
rng = np.random.default_rng(1)
boots = []
for _ in range(10000):
    idx = rng.integers(0, n, n)
    g, u = dev.grouped.values[idx], dev.ungrouped.values[idx]
    boots.append((g - u).mean() / np.sqrt((g.var(ddof=1) + u.var(ddof=1)) / 2))
ci_d = np.percentile(boots, [2.5, 97.5])
print("\nPRIMARY: paired t-test, grouped vs ungrouped deviation")
print(f"N = {n}; mean grouped = {dev.grouped.mean():.4f} s (SD {dev.grouped.std():.4f}); "
      f"mean ungrouped = {dev.ungrouped.mean():.4f} s (SD {dev.ungrouped.std():.4f})")
print(f"mean diff = {diff.mean():.4f} s, 95% CI [{ci_md[0]:.4f}, {ci_md[1]:.4f}]")
print(f"t({n-1}) = {t:.3f}, p = {p:.3g}")
print(f"d_av = {d_av:.3f}, bootstrap 95% CI [{ci_d[0]:.3f}, {ci_d[1]:.3f}]; d_z = {d_z:.3f}")
print("subjects with grouped > ungrouped:", int((diff > 0).sum()), "of", n)

print("\nROBUSTNESS: Wilcoxon signed-rank on the difference")
w = stats.wilcoxon(dev.grouped, dev.ungrouped)
print(f"W = {w.statistic:.1f}, p = {w.pvalue:.3g}")
print("one-sample t of each condition's deviation vs 0:")
for c in ["ungrouped", "grouped"]:
    r = stats.ttest_1samp(dev[c], 0)
    print(f"  {c}: t(39) = {r.statistic:.3f}, p = {r.pvalue:.3g}")

print("\nSECONDARY: 2 x 6 RM ANOVA on per-subject mean latencies (timing task)")
long = means.reset_index().melt(id_vars=["Subject", "Grouped?"], value_vars=L, var_name="pos", value_name="lat")
long["pos"] = long.pos.str[-1].astype(int)
long = long.rename(columns={"Grouped?": "grouped"})
aov = pg.rm_anova(data=long, dv="lat", within=["grouped", "pos"], subject="Subject", correction=True)
print(aov.round(4).to_string())

print("\nMean latency by position (timing task):")
mp = long.groupby(["grouped", "pos"]).lat.mean().unstack()
print(mp.round(4).to_string())

print("\nCONTEXT: same deviation measure in the order (NUMBERS) task")
ordm = df[df["Rhythm?"] == 0].groupby(["Subject", "Grouped?"])[L].mean()
odev = ordm.apply(deviation, axis=1).unstack("Grouped?"); odev.columns = ["ungrouped", "grouped"]
r = stats.ttest_rel(odev.grouped, odev.ungrouped)
print(f"order task: mean dev ungrouped {odev.ungrouped.mean():.4f}, grouped {odev.grouped.mean():.4f}; "
      f"t(39) = {r.statistic:.3f}, p = {r.pvalue:.3g}")

fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
for g, lab in [(0, "ungrouped"), (1, "grouped")]:
    m = long[long.grouped == g].groupby("pos").lat
    ax[0].errorbar(range(1, 7), m.mean(), yerr=m.sem(), marker="o", capsize=3, label=lab)
ax[0].set_xlabel("output position"); ax[0].set_ylabel("mean latency (s)"); ax[0].set_title("Timing task latencies"); ax[0].legend()
for i in range(n):
    ax[1].plot([0, 1], [dev.ungrouped.iloc[i], dev.grouped.iloc[i]], color="grey", alpha=0.4, lw=0.8)
ax[1].plot([0, 1], [dev.ungrouped.mean(), dev.grouped.mean()], color="k", marker="o", lw=2)
ax[1].axhline(0, ls=":", color="k"); ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["ungrouped", "grouped"])
ax[1].set_ylabel("4th-latency deviation (s)"); ax[1].set_title("Per-participant deviation")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig1.png"), dpi=150)
print("\nfigure written: fig1.png")

print("\nSENSITIVITY (post hoc, not planned as primary): extreme trial latencies")
print("timing-trial latencies > 5 s:", int((tim[L] > 5).sum().sum()), "of", tim[L].size)
for lab, agg in [("per-cell medians instead of means", "median")]:
    mm = tim.groupby(["Subject", "Grouped?"])[L].agg(agg)
    dv = mm.apply(deviation, axis=1).unstack("Grouped?"); dv.columns = ["ungrouped", "grouped"]
    r = stats.ttest_rel(dv.grouped, dv.ungrouped)
    print(f"  {lab}: diff {(dv.grouped-dv.ungrouped).mean():.4f}; t(39) = {r.statistic:.3f}, p = {r.pvalue:.3g}")
tt = tim.copy(); tt[L] = tt[L].where(tt[L] <= 5)
mm = tt.groupby(["Subject", "Grouped?"])[L].mean()
dv = mm.apply(deviation, axis=1).unstack("Grouped?"); dv.columns = ["ungrouped", "grouped"]
r = stats.ttest_rel(dv.grouped, dv.ungrouped)
print(f"  latencies > 5 s set missing: diff {(dv.grouped-dv.ungrouped).mean():.4f}; t(39) = {r.statistic:.3f}, p = {r.pvalue:.3g}")
