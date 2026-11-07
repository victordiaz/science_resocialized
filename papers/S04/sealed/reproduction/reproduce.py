"""Row.29 (node ujhlw): independent reproduction of the replication's key test.

Key test (replication report, Analysis Plan + Results; RPP_ujhlw.R): per participant, the
proportion of correct familiarity choices on test trials whose triplet_type is "real"
(16 of 32 test trials; pseudo-triplet trials are discarded); two-sided one-sample t-test of
those 15 proportions against chance (0.5). Effect size d = t / sqrt(n) = (mean - .5) / sd.
No participants excluded.
"""
import glob, os
import numpy as np
import scipy.io as sio
from scipy import stats

D = "data/findings/Row.29/download/Data/unz"
files = sorted(glob.glob(os.path.join(D, "subject*.mat")))
print("subject files:", len(files))
props = []
for f in files:
    m = sio.loadmat(f, squeeze_me=True, struct_as_record=False)
    d = m["data"]
    correct = np.asarray(d.correct, dtype=float)
    ttype = np.array([str(x) for x in np.atleast_1d(d.triplet_type)])
    real = ttype == "real"
    props.append(correct[real].mean())
    print(f"  {os.path.basename(f)}: trials={correct.size}, real={real.sum()}, types={sorted(set(ttype))}, p_correct_real={correct[real].mean():.4f}")
props = np.array(props)
t, p = stats.ttest_1samp(props, 0.5)
n = len(props)
ci = stats.t.interval(0.95, n - 1, loc=props.mean(), scale=stats.sem(props))
print(f"\nn = {n}; mean proportion correct (real triplets) = {props.mean():.4f}, sd = {props.std(ddof=1):.4f}, 95% CI [{ci[0]:.3f}, {ci[1]:.3f}]")
print(f"one-sample t vs 0.5: t({n-1}) = {t:.3f}, p = {p:.4g}, d = t/sqrt(n) = {t/np.sqrt(n):.3f}")
