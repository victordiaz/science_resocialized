"""S17: snake vs caterpillar target, children vs parents. Primary: type-III 2x2 ANOVA on mean latency.
Run from the S17 run directory: .venv/bin/python -I papers/S17/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats, optimize
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

df, meta = pyreadstat.read_sav('papers/S17/data/d05.sav')
df['stim'] = df['Stim_cond'].map({1: 'snake', 2: 'caterpillar'})
df['age'] = df['parentvschild'].map({1: 'child', 2: 'parent'})
M = [f'M{i}' for i in range(1, 25)]
print('N rows:', len(df))
print(pd.crosstab(df['age'], df['stim']))
print('condition x stim:\n', pd.crosstab(df['condition'], df['stim']))

# check: average equals mean of valid trials
recomputed = df[M].mean(axis=1)
print('max |average - mean(M1..M24)|:', float((df['average'] - recomputed).abs().max()))
print('valid trials per participant: min %d, median %.0f' % (df[M].notna().sum(axis=1).min(), df[M].notna().sum(axis=1).median()))

print('\nCell descriptives (average, ms):')
print(df.groupby(['age', 'stim'])['average'].agg(['count', 'mean', 'std']).round(1))
print('\nMarginal means by stimulus:')
print(df.groupby('stim')['average'].agg(['count', 'mean', 'std']).round(1))

# PRIMARY: type-III ANOVA with sum-to-zero coding
m = smf.ols('average ~ C(stim, Sum) * C(age, Sum)', data=df).fit()
a = anova_lm(m, typ=3)
print('\nType-III ANOVA:\n', a.round(4))
ss_e, df_e = a.loc['Residual', 'sum_sq'], a.loc['Residual', 'df']
row = a.loc['C(stim, Sum)']
F, p = row['F'], row['PR(>F)']
pes = row['sum_sq'] / (row['sum_sq'] + ss_e)

def ncp_ci(F, d1, d2, conf=0.95):
    def lo_f(nc, q): return stats.ncf.cdf(F, d1, d2, nc) - q
    hi_q, lo_q = (1 - conf) / 2, 1 - (1 - conf) / 2
    lo = 0.0 if lo_f(0, lo_q) < 0 else optimize.brentq(lo_f, 0, 1000, args=(lo_q,))
    hi = 0.0 if lo_f(0, hi_q) < 0 else optimize.brentq(lo_f, 0, 1000, args=(hi_q,))
    N = d1 + d2 + 1
    return lo / (lo + N), hi / (hi + N)

lo, hi = ncp_ci(F, 1, df_e)
print(f'\nPRIMARY stimulus main effect: F(1, {int(df_e)}) = {F:.3f}, p = {p:.4f}, partial eta^2 = {pes:.3f}, 95% CI [{lo:.3f}, {hi:.3f}]')
# unweighted marginal means (type-III)
cm = df.groupby(['age', 'stim'])['average'].mean().unstack()
print('Unweighted marginal means: snake %.1f, caterpillar %.1f, diff (snake - cat) %.1f ms' %
      (cm['snake'].mean(), cm['caterpillar'].mean(), cm['snake'].mean() - cm['caterpillar'].mean()))
for t in ['C(age, Sum)', 'C(stim, Sum):C(age, Sum)']:
    r = a.loc[t]
    print(f'{t}: F(1, {int(df_e)}) = {r.F:.3f}, p = {r["PR(>F)"]:.4f}, partial eta^2 = {r.sum_sq/(r.sum_sq+ss_e):.3f}')

# Robustness
print('\nRobustness:')
s, c = df.loc[df.stim == 'snake', 'average'], df.loc[df.stim == 'caterpillar', 'average']
t = stats.ttest_ind(s, c, equal_var=False)
print(f'Welch t overall snake vs caterpillar: t = {t.statistic:.3f}, p = {t.pvalue:.4f}')
for g in ['child', 'parent']:
    d = df[df.age == g]
    t = stats.ttest_ind(d.loc[d.stim == 'snake', 'average'], d.loc[d.stim == 'caterpillar', 'average'], equal_var=False)
    print(f'  {g}: Welch t = {t.statistic:.3f}, p = {t.pvalue:.4f}')
df['logavg'] = np.log(df['average'])
al = anova_lm(smf.ols('logavg ~ C(stim, Sum) * C(age, Sum)', data=df).fit(), typ=3)
print(f"log-latency ANOVA stimulus: F = {al.loc['C(stim, Sum)','F']:.3f}, p = {al.loc['C(stim, Sum)','PR(>F)']:.4f}")
# per-participant median latency (robust to slow trials)
df['med'] = df[M].median(axis=1)
am = anova_lm(smf.ols('med ~ C(stim, Sum) * C(age, Sum)', data=df).fit(), typ=3)
print(f"median-latency ANOVA stimulus: F = {am.loc['C(stim, Sum)','F']:.3f}, p = {am.loc['C(stim, Sum)','PR(>F)']:.4f}")
print('Levene (4 cells):', stats.levene(*[g['average'] for _, g in df.groupby(['age', 'stim'])]))
print('Shapiro residuals:', stats.shapiro(m.resid))

# Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5, 3.4))
for i, g in enumerate(['child', 'parent']):
    for j, st in enumerate(['snake', 'caterpillar']):
        v = df[(df.age == g) & (df.stim == st)]['average'] / 1000
        x = i * 3 + j
        ax.scatter(np.full(len(v), x) + np.random.default_rng(1).uniform(-.12, .12, len(v)), v, s=12, alpha=.6,
                   color=['C3', 'C2'][j])
        ax.errorbar(x, v.mean(), yerr=1.96 * v.std() / np.sqrt(len(v)), fmt='o', color='k', capsize=4)
ax.set_xticks([0, 1, 3, 4]); ax.set_xticklabels(['child\nsnake', 'child\ncaterpillar', 'parent\nsnake', 'parent\ncaterpillar'])
ax.set_ylabel('mean latency (s)'); ax.set_title('Mean latency by target and age (mean, 95% CI)')
fig.tight_layout(); fig.savefig('papers/S17/report/fig1.png', dpi=150)
print('figure saved')

# Sensitivity: 9 rows have a stored `average` that differs from the mean of M1..M24; refit with the recomputed mean
diff = (df['average'] - recomputed).abs() > 0.5
print('\nRows where stored average != mean(M1..M24):', int(diff.sum()), list(df.loc[diff, 'ID']))
df['avg_re'] = recomputed
ar = anova_lm(smf.ols('avg_re ~ C(stim, Sum) * C(age, Sum)', data=df).fit(), typ=3)
r = ar.loc['C(stim, Sum)']
print(f"recomputed-mean ANOVA stimulus: F(1, 44) = {r.F:.3f}, p = {r['PR(>F)']:.4f}, partial eta^2 = {r.sum_sq/(r.sum_sq+ar.loc['Residual','sum_sq']):.3f}")
