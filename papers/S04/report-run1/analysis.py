"""S04 analysis. Run from the S04 run directory: .venv/bin/python -I papers/S04/report/analysis.py"""
import io, zipfile, hashlib
import numpy as np, scipy.io as sio
from scipy import stats

D = 'papers/S04/data/'
z = zipfile.ZipFile(D + 'd02.zip')

def load(b):
    m = sio.loadmat(io.BytesIO(b), squeeze_me=True, struct_as_record=False)
    return m['data']

rows = []
for i in range(1, 16):
    b = z.read(f'subject{i:02d}.mat')
    loose = open(D + f'd{i+3:02d}.mat', 'rb').read()
    same = hashlib.sha256(b).hexdigest() == hashlib.sha256(loose).hexdigest()
    d = load(b)
    tt = np.array([str(x) for x in np.atleast_1d(d.triplet_type)])
    c = np.asarray(d.correct, dtype=float).ravel()
    real = np.char.lower(tt) == 'real'
    assert set(np.unique(c)) <= {0.0, 1.0}
    rows.append(dict(sub=i, n_trials=len(c), n_real=int(real.sum()),
                     p_real=c[real].mean(), p_pseudo=c[~real].mean(),
                     k_real=int(c[real].sum()), loose_identical=same))

print('sub n_trials n_real k_real p_real p_pseudo loose_file_identical')
for r in rows:
    print(f"{r['sub']:3d} {r['n_trials']:8d} {r['n_real']:6d} {r['k_real']:6d} {r['p_real']:.4f} {r['p_pseudo']:.4f} {r['loose_identical']}")

s = np.array([r['p_real'] for r in rows]); n = len(s)
print(f'\nN = {n}; excluded = 0')
print(f'Mean proportion real chosen = {s.mean():.4f}, SD = {s.std(ddof=1):.4f}, median = {np.median(s):.4f}')

# Primary test
t, p = stats.ttest_1samp(s, 0.5)
df = n - 1
se = s.std(ddof=1) / np.sqrt(n)
tc = stats.t.ppf(0.975, df)
print(f'\nPRIMARY: one-sample t-test vs 0.5 (two-sided): t({df}) = {t:.3f}, p = {p:.4f}')
print(f'Mean 95% CI = [{s.mean()-tc*se:.4f}, {s.mean()+tc*se:.4f}]')
dz = t / np.sqrt(n)
# CI for d via noncentral t inversion
from scipy.optimize import brentq
def nct_cdf(nc): return stats.nct.cdf(t, df, nc)
lo = brentq(lambda nc: nct_cdf(nc) - 0.975, -20, 20)
hi = brentq(lambda nc: nct_cdf(nc) - 0.025, -20, 20)
print(f'd = t/sqrt(n) = {dz:.3f}, 95% CI [{lo/np.sqrt(n):.3f}, {hi/np.sqrt(n):.3f}]')

# Robustness
w = stats.wilcoxon(s - 0.5)
print(f'\nRobustness: Wilcoxon signed-rank vs 0.5: W = {w.statistic}, p = {w.pvalue:.4f}')
K = sum(r['k_real'] for r in rows); N = sum(r['n_real'] for r in rows)
bt = stats.binomtest(K, N, 0.5)
print(f'Pooled trials: {K}/{N} = {K/N:.4f}, binomial p = {bt.pvalue:.4f} (ignores clustering)')
print(f'Participants above / at / below 0.5: {(s>0.5).sum()} / {(s==0.5).sum()} / {(s<0.5).sum()}')
ps = np.array([r['p_pseudo'] for r in rows])
tp, pp = stats.ttest_1samp(ps, 0.5)
print(f'Descriptive: pseudo-trial proportion mean = {ps.mean():.4f}, t({n-1}) = {tp:.3f}, p = {pp:.4f}')
s2 = np.delete(s, [2, 4])
t2, p2 = stats.ttest_1samp(s2, 0.5)
print(f'Sensitivity (author script drops subjects 3 and 5 as explicit learners; not our plan): mean = {s2.mean():.4f}, t({len(s2)-1}) = {t2:.3f}, p = {p2:.4f}')

