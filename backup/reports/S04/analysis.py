"""S04 analysis: per-participant proportion correct on 'real' triplet trials vs 0.5."""
import glob, os
import numpy as np, scipy.io as sio
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
files = sorted(glob.glob(os.path.join(DATA, 'd*.mat')))
print(f"files: {len(files)}")

rows = []
consist_bad = 0
for f in files:
    d = sio.loadmat(f, squeeze_me=True, struct_as_record=False)['data']
    tt = np.array([str(x) for x in d.triplet_type])
    corr = np.asarray(d.correct, dtype=float)
    resp = np.asarray(d.response, dtype=int)
    order = np.array([str(x) for x in d.order_within_trial])
    # consistency check: correct == (response picks the base interval)
    expect = np.where(order == 'base-foil', resp == 1, resp == 2).astype(float)
    consist_bad += int((expect != corr).sum())
    real = tt == 'real'
    rows.append(dict(file=os.path.basename(f), n_trials=len(tt), n_real=int(real.sum()),
                     p_real=corr[real].mean(), p_pseudo=corr[~real].mean(),
                     k_real=int(corr[real].sum())))
print(f"trials where 'correct' disagrees with response/order coding: {consist_bad}")
print("\nfile   n_trials n_real k_real p_real  p_pseudo")
for r in rows:
    print(f"{r['file']} {r['n_trials']:8d} {r['n_real']:6d} {r['k_real']:6d} {r['p_real']:.4f}  {r['p_pseudo']:.4f}")

p = np.array([r['p_real'] for r in rows]); n = len(p)
print(f"\nN after exclusions: {n} (excluded 0)")
m, sd = p.mean(), p.std(ddof=1); se = sd / np.sqrt(n)
t, pv = stats.ttest_1samp(p, 0.5)
d = t / np.sqrt(n)
ci_m = m + np.array([-1, 1]) * stats.t.ppf(.975, n - 1) * se
# 95% CI for d via noncentral t inversion
from scipy.optimize import brentq
nct = stats.nct
lo_nc = brentq(lambda nc: nct.sf(t, n - 1, nc) - 0.025, t - 10, t + 10)
hi_nc = brentq(lambda nc: nct.cdf(t, n - 1, nc) - 0.025, t - 10, t + 10)
print("\nPRIMARY: two-sided one-sample t-test of per-participant proportion (real trials) vs 0.5")
print(f"mean = {m:.4f}, SD = {sd:.4f}, 95% CI mean [{ci_m[0]:.4f}, {ci_m[1]:.4f}]")
print(f"t({n-1}) = {t:.3f}, p = {pv:.4f}")
print(f"d = t/sqrt(n) = {d:.3f}, 95% CI d [{lo_nc/np.sqrt(n):.3f}, {hi_nc/np.sqrt(n):.3f}]")

print("\nROBUSTNESS (not primary)")
w = stats.wilcoxon(p - 0.5)
print(f"Wilcoxon signed-rank vs 0.5: W = {w.statistic}, p = {w.pvalue:.4f} (ties at 0.5 dropped: {(p==0.5).sum()})")
K = sum(r['k_real'] for r in rows); N = sum(r['n_real'] for r in rows)
b = stats.binomtest(K, N, 0.5)
print(f"Pooled binomial (ignores clustering): {K}/{N} = {K/N:.4f}, p = {b.pvalue:.4f}")
print(f"Participants above / at / below 0.5: {(p>0.5).sum()} / {(p==0.5).sum()} / {(p<0.5).sum()}")
pp = np.array([r['p_pseudo'] for r in rows])
tp, pvp = stats.ttest_1samp(pp, 0.5)
print(f"Pseudo trials (descriptive, discarded by design): mean = {pp.mean():.4f}, t({n-1}) = {tp:.3f}, p = {pvp:.4f}")

# figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(4, 3))
ax.scatter(np.random.default_rng(0).uniform(-.08, .08, n), p, alpha=.7)
ax.errorbar([0.25], [m], yerr=[[m - ci_m[0]], [ci_m[1] - m]], fmt='o', color='k', capsize=4)
ax.axhline(.5, ls='--', color='grey'); ax.set_xlim(-.3, .5); ax.set_xticks([])
ax.set_ylabel('Proportion real triplet chosen'); ax.set_ylim(0, 1)
ax.set_title('Real-triplet trials, N = 15'); fig.tight_layout()
fig.savefig(os.path.join(HERE, 'fig1.png'), dpi=150)
print("figure: fig1.png")
