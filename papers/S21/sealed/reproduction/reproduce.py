"""Row.27 reproduction: 2 (stimulus quality) x 2 (word frequency) repeated-measures ANOVA on the
ex-Gaussian mu parameter per participant and cell; key term = quality x frequency interaction.

Written from step 1 (RPP.ahpik.R and the replication report), without the script's numbers.
Data: YapMu.xlsx, first sheet (Sheet3): 71 rows, columns Highfrequencyclear, Lowfrequencyclear,
Highfrequencydegraded, Lowfrequencydegraded (mu estimates from QMPE; the trial-to-mu step is not
scripted anywhere and is not reproduced here). No exclusions at participant level.
"""
import os
import numpy as np, pandas as pd, openpyxl
from scipy import stats
from statsmodels.stats.anova import AnovaRM

here = os.path.dirname(os.path.abspath(__file__))
wb = openpyxl.load_workbook(os.path.join(here, 'download/Data/YapMu.xlsx'), read_only=True, data_only=True)
print('sheets', wb.sheetnames, '-> using', wb.sheetnames[0])
rows = list(wb[wb.sheetnames[0]].iter_rows(values_only=True))
d = pd.DataFrame(rows[1:], columns=rows[0]).dropna(how='all').astype(float)
print('rows', d.shape[0], 'cols', d.shape[1], list(d.columns), 'NA cells', int(d.isna().sum().sum()))
print('cell means:', d.mean().round(2).to_dict())

cells = {('clear', 'high'): 'Highfrequencyclear', ('clear', 'low'): 'Lowfrequencyclear',
         ('degraded', 'high'): 'Highfrequencydegraded', ('degraded', 'low'): 'Lowfrequencydegraded'}
long = pd.DataFrame([dict(sub=i, quality=q, frequency=f, mu=d.loc[i, c])
                     for i in d.index for (q, f), c in cells.items()])
res = AnovaRM(long, 'mu', 'sub', within=['quality', 'frequency']).fit()
print(res.anova_table)

# Independent check by contrasts: each 1-df within effect is a one-sample t on a contrast, F = t^2,
# partial eta^2 = SS_effect / (SS_effect + SS_error) with SS computed from the contrast scores.
n = len(d)
HC, LC, HD, LD = (d[c].values for c in ['Highfrequencyclear', 'Lowfrequencyclear', 'Highfrequencydegraded', 'Lowfrequencydegraded'])
for name, w in [('quality', (HD + LD - HC - LC) / 2), ('frequency', (LC + LD - HC - HD) / 2),
                ('quality x frequency', (LD - HD) - (LC - HC))]:
    t, p = stats.ttest_1samp(w, 0)
    # contrast with coefficients +-1 on the 4 cells; SS = n*mean(c)^2/4, SS_error = sum((c-mean)^2)/4
    c = w if name == 'quality x frequency' else 2 * w
    ss_eff = n * c.mean() ** 2 / 4
    ss_err = ((c - c.mean()) ** 2).sum() / 4
    print(f'{name}: F(1,{n-1}) = {t**2:.4f}, p = {p:.6f}, SS_eff = {ss_eff:.1f}, SS_err = {ss_err:.1f}, '
          f'partial eta^2 = {ss_eff/(ss_eff+ss_err):.4f}')
print('frequency effect (low - high) clear:', round((LC - HC).mean(), 2), ' degraded:', round((LD - HD).mean(), 2))
