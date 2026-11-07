"""S25: word-length effect in immediate serial recall (English lists). Run from the run directory:
.venv/bin/python -I papers/S25/report/analysis.py"""
import hashlib, io, os, numpy as np, pandas as pd
from scipy import stats

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
files = sorted(f for f in os.listdir(D) if f.endswith(".txt"))

def load(fn):
    lines = open(os.path.join(D, fn), encoding="utf-8", errors="replace").read().splitlines()
    hdr = [i for i, l in enumerate(lines) if l.startswith("list\t")][0]
    rows = [lines[hdr]] + [l for l in lines[hdr + 1:] if l.split("\t")[0] in ("EN", "NL")]
    return pd.read_csv(io.StringIO("\n".join(rows)), sep="\t")

data, seen = {}, {}
for fn in files:
    df = load(fn)
    key = hashlib.md5(df.to_csv(index=False).encode()).hexdigest()
    print(f"{fn}: {len(df)} trials, EN={sum(df.list=='EN')}, NL={sum(df.list=='NL')}", end="")
    if key in seen:
        print(f"  -> identical trial data to {seen[key]}; dropped as duplicate")
        continue
    seen[key] = fn; data[fn] = df; print()
print(f"\nDistinct participants: {len(data)}")

recs = []
for fn, df in data.items():
    assert len(df) == 80
    for (lang, ln), g in df.groupby(["list", "length"]):
        assert len(g) == 20
        m = (g.nr_correct / 8).mean()
        recs.append(dict(pid=fn, lang=lang, length={1: "short", 2: "long"}[ln], raw=m, dv=round(m, 3)))
cell = pd.DataFrame(recs)
w = cell.pivot_table(index="pid", columns=["lang", "length"], values="dv")
print("\nPer-participant DV (rounded to 3 decimals):\n", w.round(3).to_string())
print("\nCell means (SD):")
for c in w.columns: print(f"  {c}: {w[c].mean():.3f} ({w[c].std(ddof=1):.3f})")

def paired(a, b, label):
    d = a - b; n = len(d)
    t, p2 = stats.ttest_rel(a, b)
    p1 = stats.t.sf(t, n - 1)
    dz = t / np.sqrt(n)
    se = d.std(ddof=1) / np.sqrt(n); tc = stats.t.ppf(.975, n - 1)
    # 95% CI for d_z via noncentral t inversion
    from scipy.optimize import brentq
    lo = brentq(lambda nc: stats.nct.sf(t, n - 1, nc) - .025, -20, 20) / np.sqrt(n)
    hi = brentq(lambda nc: stats.nct.cdf(t, n - 1, nc) - .025, -20, 20) / np.sqrt(n)
    print(f"\n[{label}] n={n}, mean diff={d.mean():.4f} (SD {d.std(ddof=1):.4f}), 95% CI [{d.mean()-tc*se:.4f}, {d.mean()+tc*se:.4f}]")
    print(f"  t({n-1}) = {t:.3f}, one-sided p = {p1:.4g} (two-sided {p2:.4g}), d_z = {dz:.3f}, 95% CI d_z [{lo:.3f}, {hi:.3f}]")
    print(f"  participants with short > long: {(d>0).sum()}/{n}, equal: {(d==0).sum()}")
    return t, p1, dz, lo, hi, d

print("\n=== PRIMARY: English short vs long, paired t, one-sided (short > long) ===")
t, p1, dz, lo, hi, d = paired(w[("EN", "short")], w[("EN", "long")], "EN primary")

print("\n=== Robustness (not the basis of the conclusion) ===")
wr = cell.pivot_table(index="pid", columns=["lang", "length"], values="raw")
paired(wr[("EN", "short")], wr[("EN", "long")], "EN unrounded DV")
print("  Wilcoxon signed-rank EN (one-sided):", stats.wilcoxon(d, alternative="greater"))
paired(w[("NL", "short")], w[("NL", "long")], "NL (exploratory)")
inter = (w[("EN","short")]-w[("EN","long")]) - (w[("NL","short")]-w[("NL","long")])
ti = stats.ttest_1samp(inter, 0); print(f"\n[Language x length interaction] mean={inter.mean():.4f}, t(14)={ti.statistic:.3f}, two-sided p={ti.pvalue:.4g}")
# trial-level check: English, all trials
en = pd.concat([df.assign(pid=k) for k, df in data.items()]); en = en[en.list == "EN"]
print("\nTrial-level EN mean nr_correct/8 by length:", (en.groupby("length").nr_correct.mean()/8).round(4).to_dict())

# figure
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5, 3.4))
for i, (lang) in enumerate(["EN", "NL"]):
    s, l = w[(lang, "short")], w[(lang, "long")]
    x0 = i * 3
    for a, b in zip(s, l): ax.plot([x0, x0 + 1], [a, b], color="0.7", lw=.8)
    ax.errorbar([x0, x0 + 1], [s.mean(), l.mean()], yerr=[1.96*s.std(ddof=1)/np.sqrt(15), 1.96*l.std(ddof=1)/np.sqrt(15)], fmt="o-", color="k", capsize=3)
ax.set_xticks([0, 1, 3, 4]); ax.set_xticklabels(["EN short", "EN long", "NL short", "NL long"])
ax.set_ylabel("Proportion in correct position"); ax.set_title("Serial recall by word length (n = 15)")
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig1.png"), dpi=150)
print("\nfigure written: fig1.png")
