"""Row.132 (node b98zw): 2 (Condi: headphones off = 2, headphones on = 4; between) x 4 (Discussant 1-4;
within) mixed ANOVA on look time (ms) during the second discussant's potentially offensive comment,
Amsterdam sample; key = Condi x Discussant interaction, Greenhouse-Geisser corrected.
The data file has no subject column: rows are 4 blocks of 30 (Discussant 1..4); subject = position within
block (the Condi sequence is identical across the 4 blocks, which this script checks).
Run: .venv/bin/python -I reproduce.py"""
import os, numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, "download", "Data", "Amsterdam_data.txt"), sep=r"\s+")
print("raw shape", d.shape, "| columns", list(d.columns))
assert (d.Discussant.to_numpy() == np.repeat([1, 2, 3, 4], 30)).all(), "rows not in 4 blocks of 30"
d["Subject"] = np.tile(np.arange(1, 31), 4)
cond_by_block = d.pivot(index="Subject", columns="Discussant", values="Condi")
assert (cond_by_block.nunique(axis=1) == 1).all(), "Condi differs across blocks for a subject"
print("Condi constant within inferred subject across all 4 blocks: yes")
W = d.pivot(index="Subject", columns="Discussant", values="Looktime")
g = cond_by_block[1].to_numpy()
Y = W.to_numpy(float); n, k = Y.shape
groups = np.unique(g); a = len(groups); ng = np.array([(g == x).sum() for x in groups])
print("n subjects", n, "| per Condi", dict(zip(groups.tolist(), ng.tolist())))

grand = Y.mean(); lag_mean = Y.mean(0)
cell = np.array([Y[g == x].mean(0) for x in groups]); gmean = np.array([Y[g == x].mean() for x in groups])
SS_int = sum(ng[i] * ((cell[i] - gmean[i] - lag_mean + grand) ** 2).sum() for i in range(a))
resid = np.vstack([Y[g == x] - Y[g == x].mean(1, keepdims=True) - cell[i] + gmean[i] for i, x in enumerate(groups)])
SS_err = (resid ** 2).sum()
df1, df2 = (a - 1) * (k - 1), (n - a) * (k - 1)
F = (SS_int / df1) / (SS_err / df2)
S = sum(np.cov(Y[g == x].T, ddof=1) * (ng[i] - 1) for i, x in enumerate(groups)) / (n - a)  # pooled within-group
C = np.linalg.qr(np.column_stack([np.ones(k), np.eye(k)[:, :k - 1]]))[0][:, 1:]
M = C.T @ S @ C
eps = np.trace(M) ** 2 / ((k - 1) * np.trace(M @ M))
print("\n=== KEY TEST: Condi x Discussant interaction ===")
print(f"F({df1},{df2}) = {F:.4f}; p_uncorrected = {stats.f.sf(F, df1, df2):.4f}")
print(f"GG epsilon = {eps:.4f}; GG df = ({df1*eps:.3f}, {df2*eps:.3f}); p_GG = {stats.f.sf(F, df1*eps, df2*eps):.4f}")
print(f"partial eta^2 = {SS_int/(SS_int+SS_err):.4f}")
print("cell means (rows Condi", groups.tolist(), "; cols Discussant 1-4):\n", np.round(cell, 1))
try:
    import pingouin as pg
    print("\npingouin mixed_anova:\n", pg.mixed_anova(data=d, dv="Looktime", within="Discussant", between="Condi",
                                                       subject="Subject", correction=True).to_string())
except Exception as e:
    print("pingouin cross-check failed:", e)
# the contrast the hypothesis is about: look time at discussant 3 (the Black man), on vs off
t = stats.ttest_ind(W.loc[g == 4, 3], W.loc[g == 2, 3])
print(f"\n(secondary, not the table's test) discussant 3, headphones on vs off: t({n-2}) = {t.statistic:.3f}, p = {t.pvalue:.4f}")
