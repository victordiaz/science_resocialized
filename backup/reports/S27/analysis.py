"""S27: 2 (role) x 2 (message) between-subjects ANOVA on AvgWillingReconcileTime2.
Run from the run directory: .venv/bin/python -I papers/S27/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat
from scipy import stats, optimize
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

df, meta = pyreadstat.read_sav('papers/S27/data/d05.sav')
csv = pd.read_csv('papers/S27/data/d04.csv')
print('rows sav/csv:', len(df), len(csv))
R, M, Y = 'VictimOrPerpV0P1', 'AcceptOrEmpowerA0E1', 'AvgWillingReconcileTime2'
print('missing role/message code:', int(df[[R, M]].isna().any(axis=1).sum()),
      '| missing DV:', int(df[Y].isna().sum()))
d = df.dropna(subset=[R, M, Y]).copy()
print('N after listwise deletion:', len(d), '(dropped', len(df) - len(d), ')')
d['role'] = d[R].map({0: 'victim', 1: 'perpetrator'})
d['msg'] = d[M].map({0: 'acceptance', 1: 'empowerment'})

# check: DV reproduces from its ten items. A search over all 2^10 reversal patterns (see log)
# showed the Time-2 item columns are stored already keyed (reversed items pre-reversed), so no reversal here.
items = ['Angry2', 'FeelingstoAmy2', 'FeelingstoRelationship2', 'Close2', 'LikeRelationshipBe2',
         'RelationshipDamaged2', 'FeelFuture2', 'FutureLike2', 'Reconcile2', 'OweAmends2']
X = d[items].copy()
rec = X.mean(axis=1)
print('DV recomputed as plain mean of the ten stored items: max abs diff = %.4f, r = %.4f'
      % ((rec - d[Y]).abs().max(), np.corrcoef(rec, d[Y])[0, 1]))
a = X.dropna()
k = a.shape[1]; alpha = k / (k - 1) * (1 - a.var(ddof=1).sum() / a.sum(axis=1).var(ddof=1))
print('Cronbach alpha (as recomputed): %.3f, n=%d' % (alpha, len(a)))

print('\nCell descriptives')
desc = d.groupby(['role', 'msg'])[Y].agg(['count', 'mean', 'std'])
desc['se'] = desc['std'] / np.sqrt(desc['count'])
print(desc.round(3))

# PRIMARY: Type III ANOVA with sum-to-zero contrasts
fit = smf.ols(f'{Y} ~ C(role, Sum) * C(msg, Sum)', data=d).fit()
a3 = anova_lm(fit, typ=3)
print('\nType III ANOVA'); print(a3.round(4))
ssr = a3.loc['Residual', 'sum_sq']; dfe = int(a3.loc['Residual', 'df'])
row = a3.loc['C(role, Sum):C(msg, Sum)']
F, p = row['F'], row['PR(>F)']
pes = row['sum_sq'] / (row['sum_sq'] + ssr)

def pes_ci(F, df1, df2, level=0.95):
    # CI for noncentrality by inverting noncentral F; convert to partial eta^2
    lo_t, hi_t = (1 + level) / 2, (1 - level) / 2
    f = lambda nc, t: stats.ncf.cdf(F, df1, df2, nc) - t if nc > 0 else stats.f.cdf(F, df1, df2) - t
    lo = 0.0 if stats.f.cdf(F, df1, df2) < lo_t else optimize.brentq(lambda x: f(x, lo_t), 1e-9, 1000)
    hi = 0.0 if stats.f.cdf(F, df1, df2) < hi_t else optimize.brentq(lambda x: f(x, hi_t), 1e-9, 1000)
    n = df1 + df2 + 1
    return lo / (lo + n), hi / (hi + n)
lo, hi = pes_ci(F, 1, dfe)
print('\nPRIMARY role x message: F(1, %d) = %.3f, p = %.4f, partial eta^2 = %.4f, 95%% CI [%.4f, %.4f]'
      % (dfe, F, p, pes, lo, hi))
# 90% CI as is conventional for eta^2 too
lo90, hi90 = pes_ci(F, 1, dfe, 0.90)
print('  90%% CI for partial eta^2: [%.4f, %.4f]' % (lo90, hi90))
# interaction contrast in raw units (difference of differences)
mm = d.groupby(['role', 'msg'])[Y].mean()
dv = mm['victim', 'empowerment'] - mm['victim', 'acceptance']
dp = mm['perpetrator', 'acceptance'] - mm['perpetrator', 'empowerment']
print('victim: empowerment - acceptance = %.3f ; perpetrator: acceptance - empowerment = %.3f' % (dv, dp))
print('predicted crossover signs (both > 0):', dv > 0 and dp > 0)

print('\nType II ANOVA (check)'); print(anova_lm(smf.ols(f'{Y} ~ C(role) * C(msg)', data=d).fit(), typ=2).round(4))
rob = smf.ols(f'{Y} ~ C(role, Sum) * C(msg, Sum)', data=d).fit(cov_type='HC3')
print('HC3-robust interaction coefficient test:', rob.t_test('C(role, Sum)[S.perpetrator]:C(msg, Sum)[S.acceptance] = 0'))
print('Levene (median):', stats.levene(*[g[Y].values for _, g in d.groupby(['role', 'msg'])]))

print('\nSimple effects of message within role (Welch t; pooled-error t)')
mse = ssr / dfe
for r in ['victim', 'perpetrator']:
    s = d[d.role == r]
    e = s[s.msg == 'empowerment'][Y]; ac = s[s.msg == 'acceptance'][Y]
    t = stats.ttest_ind(e, ac, equal_var=False)
    tp = (e.mean() - ac.mean()) / np.sqrt(mse * (1 / len(e) + 1 / len(ac)))
    pp = 2 * stats.t.sf(abs(tp), dfe)
    sp = np.sqrt(((len(e) - 1) * e.var() + (len(ac) - 1) * ac.var()) / (len(e) + len(ac) - 2))
    mw = stats.mannwhitneyu(e, ac)
    print(f'{r}: emp {e.mean():.3f} (n={len(e)}) vs acc {ac.mean():.3f} (n={len(ac)}); diff={e.mean()-ac.mean():.3f}; '
          f'Welch t({t.df:.1f})={t.statistic:.3f}, p={t.pvalue:.4f}; pooled t({dfe})={tp:.3f}, p={pp:.4f}; '
          f'd={(e.mean()-ac.mean())/sp:.3f}; Mann-Whitney U={mw.statistic:.1f}, p={mw.pvalue:.4f}')

print('\nRobustness: ANCOVA adjusting for before-message willingness (AvgWillingReconcileTime1)')
d2 = d.dropna(subset=['AvgWillingReconcileTime1'])
fa = smf.ols(f'{Y} ~ AvgWillingReconcileTime1 + C(role, Sum) * C(msg, Sum)', data=d2).fit()
print('n =', len(d2)); print(anova_lm(fa, typ=3).round(4))
print('Time-1 cell means:'); print(d2.groupby(['role', 'msg'])['AvgWillingReconcileTime1'].mean().round(3))
d2 = d2.assign(change=d2[Y] - d2['AvgWillingReconcileTime1'])
print('Change (T2-T1) cell means:'); print(d2.groupby(['role', 'msg'])['change'].mean().round(3))
