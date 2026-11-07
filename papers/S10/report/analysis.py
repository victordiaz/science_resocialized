"""S10: object-naming onset congruency. Run from the S10 run directory:
.venv/bin/python -I papers/S10/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
from scipy.optimize import brentq

D = 'papers/S10/data/'
df, _ = pyreadstat.read_sav(D + 'd06.sav')
print('Trials:', len(df), '| subjects:', df.Subject.nunique())
print(df.groupby('NamingTask').Subject.unique().apply(sorted))

def prep(d, sd=3.0, drop_err=True):
    d = d.copy()
    n0 = len(d)
    if drop_err:
        d = d[d.Errors == 0]
    n_err = n0 - len(d)
    if sd is not None:
        g = d.groupby('Subject').RT
        z = (d.RT - g.transform('mean')) / g.transform('std')
        d = d[z.abs() <= sd]
    n_sd = n0 - n_err - len(d)
    return d, n0, n_err, n_sd

def subj_means(d):
    return d.pivot_table(index='Subject', columns='Condition', values='RT', aggfunc='mean')

def dz_ci(t, n, conf=.95):
    df_ = n - 1
    lo = brentq(lambda nc: stats.nct.sf(t, df_, nc) - (1 - conf) / 2, t - 10, t + 10)
    hi = brentq(lambda nc: stats.nct.cdf(t, df_, nc) - (1 - conf) / 2, t - 10, t + 10)
    return lo / np.sqrt(n), hi / np.sqrt(n)

def paired(m, label):
    c, i = m['Congruent'], m['Incongruent']
    n = len(m); diff = c - i
    t, p = stats.ttest_rel(c, i)
    se = diff.std(ddof=1) / np.sqrt(n)
    tc = stats.t.ppf(.975, n - 1)
    dz = t / np.sqrt(n); lo, hi = dz_ci(t, n)
    w = stats.wilcoxon(c, i)
    print(f'\n== {label} ==  n = {n}')
    print(f'  mean congruent {c.mean():.1f} (SD {c.std():.1f}); incongruent {i.mean():.1f} (SD {i.std():.1f})')
    print(f'  diff C-I = {diff.mean():.1f} ms, 95% CI [{diff.mean()-tc*se:.1f}, {diff.mean()+tc*se:.1f}]; '
          f'{(diff<0).sum()}/{n} participants faster when congruent')
    print(f'  t({n-1}) = {t:.3f}, p = {p:.4f} (two-sided); dz = {dz:.3f}, 95% CI [{lo:.3f}, {hi:.3f}]')
    print(f'  Wilcoxon W = {w.statistic:.1f}, p = {w.pvalue:.4f}')
    return dict(n=n, t=t, p=p, dz=dz, lo=lo, hi=hi, diff=diff.mean(), c=c.mean(), i=i.mean())

obj = df[df.NamingTask == 'naming']
col = df[df.NamingTask == 'colour']

# ---- PRIMARY ----
d, n0, ne, ns = prep(obj)
print(f'\nObject naming: {n0} trials, {ne} error trials dropped ({100*ne/n0:.1f}%), '
      f'{ns} trials beyond +/-3 SD dropped ({100*ns/n0:.1f}%), {len(d)} kept')
m = subj_means(d)
print(m.round(1).to_string())
R = paired(m, 'PRIMARY: object naming, paired t-test, F1')

# ---- checks ----
print('\n---- Checks (not primary) ----')
d02, _ = pyreadstat.read_sav(D + 'd02.sav')
g = d02[d02.NamingTask == 'naming'].set_index('Subject')[['congruent_mean', 'incongruent_mean']]
g.columns = ['Congruent', 'Incongruent']
cmp = m.join(g, rsuffix='_given')
print('Max |re-derived - given| mean:',
      round(float(np.nanmax(np.abs(cmp[['Congruent', 'Incongruent']].values - cmp[['Congruent_given', 'Incongruent_given']].values))), 2))
paired(g, 'given d02 means, object naming')
paired(subj_means(prep(obj, sd=None)[0]), 'object naming, errors dropped, no SD trim')
paired(subj_means(prep(obj, sd=2.5)[0]), 'object naming, 2.5 SD trim')
paired(subj_means(prep(col)[0]), 'colour naming (claim predicts no effect)')
# task x congruency interaction as difference-of-differences (Welch)
dc = subj_means(prep(col)[0]); dd_o = m.Congruent - m.Incongruent; dd_c = dc.Congruent - dc.Incongruent
ti = stats.ttest_ind(dd_o, dd_c)
print(f'\nTask x congruency (independent t on C-I differences): t({len(dd_o)+len(dd_c)-2}) = {ti.statistic:.3f}, p = {ti.pvalue:.4f}')

# ---- figure ----
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(4.2, 3.4))
for s, r in m.iterrows():
    ax.plot([0, 1], [r.Congruent, r.Incongruent], color='grey', alpha=.6, marker='o', ms=3)
ax.plot([0, 1], [R['c'], R['i']], color='black', lw=2.5, marker='s', label='mean')
ax.set_xticks([0, 1]); ax.set_xticklabels(['Congruent', 'Incongruent']); ax.set_xlim(-.3, 1.3)
ax.set_ylabel('Mean naming RT (ms)'); ax.set_title('Object naming, per participant (n = 12)', fontsize=9)
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig('papers/S10/report/fig1.png', dpi=150)
print('\nfigure written: papers/S10/report/fig1.png')
