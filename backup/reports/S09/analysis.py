"""S09: Group x Lag mixed ANOVA on T2|T1 accuracy. Run from the S09 run root:
   .venv/bin/python -I papers/S09/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
from scipy.optimize import brentq
import pingouin as pg

df, meta = pyreadstat.read_sav("papers/S09/data/d09.sav")
lags = [1, 3, 5, 8]
cols = [f"Lag{l}_T2_correct" for l in lags]
print("Rows:", len(df))
print("Q1 (n languages fluent) by Group:\n", pd.crosstab(df.Group, df.Q1))
df["grp"] = df.Group.map({1.0: "monolingual", 2.0: "bilingual"})
d = df[["Code", "grp"] + cols].dropna()
print("Complete cases:", len(d), d.grp.value_counts().to_dict())

print("\nCell means (SD) of T2|T1:")
print(d.groupby("grp")[cols].agg(["mean", "std"]).round(3).T)

def ci_partial_eta2(F, df1, df2, conf=0.90):
    """CI for partial eta^2 by inverting the noncentral F."""
    a = (1 - conf) / 2
    def nc(target):
        f = lambda lam: stats.ncf.cdf(F, df1, df2, lam) - target
        if f(0) < 0: return 0.0
        return brentq(f, 0, 1000)
    lo, hi = nc(1 - a), nc(a)
    N = df1 + df2 + 1  # approximation for conversion lambda -> eta2
    conv = lambda lam: lam / (lam + df1 + df2 + 1)
    return conv(lo), conv(hi)

def mixed(d, label):
    long = d.melt(id_vars=["Code", "grp"], value_vars=cols, var_name="lag", value_name="acc")
    long["lag"] = long.lag.str.extract(r"Lag(\d)")[0].astype(int)
    # manual split-plot decomposition
    Y = d[cols].to_numpy(); g = d.grp.to_numpy()
    n, k = Y.shape
    groups = ["monolingual", "bilingual"]
    subj_mean = Y.mean(1, keepdims=True)
    # within-subject residualised scores
    resid_within = Y - subj_mean
    # cell means of within-subject deviations per group
    ss_err = 0.0; ss_lagxg_plus_lag = 0.0
    for gg in groups:
        R = resid_within[g == gg]
        ss_err += ((R - R.mean(0)) ** 2).sum()
    # interaction SS = sum over groups n_j * sum_l (mean_jl - mean_j. - mean_.l(weighted) + grand)
    cell = np.array([Y[g == gg].mean(0) for gg in groups]); nj = np.array([(g == gg).sum() for gg in groups])
    dev = cell - cell.mean(1, keepdims=True)
    wmean_dev = (nj[:, None] * dev).sum(0) / nj.sum()
    ss_int = (nj[:, None] * (dev - wmean_dev) ** 2).sum()
    df_int, df_err = (len(groups) - 1) * (k - 1), (n - len(groups)) * (k - 1)
    F = (ss_int / df_int) / (ss_err / df_err)
    # Greenhouse-Geisser epsilon from pooled within-group covariance
    S = sum(np.cov(Y[g == gg].T) * (nj[i] - 1) for i, gg in enumerate(groups)) / (n - len(groups))
    C = np.eye(k) - 1 / k; Sc = C @ S @ C
    eps = np.trace(Sc) ** 2 / ((k - 1) * np.trace(Sc @ Sc))
    p_unc = stats.f.sf(F, df_int, df_err)
    p_gg = stats.f.sf(F, df_int * eps, df_err * eps)
    pes = ss_int / (ss_int + ss_err)
    lo, hi = ci_partial_eta2(F, df_int * eps, df_err * eps)
    print(f"\n=== {label}: n = {n} ({dict(zip(groups, nj))}) ===")
    print(f"Manual: SS_int={ss_int:.5f} SS_err={ss_err:.5f} F({df_int},{df_err})={F:.3f} p_unc={p_unc:.4f}")
    print(f"GG epsilon={eps:.4f}; GG df=({df_int*eps:.2f}, {df_err*eps:.2f}); p_GG={p_gg:.4f}")
    print(f"partial eta^2 = {pes:.4f}; 90% CI (noncentral F, GG df) = [{lo:.4f}, {hi:.4f}]")
    aov = pg.mixed_anova(data=long, dv="acc", within="lag", between="grp", subject="Code", correction=True)
    print("pingouin mixed_anova (cross-check):"); print(aov.round(4).to_string())
    sph = pg.sphericity(data=long, dv="acc", within="lag", subject="Code")
    print("Mauchly (pingouin, ignoring group):", sph)
    return dict(F=F, df1=df_int, df2=df_err, eps=eps, p_gg=p_gg, pes=pes, lo=lo, hi=hi, n=n)

res = mixed(d, "PRIMARY (all participants, no exclusions)")

# Lag-3 group difference (descriptive check, not the primary test)
m3 = d.loc[d.grp == "monolingual", "Lag3_T2_correct"]; b3 = d.loc[d.grp == "bilingual", "Lag3_T2_correct"]
t = stats.ttest_ind(m3, b3, equal_var=False)
print(f"\nCheck: lag 3 mono {m3.mean():.3f} vs bi {b3.mean():.3f}, Welch t={t.statistic:.3f}, p={t.pvalue:.4f}")
for l, c in zip(lags, cols):
    mm, bb = d.loc[d.grp == "monolingual", c].mean(), d.loc[d.grp == "bilingual", c].mean()
    print(f"  lag {l}: mono - bi = {mm - bb:+.3f}")

# Sensitivity: drop participant with implausible T2|T1 (24145)
mixed(d[d.Code != 24145], "SENSITIVITY (without 24145)")

# Exploratory: drop bilinguals with late L2 (age of second language > 12)
age2 = pd.to_numeric(df.Q16.replace("", np.nan).str.normalize("NFKC").str.extract(r"(\d+)")[0], errors="coerce")
age2b = pd.to_numeric(df.Q17.replace("", np.nan).str.normalize("NFKC").str.extract(r"(\d+)")[0], errors="coerce")
age_en = pd.to_numeric(df.Q15.replace("", np.nan).str.normalize("NFKC").str.extract(r"(\d+)")[0], errors="coerce")
df["late"] = (df.Group == 2) & (age2.fillna(age2b).fillna(0).combine(age_en.fillna(0), max) > 12)
print("\nBilingual ages (Q15 English, Q16/Q17 other):")
print(pd.DataFrame({"Code": df.Code, "Q15": df.Q15, "Q16": df.Q16, "Q17": df.Q17, "late": df.late})[df.Group == 2].to_string())
late_codes = df.loc[df.late, "Code"]
mixed(d[~d.Code.isin(late_codes)], f"EXPLORATORY (without {len(late_codes)} late-L2 bilinguals)")

# Figure
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5, 3.4))
for gg, mk in [("monolingual", "o-"), ("bilingual", "s--")]:
    sub = d[d.grp == gg][cols]
    ax.errorbar(lags, sub.mean(), yerr=sub.sem(), fmt=mk, capsize=3, label=f"{gg} (n={len(sub)})")
ax.set_xlabel("Lag (T2 position after T1)"); ax.set_ylabel("T2|T1 proportion correct"); ax.set_xticks(lags)
ax.legend(); ax.set_ylim(0, 1); fig.tight_layout(); fig.savefig("papers/S09/report/fig_lag.png", dpi=150)
print("\nFigure saved: papers/S09/report/fig_lag.png")
