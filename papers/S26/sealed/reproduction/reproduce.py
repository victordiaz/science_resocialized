"""Row.145 reproduction: 2 (game: IPD vs IPD-MD) x 2 (communication: none vs within-group)
between-groups ANOVA on the group-level contribution to the between-group pool B; key term =
main effect of game (predicted lower pool-B contribution in IPD-MD).

Written from step 1 (RPP_76qc5.R, the replication report and the team's SPSS syntax), not from the
script's numbers. Data: Halevy_et_al._(2008)_Replication_Data.sav, 120 participants. Unit of analysis
is the 3-person group (Group_Num, 40 groups): mean GivePool_B (tokens out of 10) per group. No exclusions.
Cross-check against the team's aggregated file (Pool_B_Percent, the SPSS UNIANOVA DV, type III SS).
"""
import os
import numpy as np, pandas as pd, pyreadstat
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

here = os.path.dirname(os.path.abspath(__file__))
df, meta = pyreadstat.read_sav(os.path.join(here, 'download/Data/Halevy_et_al._(2008)_Replication_Data.sav'))
print('rows', df.shape[0], 'cols', df.shape[1], '| missing GivePool_B', int(df.GivePool_B.isna().sum()))
print('participants per group:', df.groupby('Group_Num').size().value_counts().to_dict())
g = df.groupby(['Group_Num', 'Condition_Game', 'Condition_Communication'], as_index=False).GivePool_B.mean()
print('groups', len(g), '| groups per cell:', g.groupby(['Condition_Game', 'Condition_Communication']).size().to_dict())
print('mean pool-B tokens by game (1=IPD, 2=IPD-MD):', g.groupby('Condition_Game').GivePool_B.mean().round(3).to_dict())

def fit(data, dv):
    mod = smf.ols(f'{dv} ~ C(Condition_Game, Sum) * C(Condition_Communication, Sum)', data=data).fit()
    tab = anova_lm(mod, typ=3)
    ss_err = tab.loc['Residual', 'sum_sq']
    tab['partial_eta2'] = tab.sum_sq / (tab.sum_sq + ss_err)
    return tab.drop(index='Intercept')

tab = fit(g, 'GivePool_B')
print(tab.to_string())
r = tab.iloc[0]
print(f"KEY game main effect: F({int(r.df)},{int(tab.loc['Residual','df'])}) = {r.F:.4f}, p = {r['PR(>F)']:.3g}, partial eta^2 = {r.partial_eta2:.4f}")

agg, _ = pyreadstat.read_sav(os.path.join(here, 'download/Data/Halevy_et_al._(2008)_Aggregated_Replication_Data.sav'))
print('aggregated file rows', len(agg), '| columns', list(agg.columns))
mrg = g.merge(agg[['Group_Num', 'Pool_B_Percent']], on='Group_Num')
print('max |10*mean tokens - Pool_B_Percent| =', float((mrg.GivePool_B * 10 - mrg.Pool_B_Percent).abs().max()))
tab2 = fit(agg, 'Pool_B_Percent')
r2 = tab2.iloc[0]
print(f"cross-check on Pool_B_Percent (team's SPSS DV): F = {r2.F:.4f}, p = {r2['PR(>F)']:.3g}, partial eta^2 = {r2.partial_eta2:.4f}")
