"""Row.116 reproduction: does averaging two guesses from the same person, three weeks apart
(delayed condition), give a lower mean squared error than the first guess alone?

Written from step 1 (RPP_ivfu6.R, the authors' MATLAB postprocessing/confirmatory code), not from
the script's numbers. Data: rawdata_delayed_session1.txt and rawdata_delayed_session2.txt,
merged on student_number_simple (inner join). Exclusions: any defocus of the browser window on any
of the 16 answers (defocus_* columns of both sessions), any missing answer, or peaking != 'Nee'
(admitted looking up answers). DV: per participant, MSE over the 8 questions against the true values;
MSE of guess 1 vs MSE of the per-question average of guess 1 and guess 2. Paired t-test.
The audit script is one-sided (greater); the authors' MATLAB ttest is two-sided; both printed.
d_z = t / sqrt(n).
"""
import os
import numpy as np, pandas as pd
from scipy import stats

here = os.path.dirname(os.path.abspath(__file__))
s1 = pd.read_csv(os.path.join(here, 'download/rawdata_delayed_session1.txt'), sep='\t', na_values=['NaN'])
s2 = pd.read_csv(os.path.join(here, 'download/rawdata_delayed_session2.txt'), sep='\t', na_values=['NaN'])
print('session1 rows/cols', s1.shape, 'session2 rows/cols', s2.shape)
print('duplicate ids s1/s2:', int(s1.student_number_simple.duplicated().sum()), int(s2.student_number_simple.duplicated().sum()))
m = s1.merge(s2, on='student_number_simple', suffixes=('.s1', '.s2'))
print('merged rows', len(m))
q = [f'q{i}' for i in range(1, 9)]
qcols = [f'{c}.s1' for c in q] + [f'{c}.s2' for c in q]
dcols = [c for c in m.columns if c.startswith('defocus')]
print('defocus columns used:', len(dcols))
defocus_total = m[dcols].sum(axis=1)  # NaN counted as 0 by pandas; checked below
miss = m[qcols].isna().sum(axis=1)
keep = (defocus_total == 0) & (miss == 0) & (m.peaking == 'Nee')
print('excluded: defocus>0', int((defocus_total > 0).sum()), '| missing answers', int((miss > 0).sum()),
      '| peaking != Nee', int((m.peaking != 'Nee').sum()), '| NaN in defocus among kept',
      int(m.loc[keep, dcols].isna().any(axis=1).sum()))
x = m[keep].copy()
print('duplicate ids among kept rows:', int(x.student_number_simple.duplicated().sum()), '(duplicate ids in the raw files only produce rows with missing answers, which the missing-answer rule drops)')
n = len(x)
print('n after exclusions', n, '| sex', x.sex.value_counts().to_dict(), '| age mean/sd', round(x.age.mean(), 1), round(x.age.std(), 1))

truth = np.array([6.3, 43.3, 32.3, 13.4, 53.6, 54.8, 26.4, 22.4])
g1 = x[[f'{c}.s1' for c in q]].to_numpy(float)
g2 = x[[f'{c}.s2' for c in q]].to_numpy(float)
mse1 = ((g1 - truth) ** 2).mean(axis=1)
mse2 = ((g2 - truth) ** 2).mean(axis=1)
mseav = (((g1 + g2) / 2 - truth) ** 2).mean(axis=1)
print('mean MSE guess1, guess2, average:', round(mse1.mean(), 2), round(mse2.mean(), 2), round(mseav.mean(), 2))
t, p1 = stats.ttest_rel(mse1, mseav, alternative='greater')
p2 = stats.ttest_rel(mse1, mseav).pvalue
print(f'KEY guess1 vs average: t({n-1}) = {t:.4f}, p(one-sided) = {p1:.3g}, p(two-sided) = {p2:.3g}, d_z = {t/np.sqrt(n):.4f}')
t2, p22 = stats.ttest_rel(mse2, mseav)
print(f'(not the key test) guess2 vs average: t({n-1}) = {t2:.4f}, p(two-sided) = {p22:.3g}')
