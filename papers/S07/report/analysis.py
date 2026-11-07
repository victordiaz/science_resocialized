"""S07: sunny-minus-cloudy contrast of drug-use correlations (Meng, Rosenthal & Rubin 1992).
Run from the S07 run directory: .venv/bin/python -I papers/S07/report/analysis.py"""
import numpy as np, pandas as pd, os
from scipy import stats
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
C = ['KS', 'KC', 'RS', 'RC']; LAM = np.array([1, -1, 1, -1])

def mrr(df):
    n = len(df)
    r = np.array([stats.pearsonr(df[c], df.polydrug)[0] for c in C])
    z = np.arctanh(r)
    ic = df[C].corr().values[np.triu_indices(4, 1)]
    rx = np.median(ic)
    r2 = np.mean(r ** 2)
    f = min((1 - rx) / (2 * (1 - r2)), 1.0)
    h = (1 - f * r2) / (1 - r2)
    Z = np.sum(LAM * z) * np.sqrt((n - 3) / (np.sum(LAM ** 2) * (1 - rx) * h))
    return dict(n=n, r=r, z=z, ic=ic, rx=rx, f=f, h=h, Z=Z, p=2 * stats.norm.sf(abs(Z)),
                dz=np.sum(LAM * z) / 2)

def show(label, res):
    print(f'--- {label}: N = {res["n"]}')
    for c, r in zip(C, res['r']):
        se = 1 / np.sqrt(res['n'] - 3); z = np.arctanh(r)
        lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
        print(f'  r(polydrug, {c}) = {r:+.4f}  95% CI [{lo:+.3f}, {hi:+.3f}]  p = {2*stats.t.sf(abs(r)*np.sqrt((res["n"]-2)/(1-r*r)), res["n"]-2):.3f}')
    print('  inter-correlations (KS-KC, KS-RS, KS-RC, KC-RS, KC-RC, RS-RC):', np.round(res['ic'], 4))
    print(f'  median r_x = {res["rx"]:.4f}; f = {res["f"]:.4f}; h = {res["h"]:.4f}')
    print(f'  contrast (sunny - cloudy), mean z difference = {res["dz"]:+.4f}')
    print(f'  Z = {res["Z"]:+.3f}, two-sided p = {res["p"]:.4f}')

# ---------- primary: cleaned per-participant file ----------
t6 = pd.read_stata(os.path.join(D, 'd10.dta'), convert_categoricals=False)
print('d10 rows:', len(t6), '| missing polydrug:', t6.polydrug.isna().sum(),
      '| missing any casting score:', t6[C].isna().any(axis=1).sum())
prim = t6.dropna(subset=C + ['polydrug']).reset_index(drop=True)
print('Excluded (no drug-use score or missing casting score):', len(t6) - len(prim))
print(prim[C + ['polydrug']].describe().round(2).to_string())
res = mrr(prim); show('PRIMARY (d10)', res)

# bootstrap CI of the contrast (mean sunny-cloudy difference in Fisher z) and of Z-free r difference
rng = np.random.default_rng(20261107)
bs = []
X = prim[C + ['polydrug']].values
for _ in range(5000):
    s = X[rng.integers(0, len(X), len(X))]
    rr = [np.corrcoef(s[:, i], s[:, 4])[0, 1] for i in range(4)]
    bs.append(np.sum(LAM * np.arctanh(rr)) / 2)
bs = np.array(bs)
print(f'  bootstrap 95% CI of mean z difference (5000 resamples): [{np.percentile(bs,2.5):+.4f}, {np.percentile(bs,97.5):+.4f}]')
r_contrast = res['Z'] / np.sqrt(res['Z'] ** 2 + res['n'] - 3)
print(f'  effect size r_contrast = Z/sqrt(Z^2+N-3) = {r_contrast:+.4f}')

# ---------- check: drug score agrees with d09 ----------
pdg = pd.read_stata(os.path.join(D, 'd09.dta'), convert_categoricals=False)
m = prim.merge(pdg, on='id', suffixes=('', '_d09'))
print('\nd09 match:', len(m), 'ids; polydrug identical:', bool((m.polydrug == m.polydrug_d09).all()))

# ---------- robustness: recompute casting scores from trial file ----------
tr = pd.read_stata(os.path.join(D, 'd08.dta'), convert_categoricals=False,
                   columns=['id', 'start_time', 'practice', 'release_rule', 'weather', 'visit', 'casts', 'bluefish'])
print('\nTrial file rows:', len(tr), '| rows with missing id:', tr.id.isna().sum())
tr = tr.dropna(subset=['id'])
tr = tr.drop_duplicates(subset=['id', 'release_rule', 'weather', 'visit', 'practice', 'casts', 'bluefish'])
print('after dropping duplicate entries:', len(tr))
tr['cond'] = np.where(tr.release_rule == 1, 'K', 'R') + np.where(tr.weather == 1, 'S', 'C')
print('value check: release_rule 1 = Keep, weather 1 = Clear (from labelled read above)')

def scores(t):
    s = t[t.bluefish == 0].groupby(['id', 'cond']).casts.mean().unstack()[C]
    return s.reset_index().merge(prim[['id', 'polydrug']], on='id').dropna()

for lab, sub in [('trial file, all rounds', tr), ('trial file, practice rounds excluded', tr[tr.practice == 2])]:
    s = scores(sub)
    if lab.endswith('all rounds'):
        cmp = s.merge(prim, on='id', suffixes=('', '_d10'))
        print('max |recomputed - d10| per condition:',
              {c: round(float((cmp[c] - cmp[c + '_d10']).abs().max()), 4) for c in C})
    show('ROBUSTNESS ' + lab, mrr(s))

# Spearman version on primary data
sp = mrr(prim[C + ['polydrug']].rank())
show('ROBUSTNESS Spearman (ranks), d10', sp)

# ---------- figure ----------
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 3))
    se = 1 / np.sqrt(res['n'] - 3)
    for i, c in enumerate(C):
        z = res['z'][i]
        ax.errorbar(i, res['r'][i], yerr=[[res['r'][i] - np.tanh(z - 1.96*se)], [np.tanh(z + 1.96*se) - res['r'][i]]],
                    fmt='o', color='tab:orange' if c[1] == 'S' else 'tab:gray', capsize=4)
    ax.axhline(0, lw=.8, color='k'); ax.set_xticks(range(4)); ax.set_xticklabels(['Keep-Sunny', 'Keep-Cloudy', 'Release-Sunny', 'Release-Cloudy'])
    ax.set_ylabel('r with polydrug (95% CI)'); fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig1.png'), dpi=150)
    print('\nfigure written: fig1.png')
except ImportError:
    print('\nmatplotlib not available; no figure')
