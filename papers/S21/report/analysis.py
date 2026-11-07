"""S21: quality x frequency interaction on ex-Gaussian mu (lexical decision, pseudohomophone nonwords).
Run from the S21 run directory: .venv/bin/python -I papers/S21/report/analysis.py"""
import numpy as np, pandas as pd
from scipy import stats, optimize
import warnings; warnings.filterwarnings("ignore")

d = pd.read_csv("papers/S21/data/d07.csv").iloc[:, :8]
print("rows", len(d), "subjects", d.Subject.nunique())
print("ACC values", d["Target.ACC"].unique(), "RT range", d["Target.RT"].min(), d["Target.RT"].max())

# ---- trimming check: per subject, word vs nonword, 2.5 SD of own mean
g = d.groupby(["Subject", "word_NW"])["Target.RT"]
z = (d["Target.RT"] - g.transform("mean")) / g.transform("std")
print("max |z| (per subject x word/nonword) in file:", round(z.abs().max(), 3),
      "| trials beyond 2.5 SD if re-trimmed:", int((z.abs() > 2.5).sum()))

import sys
TRIM = "--no-trim" not in sys.argv
d["absz"] = z.abs()
nw0 = int((d.word_NW == 1).sum())
if TRIM:
    d = d[d.absz <= 2.5]
print("TRIM applied:", TRIM, "| word trials before", nw0, "after", int((d.word_NW == 1).sum()),
      "| nonword trials removed", int(((z.abs() > 2.5) & (d.word_NW == 2)).sum()) if not TRIM else "")
w = d[d.word_NW == 1].copy()
# frequency coding: 100 HF and 100 LF items; ldtfreq 1 has more correct trials -> higher accuracy -> high frequency
cnt = w.groupby("ldtfreq").size(); print("correct word trials by ldtfreq:", cnt.to_dict())
w["freq"] = np.where(w.ldtfreq == cnt.idxmax(), "High", "Low")
w["qual"] = np.where(w.Procedure == "CleanProc", "clear", "degraded")
print("mean RT by ldtfreq (check: HF should be faster):", w.groupby("ldtfreq")["Target.RT"].mean().round(1).to_dict())

def exg_cdf(x, mu, sig, tau):
    return stats.exponnorm.cdf(x, tau / sig, loc=mu, scale=sig)

def start(x):
    m, s = x.mean(), x.std(ddof=1)
    sk = max(stats.skew(x), 0.1)
    tau = s * (sk / 2) ** (1 / 3)
    tau = min(max(tau, 0.1 * s), 0.9 * s)
    sig = np.sqrt(max(s**2 - tau**2, (0.1 * s) ** 2))
    return np.array([m - tau, sig, tau])

PROBS = np.arange(0.1, 1.0, 0.1)
def fit_qmle(x):
    x = np.sort(np.asarray(x, float))
    q = np.quantile(x, PROBS)
    counts = np.diff(np.r_[0, [np.sum(x <= b) for b in q], len(x)])
    def nll(p):
        mu, ls, lt = p; sig, tau = np.exp(ls), np.exp(lt)
        F = np.r_[0, exg_cdf(q, mu, sig, tau), 1]
        pr = np.clip(np.diff(F), 1e-12, None)
        return -np.sum(counts * np.log(pr))
    s0 = start(x); p0 = [s0[0], np.log(s0[1]), np.log(s0[2])]
    r = optimize.minimize(nll, p0, method="Nelder-Mead", options=dict(maxiter=5000, xatol=1e-4, fatol=1e-8))
    return r.x[0], np.exp(r.x[1]), np.exp(r.x[2]), r.success

def fit_ml(x):
    x = np.asarray(x, float); s0 = start(x)
    def nll(p):
        mu, ls, lt = p
        return -np.sum(stats.exponnorm.logpdf(x, np.exp(lt - ls), loc=mu, scale=np.exp(ls)))
    r = optimize.minimize(nll, [s0[0], np.log(s0[1]), np.log(s0[2])], method="Nelder-Mead", options=dict(maxiter=5000))
    return r.x[0], np.exp(r.x[1]), np.exp(r.x[2]), r.success

rows = []
for (s, q, f), x in w.groupby(["Subject", "qual", "freq"])["Target.RT"]:
    mq = fit_qmle(x.values); mm = fit_ml(x.values)
    rows.append(dict(Subject=s, qual=q, freq=f, n=len(x), mean=x.mean(),
                     mu_q=mq[0], sig_q=mq[1], tau_q=mq[2], ok_q=mq[3], mu_ml=mm[0], ok_ml=mm[3]))
P = pd.DataFrame(rows)
print("cells", len(P), "trials per cell: min", P.n.min(), "median", P.n.median(),
      "| QMLE converged", P.ok_q.sum(), "| ML converged", P.ok_ml.sum())

def anova(col, label):
    W = P.pivot_table(index="Subject", columns=["qual", "freq"], values=col)
    W = W.dropna(); n = len(W)
    hc, lc, hd, ld = W[("clear", "High")], W[("clear", "Low")], W[("degraded", "High")], W[("degraded", "Low")]
    print(f"\n=== {label}: n = {n}")
    print("cell means:", {k: round(v, 1) for k, v in {"HF clear": hc.mean(), "LF clear": lc.mean(),
          "HF degraded": hd.mean(), "LF degraded": ld.mean()}.items()})
    out = {}
    for name, c in [("quality (deg - clear)", (hd + ld - hc - lc) / 2), ("frequency (LF - HF)", (lc + ld - hc - hd) / 2),
                    ("interaction (LF-HF)deg - (LF-HF)clear", (ld - hd) - (lc - hc))]:
        t, p = stats.ttest_1samp(c, 0)
        # SS for 2x2 within: effect SS = n * mean(c)^2 * k, error SS = k * sum((c-mean)^2); ratio gives partial eta^2
        F = t**2; pes = F / (F + n - 1)
        se = c.std(ddof=1) / np.sqrt(n); ci = c.mean() + np.array([-1, 1]) * stats.t.ppf(.975, n - 1) * se
        lo, hi = pes_ci(F, 1, n - 1)
        print(f"{name}: contrast = {c.mean():.2f} ms [95% CI {ci[0]:.2f}, {ci[1]:.2f}], F(1,{n-1}) = {F:.3f}, p = {p:.4g}, "
              f"partial eta^2 = {pes:.4f} [95% CI {lo:.4f}, {hi:.4f}]")
        out[name] = dict(c=c.mean(), ci=ci, F=F, p=p, pes=pes, n=n, pes_ci=(lo, hi))
    print(f"frequency effect clear = {(lc-hc).mean():.2f}, degraded = {(ld-hd).mean():.2f}")
    return out

def pes_ci(F, df1, df2, conf=0.95):
    # CI for partial eta^2 by inverting the noncentral F distribution for lambda
    a = (1 - conf) / 2
    def lam_for(pt):
        f = lambda L: stats.ncf.cdf(F, df1, df2, L) - pt if L > 0 else stats.f.cdf(F, df1, df2) - pt
        if stats.f.cdf(F, df1, df2) < pt: return 0.0
        return optimize.brentq(f, 1e-9, 1e4)
    Llo, Lhi = lam_for(1 - a), lam_for(a)
    N = df1 + df2 + 1
    return Llo / (Llo + N), Lhi / (Lhi + N)

prim = anova("mu_q", "PRIMARY: mu by quantile ML (decile bins)")
anova("mu_ml", "Robustness: mu by continuous ML")
anova("mean", "Secondary: mean RT")
# robustness: re-trim at 2.5 SD (second pass) then QMLE
P.to_csv("papers/S21/report/cell_estimates%s.csv" % ("" if TRIM else "_notrim"), index=False)
r = prim["interaction (LF-HF)deg - (LF-HF)clear"]
print(f"\nPRIMARY RESULT: F(1, {r['n']-1}) = {r['F']:.2f}, p = {r['p']:.4g}, partial eta^2 = {r['pes']:.3f}, contrast = {r['c']:.1f} ms")
