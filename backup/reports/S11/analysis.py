"""S11: mixed ANOVA, Condition (between) x Discussant (within) on look time.
Run from the S11 run directory: .venv/bin/python -I papers/S11/report/analysis.py
"""
import numpy as np, pandas as pd
from scipy import stats
from scipy.optimize import brentq
import pingouin as pg

df = pd.read_csv("papers/S11/data/d02.txt", sep="\t")
df.columns = [c.strip() for c in df.columns]
print("rows:", len(df), "columns:", list(df.columns))
print("missing values:", int(df.isna().sum().sum()))
df["subject"] = df.groupby("Discussant").cumcount() + 1
# consistency check: each subject has the same Condi in all four blocks
cons = df.groupby("subject")["Condi"].nunique()
print("subjects with inconsistent Condi across blocks:", int((cons > 1).sum()))
df["cond"] = df["Condi"].map({4: "on (can hear)", 2: "off (cannot hear)"})
print("n per condition:", df[df.Discussant == 1]["cond"].value_counts().to_dict())

print("\nCell means (SD) of look time, ms:")
desc = df.groupby(["Discussant", "cond"])["Looktime"].agg(["mean", "std", "count"]).round(1)
print(desc)

# ---- manual mixed ANOVA ----
wide = df.pivot(index="subject", columns="Discussant", values="Looktime")
grp = df[df.Discussant == 1].set_index("subject")["Condi"]
Y = wide.values; g = grp.loc[wide.index].values
n, k = Y.shape; levels = np.unique(g); a = len(levels)
gm = Y.mean()
subj_m = Y.mean(1)
grp_m = {l: Y[g == l].mean() for l in levels}
cell_m = {l: Y[g == l].mean(0) for l in levels}
disc_m = Y.mean(0)
SS_tot = ((Y - gm) ** 2).sum()
SS_A = sum((g == l).sum() * k * (grp_m[l] - gm) ** 2 for l in levels)
SS_S_A = sum(k * ((subj_m[g == l] - grp_m[l]) ** 2).sum() for l in levels)
SS_B = n * ((disc_m - gm) ** 2).sum()
SS_AB = sum((g == l).sum() * ((cell_m[l] - grp_m[l] - disc_m + gm) ** 2).sum() for l in levels)
SS_err = SS_tot - SS_A - SS_S_A - SS_B - SS_AB
df_A, df_SA = a - 1, n - a
df_B, df_AB, df_err = k - 1, (a - 1) * (k - 1), (n - a) * (k - 1)
F_A = (SS_A / df_A) / (SS_S_A / df_SA)
F_B = (SS_B / df_B) / (SS_err / df_err)
F_AB = (SS_AB / df_AB) / (SS_err / df_err)

# Greenhouse-Geisser epsilon from the pooled within-group covariance matrix
S = sum(np.cov(Y[g == l].T, ddof=1) * ((g == l).sum() - 1) for l in levels) / (n - a)
C = np.eye(k) - 1.0 / k  # centering
# orthonormal contrasts
Q, _ = np.linalg.qr(np.column_stack([np.ones(k), np.eye(k)[:, :k-1]]))
M = Q[:, 1:]
V = M.T @ S @ M
eps_gg = np.trace(V) ** 2 / ((k - 1) * np.trace(V @ V))
# Mauchly
p_ = k - 1
W = np.linalg.det(V) / (np.trace(V) / p_) ** p_
dfr = n - a
f = 1 - (2 * p_**2 + p_ + 2) / (6 * p_ * dfr)
chi = -dfr * f * np.log(W); dfm = p_ * (p_ + 1) / 2 - 1
print(f"\nMauchly W = {W:.4f}, chi2({dfm:.0f}) = {chi:.2f}, p = {stats.chi2.sf(chi, dfm):.3g}; GG epsilon = {eps_gg:.4f}")

def row(name, SS, d1, d2, F, eps=1.0):
    p = stats.f.sf(F, d1 * eps, d2 * eps)
    print(f"{name:22s} SS={SS:14.1f} df=({d1*eps:.3f}, {d2*eps:.3f}) F={F:8.3f} p={p:.4g}")
    return p
print("\nMixed ANOVA (uncorrected):")
row("Condition", SS_A, df_A, df_SA, F_A)
row("Discussant", SS_B, df_B, df_err, F_B)
row("Condition x Discussant", SS_AB, df_AB, df_err, F_AB)
print("Within-subject effects, Greenhouse-Geisser corrected:")
row("Discussant (GG)", SS_B, df_B, df_err, F_B, eps_gg)
p_int = row("Cond x Disc (GG)", SS_AB, df_AB, df_err, F_AB, eps_gg)
pes = SS_AB / (SS_AB + SS_err)
print(f"\nPRIMARY: Condition x Discussant F({df_AB*eps_gg:.2f}, {df_err*eps_gg:.2f}) = {F_AB:.3f}, "
      f"p(GG) = {p_int:.4f}, partial eta^2 = {pes:.4f}")

# 90% CI for partial eta^2 via noncentral F (uncorrected df and GG df)
def pes_ci(F, d1, d2, conf=0.90):
    lo_q, hi_q = (1 + conf) / 2, (1 - conf) / 2
    def ncp_for(q):
        fn = lambda nc: stats.ncf.cdf(F, d1, d2, nc) - q
        if fn(0) < q: return 0.0
        return brentq(fn, 0, 1000)
    l, u = ncp_for(lo_q), ncp_for(hi_q)
    N = d1 + d2 + 1
    return l / (l + N), u / (u + N)
lo, hi = pes_ci(F_AB, df_AB, df_err)
lo2, hi2 = pes_ci(F_AB, df_AB * eps_gg, df_err * eps_gg)
print(f"90% CI partial eta^2 (uncorrected df): [{lo:.4f}, {hi:.4f}]; (GG df): [{lo2:.4f}, {hi2:.4f}]")

# cross-check with pingouin
print("\npingouin mixed_anova cross-check:")
aov = pg.mixed_anova(data=df, dv="Looktime", within="Discussant", between="cond",
                     subject="subject", correction=True)
with pd.option_context("display.width", 200, "display.max_columns", 20):
    print(aov.round(4))

# secondary: condition simple effects per discussant (Welch t, on - off)
print("\nSecondary: condition difference (on - off) by discussant, Welch t-test:")
for d in range(1, 5):
    on = wide.loc[grp[grp == 4].index, d]; off = wide.loc[grp[grp == 2].index, d]
    t, p = stats.ttest_ind(on, off, equal_var=False)
    u, pu = stats.mannwhitneyu(on, off, alternative="two-sided")
    print(f"  D{d}: on M={on.mean():8.1f}  off M={off.mean():8.1f}  diff={on.mean()-off.mean():8.1f}  t={t:6.3f} p={p:.4f}  MWU p={pu:.4f}")

# robustness: interaction on discussants 1,3,4 only (excluding the speaker, whose region dominates)
print("\nRobustness: ANOVA excluding discussant 2 (the speaker):")
aov2 = pg.mixed_anova(data=df[df.Discussant != 2], dv="Looktime", within="Discussant",
                      between="cond", subject="subject", correction=True)
with pd.option_context("display.width", 200, "display.max_columns", 20):
    print(aov2.round(4))
# robustness: log(1+ms)
df["logLT"] = np.log1p(df["Looktime"])
print("\nRobustness: ANOVA on log(1 + look time):")
aov3 = pg.mixed_anova(data=df, dv="logLT", within="Discussant", between="cond",
                      subject="subject", correction=True)
with pd.option_context("display.width", 200, "display.max_columns", 20):
    print(aov3.round(4))

# figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6, 3.2))
x = np.arange(1, 5); w = 0.35
for i, (l, lab) in enumerate([(4, "Headphones on (can hear)"), (2, "Headphones off")]):
    m = cell_m[l]; se = Y[g == l].std(0, ddof=1) / np.sqrt((g == l).sum())
    ax.bar(x + (i - 0.5) * w, m, w, yerr=se, label=lab, capsize=3)
ax.set_xticks(x); ax.set_xticklabels(["D1 (White)", "D2 (speaker)", "D3 (Black)", "D4 (White)"])
ax.set_ylabel("Look time (ms), mean ± SE"); ax.set_yscale("symlog", linthresh=1000)
ax.legend(fontsize=8); fig.tight_layout()
fig.savefig("papers/S11/report/fig1.png", dpi=150)
print("\nfigure written: papers/S11/report/fig1.png")
