"""S19: distance effect on 'different' RTs in the numerical-value task.
Run from the run directory:  .venv/bin/python -I papers/S19/report/analysis.py
"""
import os, subprocess, tempfile
import numpy as np, pandas as pd
from scipy import stats
from scipy.optimize import brentq
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
d = pd.read_csv(os.path.join(DATA, 'd06.csv'))
order = pd.read_csv(os.path.join(DATA, 'd07.csv'))
print('Trials loaded:', len(d), 'participants:', d.participant.nunique())

# ---- exclusions (card) ----
steps = []
n0 = len(d)
d = d[d.participant != 24]; steps.append(('drop participant 24', n0 - len(d))); n0 = len(d)
d = d[d.Distraction != 1]; steps.append(('drop fillers (Distraction==1)', n0 - len(d))); n0 = len(d)
d = d[d.Distance != 0]; steps.append(('drop same-value pairs (Distance==0)', n0 - len(d))); n0 = len(d)
d = d[d.correct == 1]; steps.append(('drop error trials (correct==0)', n0 - len(d))); n0 = len(d)
d = d[(d.RT >= 200) & (d.RT <= 2500)]; steps.append(('drop RT <200 or >2500 ms', n0 - len(d))); n0 = len(d)
for s, k in steps: print(f'  {s}: -{k}')
print('Trials kept:', len(d))
print('filter_$==1 among kept:', int((d['filter_$'] == 1).sum()), '; filter_$==1 in full file excl. P24:',
      int(((pd.read_csv(os.path.join(DATA, 'd06.csv'))['filter_$'] == 1) &
           (pd.read_csv(os.path.join(DATA, 'd06.csv')).participant != 24)).sum()))

# ---- cell means ----
cm = d.groupby(['participant', 'Notation', 'Distance']).RT.mean().reset_index()
cm = cm.merge(order, on='participant')
print('Participants in analysis:', cm.participant.nunique(), ' cells per participant:',
      cm.groupby('participant').size().unique(), ' order n:',
      cm.drop_duplicates('participant').Order.value_counts().to_dict())
print('Trials per cell: min', d.groupby(['participant', 'Notation', 'Distance']).size().min())
print('\nCell means (ms) [Notation 1=Arabic 2=Indian 3=mixed; Distance 1=small 2=large]:')
print(cm.groupby(['Notation', 'Distance']).RT.agg(['mean', 'std']).round(1))
print(cm.groupby('Distance').RT.mean().round(1))

# cross-check against provided aggregated cell-mean file d36.csv (d33.csv does not match: it appears to be the other task)
agg = pd.read_csv(os.path.join(DATA, 'd36.csv'))
mm = cm.merge(agg, left_on=['participant', 'Notation', 'Distance'], right_on=['participant', 'Notation', 'Distance'])
print('\nd36.csv cross-check: rows matched', len(mm), ' max |diff|', round((mm.RT - mm.RT_mean).abs().max(), 6))

# ---- primary test: main effect of distance in 3x2x2 mixed ANOVA, type III ----
w = cm.pivot_table(index=['participant', 'Order'], columns=['Notation', 'Distance'], values='RT')
D = (w.xs(2, level='Distance', axis=1) - w.xs(1, level='Distance', axis=1)).mean(axis=1)  # large - small, avg over notation
dd = D.reset_index(); dd.columns = ['participant', 'Order', 'D']
fit = smf.ols('D ~ C(Order, Sum)', data=dd).fit()
t_int = fit.tvalues['Intercept']; F = t_int ** 2; df_err = int(fit.df_resid)
p = fit.pvalues['Intercept']
mse = 1.5 * fit.ssr / df_err          # MSE of distance x subject(order) stratum, ANOVA scale
ss_eff = F * mse
pes = ss_eff / (ss_eff + mse * df_err)
est = fit.params['Intercept']; ci = fit.conf_int().loc['Intercept'].values
print(f'\nPRIMARY: main effect of numerical difference: F(1, {df_err}) = {F:.3f}, MSE = {mse:.1f}, p = {p:.3g}, '
      f'partial eta^2 = {pes:.3f}')
print(f'  large - small (unweighted over order, avg over notation) = {est:.1f} ms, 95% CI [{ci[0]:.1f}, {ci[1]:.1f}]')

def ncp_ci(F, df1, df2, conf=0.90):
    lo_q, hi_q = (1 + conf) / 2, (1 - conf) / 2
    f = lambda nc, q: stats.ncf.cdf(F, df1, df2, nc) - q
    lo = 0.0 if f(0, lo_q) < 0 else brentq(f, 0, 1e4, args=(lo_q,))
    hi = 0.0 if f(0, hi_q) < 0 else brentq(f, 0, 1e4, args=(hi_q,))
    N = df1 + df2 + 1
    return lo / (lo + N), hi / (hi + N)
lo, hi = ncp_ci(F, 1, df_err)
print(f'  90% CI partial eta^2: [{lo:.3f}, {hi:.3f}]')
dz = D.mean() / D.std(ddof=1)
print(f'  paired dz (large-small, all 31, pooled over order) = {dz:.3f}; mean = {D.mean():.1f} ms')
print('  participants with large < small:', int((D < 0).sum()), 'of', len(D))

# ---- full ANOVA cross-check in R (aov with error strata, sum contrasts) ----
rs = '/opt/homebrew/bin/Rscript'
with tempfile.TemporaryDirectory() as td:
    csv = os.path.join(td, 'cm.csv'); cm.to_csv(csv, index=False)
    rcode = f'''
options(contrasts=c("contr.sum","contr.poly"))
x <- read.csv("{csv}"); x$participant<-factor(x$participant); x$Notation<-factor(x$Notation)
x$Distance<-factor(x$Distance); x$Order<-factor(x$Order)
print(summary(aov(RT ~ Notation*Distance*Order + Error(participant/(Notation*Distance)), data=x)))
'''
    rf = os.path.join(td, 'a.R'); open(rf, 'w').write(rcode)
    print('\nR aov (full 3x2x2 mixed ANOVA, sequential SS within strata; check of the distance row):')
    print(subprocess.run([rs, rf], capture_output=True, text=True).stdout)

# ---- robustness: within each notation ----
print('Robustness: large - small within each notation (paired t over 31):')
for n, lab in [(1, 'Arabic'), (2, 'Indian'), (3, 'mixed')]:
    a = w[(n, 2)] - w[(n, 1)]
    t, pp = stats.ttest_1samp(a, 0)
    print(f'  {lab}: mean {a.mean():.1f} ms, t(30) = {t:.2f}, p = {pp:.3g}')
