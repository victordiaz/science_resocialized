"""S16 analysis: F1 repeated-measures ANOVA on per-participant error rates, typical vs atypical."""
import os
import numpy as np, pandas as pd, pyreadstat
from scipy import stats, optimize
import statsmodels.api as sm
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
df, meta = pyreadstat.read_sav(os.path.join(HERE, '..', 'data', 'd02.sav'))
print("rows", len(df), "participants", df.Subj.nunique())
print("value labels", meta.variable_value_labels)

# integrity checks
assert df.resp_corr.notna().all() and df.typisch.notna().all()
agree = (df.Correct.str.strip().map({'True': 1, 'False': 0}) == df.resp_corr).mean()
print("resp_corr agrees with Correct string:", agree)
print("trials per subject x condition:\n", df.groupby(['Subj', 'typisch']).size().unstack().describe().loc[['min', 'max']])
print("crosstab conditio x typisch:\n", pd.crosstab(df.conditio, df.typisch))

df['err'] = 1 - df.resp_corr
er = df.groupby(['Subj', 'typisch']).err.mean().unstack()
er.columns = ['typical', 'atypical']
print("\nper-participant error rates:\n", er.round(4).to_string())
n = len(er)
print("\nmeans:", er.mean().round(4).to_dict(), "SDs:", er.std(ddof=1).round(4).to_dict())
print("total errors: typical", int(df[df.typisch == 1].err.sum()), "atypical", int(df[df.typisch == 2].err.sum()))

# primary: one-way RM ANOVA, 2 levels
Y = er.values
gm = Y.mean()
ss_loc = n * ((Y.mean(0) - gm) ** 2).sum()
ss_subj = 2 * ((Y.mean(1) - gm) ** 2).sum()
ss_tot = ((Y - gm) ** 2).sum()
ss_err = ss_tot - ss_loc - ss_subj
df1, df2 = 1, n - 1
F = (ss_loc / df1) / (ss_err / df2)
p = stats.f.sf(F, df1, df2)
pes = ss_loc / (ss_loc + ss_err)
print(f"\nPRIMARY F1 RM-ANOVA: SS_loc={ss_loc:.6f} SS_err={ss_err:.6f} F({df1},{df2})={F:.3f} p={p:.4f} partial_eta2={pes:.4f}")

# 95% CI for partial eta^2 via noncentral F inversion (lambda -> eta = lambda/(lambda+df1+df2+1))
def ncp_bound(target):
    f = lambda lam: stats.ncf.cdf(F, df1, df2, lam) - target if lam > 0 else stats.f.cdf(F, df1, df2) - target
    if f(0) < 0: return 0.0
    return optimize.brentq(f, 1e-9, 1000)
lo_l, hi_l = ncp_bound(0.975), ncp_bound(0.025)
conv = lambda lam: lam / (lam + df1 + df2 + 1)
print(f"partial eta2 95% CI (noncentral F): [{conv(lo_l):.4f}, {conv(hi_l):.4f}]")

# mean difference with CI (equivalently paired t)
d = er.typical - er.atypical
t, pt = stats.ttest_rel(er.typical, er.atypical)
se = d.std(ddof=1) / np.sqrt(n); tc = stats.t.ppf(.975, n - 1)
print(f"diff typical-atypical = {d.mean():.4f} (95% CI {d.mean()-tc*se:.4f}, {d.mean()+tc*se:.4f}); paired t({n-1})={t:.3f}, p={pt:.4f}, t^2={t**2:.3f}; dz={d.mean()/d.std(ddof=1):.3f}")
print("participants with more errors typical/equal/fewer:", int((d > 0).sum()), int((d == 0).sum()), int((d < 0).sum()))

# cross-check with statsmodels AnovaRM
from statsmodels.stats.anova import AnovaRM
long = er.reset_index().melt(id_vars='Subj', var_name='loc', value_name='err')
print(AnovaRM(long, 'err', 'Subj', within=['loc']).fit())

# robustness
w = stats.wilcoxon(er.typical, er.atypical)
print(f"Wilcoxon signed-rank: W={w.statistic}, p={w.pvalue:.4f}")
df['typ'] = (df.typisch == 1).astype(int)
gee = smf.gee('err ~ typ', groups='Subj', data=df, family=sm.families.Binomial(),
              cov_struct=sm.cov_struct.Exchangeable()).fit()
print(f"GEE logistic (trial level, clustered by subject): b_typical={gee.params['typ']:.3f}, OR={np.exp(gee.params['typ']):.3f}, z={gee.tvalues['typ']:.3f}, p={gee.pvalues['typ']:.4f}")

# figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(3.6, 3.2))
for _, r in er.iterrows():
    ax.plot([0, 1], [r.typical * 100, r.atypical * 100], color='0.75', lw=0.8, marker='o', ms=3)
m = er.mean() * 100; s = er.std(ddof=1) / np.sqrt(n) * 100
ax.errorbar([0, 1], m.values, yerr=s.values, color='k', lw=2, marker='s', capsize=4)
ax.set_xticks([0, 1]); ax.set_xticklabels(['typical', 'atypical']); ax.set_xlim(-.3, 1.3)
ax.set_ylabel('error rate (%)'); ax.set_title('Per-participant error rates (n=22)', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig1.png'), dpi=150)
print("figure saved fig1.png")
