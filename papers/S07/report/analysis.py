"""S07: contrast sunny - cloudy among correlations of game casting scores with polydrug use.
Run from the run directory: .venv/bin/python -I papers/S07/report/analysis.py"""
import numpy as np, pandas as pd
from scipy import stats

D = "papers/S07/data/"
LAM = np.array([1, -1, 1, -1])           # KS, KC, RS, RC: sunny minus cloudy
CONDS = ["KS", "KC", "RS", "RC"]

# ---------- casting scores from the raw trial file ----------
tr = pd.read_stata(D + "d08.dta")
print("trial rows:", len(tr), "| rows with missing id (dropped):", tr.id.isna().sum())
tr = tr.dropna(subset=["id"])
print("exact duplicate rows (all columns):", tr.duplicated().sum())
tr["cond"] = tr.release_rule.map({"Keep": "K", "Release": "R"}).astype(str) + tr.weather.map({"Clear": "S", "Cloudy": "C"}).astype(str)

def scores(t):
    s = t[t.bluefish == 0].groupby(["id", "cond"]).casts.mean().unstack()[CONDS]
    return s

cast_all = scores(tr)                                   # all rounds (as the card's cleaning script does)
cast_test = scores(tr[tr.practice == "test"])           # robustness: practice rounds removed
print("participants with casting scores:", len(cast_all), "| missing any condition:", cast_all.isna().any(axis=1).sum())

# ---------- polydrug from the item-level questionnaire ----------
q = pd.read_stata(D + "d11.dta")
ever = q[q.qType == 0].pivot_table(index="id", columns="qID", values="answer")
most = q[q.qType == 2].pivot_table(index="id", columns="qID", values="answer")
most.columns = [int(c) - 2 for c in most.columns]       # align with the "ever used" item of the same class
most = most.reindex(index=ever.index, columns=ever.columns)   # participants who never used any drug have no frequency rows
rank = most.where(ever == 1).fillna(1)                   # never used (ever==2) -> rank 1 ("never")
poly = (rank - 1).sum(axis=1).rename("polydrug")
print("drug questionnaire: participants", len(poly), "| classes", ever.shape[1])

# ---------- cross-checks against the cleaned files ----------
d10 = pd.read_stata(D + "d10.dta").set_index("id")
d09 = pd.read_stata(D + "d09.dta").set_index("id")
cmp = cast_all.join(d10[CONDS].add_suffix("_clean"), how="inner")
for c in CONDS:
    print(f"check {c}: max |raw - cleaned| = {np.nanmax(np.abs(cmp[c] - cmp[c + '_clean'])):.4f}")
pc = poly.to_frame().join(d09.polydrug.rename("clean"), how="inner")
print("check polydrug: n =", len(pc), "| max |raw - cleaned| =", np.abs(pc.polydrug - pc.clean).max())

# ---------- analysis sample ----------
df = cast_all.join(poly, how="inner").dropna()
N = len(df)
print(f"\nSample: {len(cast_all)} with game data; {len(cast_all) - cast_all.index.isin(poly.index).sum()} without a drug score dropped; N = {N} with all five values")
print(df.describe().round(2).T)

def mrr(d, verbose=False):
    n = len(d)
    r = np.array([stats.pearsonr(d[c], d.polydrug)[0] for c in CONDS])
    z = np.arctanh(r)
    R = d[CONDS].corr().values
    rx = np.median(R[np.triu_indices(4, 1)])
    r2 = np.mean(r ** 2)
    f = min((1 - rx) / (2 * (1 - r2)), 1.0)
    h = (1 - f * r2) / (1 - r2)
    Z = (LAM @ z) * np.sqrt((n - 3) / ((LAM ** 2).sum() * (1 - rx) * h))
    if verbose:
        for c, ri, zi in zip(CONDS, r, z):
            print(f"  r(polydrug, {c}) = {ri:.3f}  (z = {zi:.3f}, p = {stats.pearsonr(d[c], d.polydrug)[1]:.4f})")
        print("  inter-correlations of casting scores:\n", np.round(R, 3))
        print(f"  r_x (median inter-corr) = {rx:.3f}; mean r^2 = {r2:.4f}; f = {f:.3f}; h = {h:.4f}")
    return Z, r, z, rx

print("\n=== PRIMARY: Meng-Rosenthal-Rubin contrast, weights (+1,-1,+1,-1) on (KS,KC,RS,RC) ===")
Z, r, z, rx = mrr(df, verbose=True)
p = 2 * stats.norm.sf(abs(Z))
dz = (LAM @ z) / 2                                         # mean sunny z minus mean cloudy z
rng = np.random.default_rng(20261107)
boot = []
idx = np.arange(N)
for _ in range(5000):
    b = df.iloc[rng.choice(idx, N, replace=True)]
    zb = np.arctanh([np.corrcoef(b[c], b.polydrug)[0, 1] for c in CONDS])
    boot.append((LAM @ zb) / 2)
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"  N = {N}; Z = {Z:.3f}; two-sided p = {p:.4f}")
print(f"  contrast (mean z sunny - mean z cloudy) = {dz:.3f}, 95% bootstrap CI [{lo:.3f}, {hi:.3f}] (5000 resamples)")
print(f"  r_contrast = Z/sqrt(N) = {Z/np.sqrt(N):.3f}")
print(f"  mean r sunny = {np.mean(r[[0,2]]):.3f}; mean r cloudy = {np.mean(r[[1,3]]):.3f}")

print("\n=== Robustness (not primary) ===")
Zs, *_ = mrr(df.rank()); print(f"  Spearman (ranks) MRR Z = {Zs:.3f}, p = {2*stats.norm.sf(abs(Zs)):.4f}")
dl = df.copy(); dl["polydrug"] = np.log1p(dl.polydrug)
Zl, *_ = mrr(dl); print(f"  log(1+polydrug) MRR Z = {Zl:.3f}, p = {2*stats.norm.sf(abs(Zl)):.4f}")
dt = cast_test.join(poly, how="inner").dropna()
Zt, rt, *_ = mrr(dt); print(f"  practice rounds removed (N={len(dt)}) MRR Z = {Zt:.3f}, p = {2*stats.norm.sf(abs(Zt)):.4f}; r = {np.round(rt,3)}")
dc = d10[CONDS + ["polydrug"]].dropna()
Zc, rc, *_ = mrr(dc); print(f"  cleaned file d10 as given (N={len(dc)}) MRR Z = {Zc:.3f}, p = {2*stats.norm.sf(abs(Zc)):.4f}; r = {np.round(rc,3)}")
for w, lab in [([1,-1,0,0], "Keep only (KS-KC)"), ([0,0,1,-1], "Release only (RS-RC)")]:
    print(f"  {lab}: z diff = {np.dot(w, z):.3f}")

# ---------- figure ----------
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.5, 3))
    lo_r = np.tanh(z - 1.96 / np.sqrt(N - 3)); hi_r = np.tanh(z + 1.96 / np.sqrt(N - 3))
    ax.errorbar(range(4), r, yerr=[r - lo_r, hi_r - r], fmt="o", capsize=4, color="k")
    ax.axhline(0, lw=0.5, color="grey"); ax.set_xticks(range(4)); ax.set_xticklabels(["Keep\nsunny", "Keep\ncloudy", "Release\nsunny", "Release\ncloudy"])
    ax.set_ylabel("r with polydrug (95% CI)"); fig.tight_layout(); fig.savefig("papers/S07/report/fig1.png", dpi=150)
    print("\nfigure written: papers/S07/report/fig1.png")
except ImportError:
    print("\nmatplotlib not available; no figure")
