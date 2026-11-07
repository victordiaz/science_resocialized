"""Row.7 reproduction: one-sided paired t-test, English short vs English long lists.

Written from the key test as defined in RPP_6n3bm.R (step 1), without its intermediate numbers.
DV: per subject, mean over trials of nr_correct/8 (proportion of 8 words recalled in the
correct serial position), separately for list == 'EN' & length == 1 (short words) and
list == 'EN' & length == 2 (long words). Subject = source file (1.txt .. 15.txt).
Test: paired t, H1 short > long (one-sided). d = t / sqrt(n) (Lakens 2013 d_z, as the script).
No exclusions (all 15 files). The audit script rounds the proportions to 3 decimals before
the test; both versions are printed.
"""
import glob, os, sys
import pandas as pd
from scipy import stats
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(here, 'download/unz/*.txt')),
               key=lambda p: int(os.path.basename(p).split('.')[0]))
frames = []
for f in files:
    d = pd.read_csv(f, sep='\t')
    d['subject'] = int(os.path.basename(f).split('.')[0])
    frames.append(d)
data = pd.concat(frames, ignore_index=True)
print('files', len(files), 'rows', data.shape[0], 'cols', data.shape[1] - 1)
print('trials per subject x list x length:')
print(data.groupby(['list', 'length']).size().to_string())

pr = data.assign(p=data.nr_correct / 8).groupby(['subject', 'list', 'length']).p.mean().unstack(['list', 'length'])
short, long_ = pr[('EN', 1)], pr[('EN', 2)]
n = len(pr)
for label, a, b in [('unrounded', short, long_), ('rounded to 3 dp (as the script)', short.round(3), long_.round(3))]:
    t, p = stats.ttest_rel(a, b, alternative='greater')
    print(f'{label}: n={n} mean short={a.mean():.4f} mean long={b.mean():.4f} '
          f't({n-1})={t:.4f} p(one-sided)={p:.4f} p(two-sided)={2*p:.4f} d_z=t/sqrt(n)={t/np.sqrt(n):.4f}')

# The other condition a reader could pick by mistake: Dutch lists
t, p = stats.ttest_rel(pr[('NL', 1)], pr[('NL', 2)], alternative='greater')
print(f'(not the key test) Dutch short vs long: t({n-1})={t:.4f} p(one-sided)={p:.4g}')

# Rounding check: means are multiples of 0.05, so mean/8 often ends in an exact 5 at the
# 4th decimal; round(.,3) then depends on the tie rule. Exact decimal arithmetic:
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
m = data.groupby(['subject', 'list', 'length']).nr_correct.mean().unstack(['list', 'length'])
for rule in (ROUND_HALF_EVEN, ROUND_HALF_UP):
    f = lambda x: float((Decimal(repr(round(x, 2))) / 8).quantize(Decimal('0.001'), rule))
    a, b = m[('EN', 1)].map(f), m[('EN', 2)].map(f)
    t, p = stats.ttest_rel(a, b, alternative='greater')
    print(f'exact decimal rounding {rule}: t({n-1})={t:.4f} p(one-sided)={p:.4f}')
