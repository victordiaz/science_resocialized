"""S29: Pearson correlation ERN vs EPS, one-tailed (negative). Run from the run root:
.venv/bin/python -I papers/S29/report/analysis.py"""
import io, os
import numpy as np, pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data", "d05.csv")
raw = open(DATA, "rb").read().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
df = pd.read_csv(io.StringIO(raw))
print("rows", len(df), "cols", list(df.columns))
print(df.startle_type.value_counts().to_dict())
print("unique participants", df.participant.nunique())
chk = df.groupby("participant")[["ERN", "EPS"]].nunique()
print("ERN/EPS constant within participant:", bool((chk == 1).all().all()))

d = df[df.startle_type == "error"][["participant", "ERN", "EPS"]].copy()
d["ERN"] = pd.to_numeric(d.ERN, errors="coerce"); d["EPS"] = pd.to_numeric(d.EPS, errors="coerce")
print("error rows", len(d), "missing ERN/EPS", int(d[["ERN","EPS"]].isna().any(axis=1).sum()))
d = d.dropna()
n = len(d)
print("\nDescriptives (n=%d)" % n)
print(d[["ERN", "EPS"]].describe().round(3))

x, y = d.ERN.values, d.EPS.values
r, p2 = stats.pearsonr(x, y)
t = r * np.sqrt((n - 2) / (1 - r**2))
p1 = stats.t.cdf(t, n - 2)  # H1: rho < 0
z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
up1 = np.tanh(z + 1.645 * se)
print("\nPRIMARY: Pearson r = %.4f, t(%d) = %.3f, one-tailed p (rho<0) = %.4f, two-tailed p = %.4f" % (r, n-2, t, p1, p2))
print("95%% CI for r (Fisher z): [%.3f, %.3f]; one-sided 95%% upper bound: %.3f" % (lo, hi, up1))

print("\nROBUSTNESS")
rs, ps = stats.spearmanr(x, y)
print("Spearman rho = %.4f, two-tailed p = %.4f, one-tailed (neg) p = %.4f" % (rs, ps, ps/2 if rs < 0 else 1 - ps/2))
zs = d[["ERN", "EPS"]].apply(stats.zscore)
keep = (zs.abs() <= 3).all(axis=1)
print("outliers |z|>3:", d[~keep].to_dict("records"))
r2, p22 = stats.pearsonr(x[keep], y[keep]); n2 = int(keep.sum())
print("Pearson without outliers: n = %d, r = %.4f, two-tailed p = %.4f, one-tailed (neg) p = %.4f" % (n2, r2, p22, p22/2 if r2 < 0 else 1 - p22/2))

# figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(4.5, 3.4))
ax.scatter(x, y, s=18, color="#2b6cb0")
b, a = np.polyfit(x, y, 1)
xs = np.linspace(x.min(), x.max(), 50); ax.plot(xs, a + b * xs, color="#c53030")
ax.set_xlabel("ERN (error − correct, µV)"); ax.set_ylabel("EPS (error − correct startle, µV)")
ax.set_title("r = %.2f, n = %d" % (r, n), fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "fig1.png"), dpi=150)
print("figure written fig1.png")
