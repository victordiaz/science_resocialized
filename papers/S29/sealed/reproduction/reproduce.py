"""Row.120 (node 73pnd): Pearson correlation between ERN amplitude and error-potentiated startle (EPS)
across participants. The file is long (one row per participant x startle_type), with ERN and EPS repeated
on each of a participant's rows, so one row per participant is kept (startle_type == 'error').
Reports two-sided p (what cor.test gives) and one-sided p in the predicted (negative) direction."""
import os, io, numpy as np, pandas as pd
from scipy import stats
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "download", "Data", "rp.csv"), newline=None) as f:  # CR-only line endings
    df = pd.read_csv(io.StringIO(f.read()))
print("raw shape", df.shape, "| startle_type counts", df.startle_type.value_counts().to_dict())
print("participants:", df.participant.nunique(), "| missing ids in 1..51:", sorted(set(range(1, 52)) - set(df.participant)))
# check ERN/EPS are constant within participant
const = df.groupby("participant")[["ERN", "EPS"]].nunique().max()
print("max distinct ERN/EPS values within a participant:", const.to_dict())
p1 = df.groupby("participant")[["ERN", "EPS"]].first()
print("n for correlation:", len(p1), "| any NaN:", int(p1.isna().sum().sum()))
r, p2 = stats.pearsonr(p1.ERN, p1.EPS)
n = len(p1); t = r * np.sqrt((n - 2) / (1 - r ** 2))
p_one = stats.t.cdf(t, n - 2)  # predicted direction: negative
print(f"KEY r = {r:.4f}, t({n-2}) = {t:.4f}, p two-sided = {p2:.4f}, p one-sided (r<0) = {p_one:.4f}")
e = df[df.startle_type == "error"]
r2, pp = stats.pearsonr(e.ERN, e.EPS)
print(f"same on startle_type=='error' rows directly: n={len(e)}, r={r2:.4f}, p={pp:.4f}")
# what N=43 would imply for the same r
for N in (43,):
    tt = r * np.sqrt((N - 2) / (1 - r ** 2)); print(f"if N were {N}: t({N-2})={tt:.3f}, p2={2*stats.t.sf(abs(tt),N-2):.4f}")
