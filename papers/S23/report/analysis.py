"""S23 analysis: MSE of guess 1 vs MSE of average of guess 1 and delayed guess 2."""
import numpy as np, pandas as pd
from scipy import stats

D = "papers/S23/data/"
TRUTH = np.array([6.3, 43.3, 32.3, 13.4, 53.6, 54.8, 26.4, 22.4])
Q = [f"q{i}" for i in range(1, 9)]
DF = [f"defocus_q{i}" for i in range(1, 9)]

s1 = pd.read_csv(D + "d04.txt", sep="\t", na_values=["NaN"])
s2 = pd.read_csv(D + "d05.txt", sep="\t", na_values=["NaN"])
print("rows: session1", len(s1), "session2", len(s2))
for name, s in (("s1", s1), ("s2", s2)):
    dup = s["student_number_simple"].duplicated(keep=False)
    print(name, "IDs duplicated within session:", int(dup.sum()), "rows;",
          sorted(s.loc[dup, "student_number_simple"].unique().tolist()))
print("peaking values:", s2["peaking"].value_counts(dropna=False).to_dict())

def dedup(s):
    return s[~s["student_number_simple"].duplicated(keep=False)]

m_raw = s1.merge(s2, on="student_number_simple", suffixes=("_1", "_2"))
print("matched rows (all, incl. duplicate IDs):", len(m_raw))
m = dedup(s1).merge(dedup(s2), on="student_number_simple", suffixes=("_1", "_2"))
print("matched participants (unique IDs):", len(m))

g1 = m[[q + "_1" for q in Q]].apply(pd.to_numeric, errors="coerce").to_numpy(float)
g2 = m[[q + "_2" for q in Q]].apply(pd.to_numeric, errors="coerce").to_numpy(float)
defoc = (m[[d + "_1" for d in DF] + [d + "_2" for d in DF]].fillna(0).to_numpy() == 1).any(axis=1)
missing = np.isnan(g1).any(axis=1) | np.isnan(g2).any(axis=1)
peek = m["peaking"].astype(str).str.strip() != "Nee"
print(f"excluded flags (overlapping): defocus={defoc.sum()}, missing={missing.sum()}, peaking={peek.sum()}")
# sequential counts
k = np.ones(len(m), bool)
for lab, f in (("defocus", defoc), ("missing answer", missing), ("peaking", peek)):
    print(f"  sequential: removed for {lab}: {(k & f).sum()}")
    k &= ~f
print("n after exclusions:", k.sum())

def mses(g1, g2):
    mse1 = ((g1 - TRUTH) ** 2).mean(axis=1)
    mse2 = ((g2 - TRUTH) ** 2).mean(axis=1)
    mavg = (((g1 + g2) / 2 - TRUTH) ** 2).mean(axis=1)
    return mse1, mse2, mavg

def paired(a, b, label):
    d = a - b
    n = len(d)
    t, p = stats.ttest_rel(a, b)
    dz = d.mean() / d.std(ddof=1)
    se = d.std(ddof=1) / np.sqrt(n)
    tc = stats.t.ppf(0.975, n - 1)
    ci = (d.mean() - tc * se, d.mean() + tc * se)
    # CI for d_z via noncentral t inversion
    from scipy.optimize import brentq
    lo = brentq(lambda nc: stats.nct.sf(t, n - 1, nc) - 0.025, t - 10, t + 10) / np.sqrt(n)
    hi = brentq(lambda nc: stats.nct.cdf(t, n - 1, nc) - 0.025, t - 10, t + 10) / np.sqrt(n)
    p1 = stats.t.sf(t, n - 1)
    print(f"{label}: n={n}, mean A={a.mean():.2f} (SD {a.std(ddof=1):.2f}), mean B={b.mean():.2f} (SD {b.std(ddof=1):.2f})")
    print(f"   mean diff A-B={d.mean():.2f}, 95% CI [{ci[0]:.2f}, {ci[1]:.2f}]; t({n-1})={t:.3f}, p two-sided={p:.3g}, one-sided={p1:.3g}")
    print(f"   d_z={dz:.3f}, 95% CI [{lo:.3f}, {hi:.3f}]; share with A>B: {(d>0).mean():.3f}")
    w = stats.wilcoxon(a, b)
    print(f"   Wilcoxon signed-rank: W={w.statistic:.1f}, p={w.pvalue:.3g}")
    return t, p, dz, (lo, hi), d

mse1, mse2, mavg = mses(g1[k], g2[k])
print("\n=== PRIMARY: MSE(guess1) vs MSE(average), delayed condition, after exclusions ===")
t, p, dz, ci, d = paired(mse1, mavg, "MSE1 vs MSEavg")
print("\n--- descriptive: MSE(guess2) vs MSE(average) ---")
paired(mse2, mavg, "MSE2 vs MSEavg")
print("\n--- descriptive: MSE1 vs MSE2 ---")
paired(mse1, mse2, "MSE1 vs MSE2")

ok = ~missing
a1, a2, aa = mses(g1[ok], g2[ok])
print("\n--- robustness: no exclusions except missing answers ---")
paired(a1, aa, "MSE1 vs MSEavg (all complete)")

# per-question
print("\n--- per question, squared error of g1 vs avg (after exclusions), means ---")
e1 = (g1[k] - TRUTH) ** 2; ea = ((g1[k] + g2[k]) / 2 - TRUTH) ** 2
for i in range(8):
    print(f"   q{i+1}: SE1={e1[:, i].mean():.1f}  SEavg={ea[:, i].mean():.1f}")
r = np.array([np.corrcoef(g1[k][:, i], g2[k][:, i])[0, 1] for i in range(8)])
print("   correlation g1,g2 per question:", np.round(r, 2))
print("   identical answers g1==g2 share:", round((g1[k] == g2[k]).mean(), 3))

s1k = m.loc[k]
print("\nsex:", s1k["sex"].value_counts().to_dict(), " age mean", round(pd.to_numeric(s1k['age'], errors='coerce').mean(), 2),
      "SD", round(pd.to_numeric(s1k['age'], errors='coerce').std(), 2))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5, 3.2))
ax.hist(d, bins=30, color="#4a6fa5")
ax.axvline(0, color="k", lw=1); ax.axvline(d.mean(), color="r", ls="--", lw=1, label=f"mean = {d.mean():.1f}")
ax.set_xlabel("MSE(guess 1) - MSE(average), per participant"); ax.set_ylabel("participants"); ax.legend()
fig.tight_layout(); fig.savefig("papers/S23/report/fig1.png", dpi=150)
print("figure written")

# --- robustness: card's sample definition (keep duplicate-ID rows, as the card's 174 matched implies) ---
print("\n--- robustness: all 174 matched rows incl. duplicate IDs, same exclusions ---")
G1 = m_raw[[q + "_1" for q in Q]].apply(pd.to_numeric, errors="coerce").to_numpy(float)
G2 = m_raw[[q + "_2" for q in Q]].apply(pd.to_numeric, errors="coerce").to_numpy(float)
dfc = (m_raw[[x + "_1" for x in DF] + [x + "_2" for x in DF]].fillna(0).to_numpy() == 1).any(axis=1)
mis = np.isnan(G1).any(axis=1) | np.isnan(G2).any(axis=1)
pk = m_raw["peaking"].astype(str).str.strip() != "Nee"
K = ~(dfc | mis | pk)
print("n after exclusions:", K.sum(), " sex:", m_raw.loc[K, "sex"].value_counts().to_dict())
b1, b2, ba = mses(G1[K], G2[K])
paired(b1, ba, "MSE1 vs MSEavg (card sample)")
