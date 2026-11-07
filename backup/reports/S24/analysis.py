"""S24: mixed ANOVA, list type (between) x test-word type (within), DV = proportion correct."""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
import pingouin as pg

D = 'papers/S24/data/'
wide, _ = pyreadstat.read_sav(D + 'd03.sav')
wide['subject'] = wide['subject'].astype(int)
types = ['correct', 'intrusion', 'new']
print('N =', len(wide)); print(wide.listtype.value_counts().to_string())

# consistency check against trial file
tr = pd.read_csv(D + 'd05.csv')
rec = tr.groupby(['subject', 'condition']).correct.mean().unstack()[types]
m = wide.set_index('subject')[types]
print('max |wide - recomputed from trials| =', float((m - rec.loc[m.index]).abs().max().max()))

long_ = wide.melt(id_vars=['subject', 'listtype'], value_vars=types, var_name='type', value_name='acc')

print('\nCell means (SD):')
print(long_.groupby(['listtype', 'type']).acc.agg(['mean', 'std', 'count']).round(4).to_string())
pm = wide.assign(pm=wide[types].mean(axis=1)).groupby('listtype').pm.agg(['mean', 'std', 'count'])
print('\nPer-participant mean over the three types, by group:'); print(pm.round(4).to_string())

# Primary: mixed ANOVA (manual split-plot decomposition; equals type III here since within is balanced)
a, b = 2, 3
gm = long_.acc.mean()
subj_mean = long_.groupby('subject').acc.mean()
grp = wide.set_index('subject').listtype
n_g = wide.listtype.value_counts()
gmeans = long_.groupby('listtype').acc.mean()
# Type III for unbalanced between groups: use unweighted means approach via regression check below
SS_A_w = sum(n_g[g] * b * (gmeans[g] - gm) ** 2 for g in gmeans.index)
SS_S_A = b * sum((subj_mean[s] - gmeans[grp[s]]) ** 2 for s in subj_mean.index)
df_A, df_SA = a - 1, len(wide) - a
F_A = (SS_A_w / df_A) / (SS_S_A / df_SA)
p_A = stats.f.sf(F_A, df_A, df_SA)
pes = SS_A_w / (SS_A_w + SS_S_A)
print(f'\nManual (sequential) list-type effect: SS={SS_A_w:.5f}, SS_err={SS_S_A:.5f}, F({df_A},{df_SA})={F_A:.4f}, p={p_A:.4f}, pes={pes:.4f}')

# Type III between-subjects term: on subject means, effect-coded one-way ANOVA = type III for the between term
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
sm_df = wide.assign(pm=wide[types].mean(axis=1))
fit = smf.ols('pm ~ C(listtype, Sum)', data=sm_df).fit()
t3 = anova_lm(fit, typ=3)
SS_A3 = t3.loc['C(listtype, Sum)', 'sum_sq'] * b
SS_E3 = t3.loc['Residual', 'sum_sq'] * b
F3 = t3.loc['C(listtype, Sum)', 'F']; p3 = t3.loc['C(listtype, Sum)', 'PR(>F)']
pes3 = SS_A3 / (SS_A3 + SS_E3)
print(f'Type III list-type effect: SS={SS_A3:.5f}, SS_err={SS_E3:.5f}, F(1,{int(fit.df_resid)})={F3:.4f}, p={p3:.4f}, partial eta^2={pes3:.4f}')

# CI for partial eta^2 by noncentral F inversion
def ncp_ci(F, d1, d2, conf):
    from scipy.optimize import brentq
    alpha = 1 - conf
    def lo_f(nc): return stats.ncf.sf(F, d1, d2, nc) - alpha / 2 if nc > 0 else stats.f.sf(F, d1, d2) - alpha / 2
    def hi_f(nc): return stats.ncf.sf(F, d1, d2, nc) - (1 - alpha / 2) if nc > 0 else stats.f.sf(F, d1, d2) - (1 - alpha / 2)
    lo = 0.0 if lo_f(0) >= 0 else brentq(lo_f, 1e-9, 1000)
    hi = 0.0 if hi_f(0) >= 0 else brentq(hi_f, 1e-9, 1000)
    N = d1 + d2 + 1
    return lo / (lo + N), hi / (hi + N)
for c in (0.90, 0.95):
    l, h = ncp_ci(F3, 1, 19, c)
    print(f'{int(c*100)}% CI partial eta^2: [{l:.4f}, {h:.4f}]')

# Group difference with CI (subject means)
g1 = sm_df[sm_df.listtype == 'long-short'].pm; g2 = sm_df[sm_df.listtype == 'short-long'].pm
t = stats.ttest_ind(g1, g2)
diff = g1.mean() - g2.mean()
se = diff / t.statistic
ci = diff + np.array([-1, 1]) * stats.t.ppf(.975, 19) * se
print(f'Mean difference (long-short minus short-long) = {diff:.4f}, 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]; t(19)={t.statistic:.4f} (t^2={t.statistic**2:.4f})')
print('Hedges g =', round(float(pg.compute_effsize(g1, g2, eftype='hedges')), 4))

print('\nFull mixed ANOVA (pingouin):')
print(pg.mixed_anova(data=long_, dv='acc', within='type', between='listtype', subject='subject', correction=True).round(4).to_string())

# Secondary: new column alone
n1 = wide[wide.listtype == 'long-short'].new; n2 = wide[wide.listtype == 'short-long'].new
tt = stats.ttest_ind(n1, n2); tw = stats.ttest_ind(n1, n2, equal_var=False)
print(f'\nSecondary, new only: long-short M={n1.mean():.4f}, short-long M={n2.mean():.4f}; Student t(19)={tt.statistic:.4f}, p={tt.pvalue:.4f}; Welch t={tw.statistic:.4f}, p={tw.pvalue:.4f}')
mw = stats.mannwhitneyu(n1, n2); print(f'Mann-Whitney U={mw.statistic}, p={mw.pvalue:.4f}')

# Robustness: primary without the visibly low-accuracy participant (106), not the basis of the conclusion
r = sm_df[sm_df.subject != 106]
f2 = anova_lm(smf.ols('pm ~ C(listtype, Sum)', data=r).fit(), typ=3)
print(f"\nRobustness (drop 106, lowest accuracy): F(1,18)={f2.loc['C(listtype, Sum)','F']:.4f}, p={f2.loc['C(listtype, Sum)','PR(>F)']:.4f}")
mwp = stats.mannwhitneyu(g1, g2); print(f'Robustness, Mann-Whitney on subject means: U={mwp.statistic}, p={mwp.pvalue:.4f}')

# figure
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5.5, 3.2))
for i, (g, col) in enumerate([('long-short', 'C0'), ('short-long', 'C1')]):
    sub = long_[long_.listtype == g]
    for j, ty in enumerate(types):
        v = sub[sub.type == ty].acc
        x = j + (i - .5) * .3
        ax.scatter(np.full(len(v), x) + np.random.default_rng(j + 10 * i).uniform(-.05, .05, len(v)), v, s=10, color=col, alpha=.5)
        ax.errorbar(x, v.mean(), yerr=stats.sem(v) * 1.96, fmt='o', color=col, capsize=3, label=g if j == 0 else None)
ax.set_xticks(range(3)); ax.set_xticklabels(types); ax.set_ylabel('Proportion correct'); ax.legend(frameon=False, loc='lower left')
plt.tight_layout(); plt.savefig('papers/S24/report/fig1.png', dpi=150)
print('\nfigure written: papers/S24/report/fig1.png')
