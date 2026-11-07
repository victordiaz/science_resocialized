"""Row.80 reproduction: one-way between-subjects ANOVA of the ambivalence index across the three
mind-set conditions (0 neutral, 1 one-sided focus, 2 two-sided focus).

Written from step 1 (RPP_79dey.R, the replication's SAS syntax and codebook), not from the script's numbers.
Data: reconciling.for.repro.txt (3 summary lines above the header), rows with Include == 1.
The Include flag equals SexOffender == 'No' (checked below): participants with experience of sex
offenders or the offender list are excluded, as in the SAS block 'Excluding Yes to Sex Offender'.
Ambivalence = mean of StrongMixed (-3..3), -NotTorn (-3..3) and Indecisive - 4 (1..7 -> -3..3),
over the items answered (SAS mean() semantics; one included participant lacks Indecisive).
"""
import os
import numpy as np, pandas as pd
from scipy import stats

here = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(here, 'download/reconciling.for.repro.txt'), sep='\t', skiprows=3,
                encoding='latin-1', na_values=['.', ' '])
print('rows', d.shape[0], 'cols', d.shape[1])
d = d.rename(columns={d.columns[20]: 'Include'})
print('Include == (SexOffender == "No") for every row:', bool(((d.Include == 1) == (d.SexOffender == 'No')).all()))
x = d[d.Include == 1].copy()
items = pd.DataFrame({'StrongMixed': x.StrongMixed, 'NotTorn_R': -x.NotTorn, 'Indecisive_RC': x.Indecisive - 4})
print('missing item values among included:', items.isna().sum().to_dict())
x['ambiv'] = items.mean(axis=1, skipna=True)
print('n per condition:', x.Condition.value_counts().sort_index().to_dict())
print('mean ambivalence per condition:', x.groupby('Condition').ambiv.mean().round(4).to_dict())

groups = [g.ambiv.values for _, g in x.groupby('Condition')]
F, p = stats.f_oneway(*groups)
grand = x.ambiv.mean()
ss_b = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
ss_w = sum(((g - g.mean()) ** 2).sum() for g in groups)
k, n = len(groups), len(x)
print(f'one-way ANOVA: F({k-1},{n-k}) = {F:.4f}, p = {p:.4f}, eta^2 = SSb/(SSb+SSw) = {ss_b/(ss_b+ss_w):.4f}, n = {n}')

# sensitivity: drop the participant with the missing item instead of averaging two items
y = x[items.notna().all(axis=1)]
F2, p2 = stats.f_oneway(*[g.ambiv.values for _, g in y.groupby('Condition')])
print(f'sensitivity (complete cases, n={len(y)}): F(2,{len(y)-3}) = {F2:.4f}, p = {p2:.4f}')

# second plausible test (the effect description names one-sided vs two-sided only): Student t, 1 vs 2
t, pt = stats.ttest_ind(x[x.Condition == 1].ambiv, x[x.Condition == 2].ambiv)
print(f'(not the table test) one-sided focus vs two-sided focus, Student t: t({(x.Condition.isin([1,2])).sum()-2}) = {t:.4f}, p(two-sided) = {pt:.4f}')
