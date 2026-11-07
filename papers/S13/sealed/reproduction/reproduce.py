"""Row.122 (node dnaxe): reproduce the replication's key statistic.

Key test as RPP_dnaxe.r defines it, written before running:
  data: Alvarez_Data.dta (OSF d5im2), trial level, 17 subjects x 120 trials.
  rows: centroid trials (one_vs_four != 1, i.e. four dots missing) that are NOT
        target trials (tar_vs_dis != 1): experimental distractor-centroid trials
        (tar_vs_dis == 11) plus all guessing-phase centroid trials (tar_vs_dis NA).
  DV: angle = localization error in degrees of visual angle between the click
      and the true centroid of the four missing dots.
  test: per-subject mean angle, experimental vs guessing (empirical chance),
        paired t-test, two-sided; dz = t / sqrt(n).
  expected (table): t(16) = -9.59, p reported as 1e-04 (a floor), dz = -2.33, N = 17.
Route A uses the .dta's precomputed angle. Route B rebuilds angle from the 17
raw MATLAB txt files following 'merge and analyze.do' (centroid of the
quadrilateral, pixel -> cm -> degrees at 43 cm), written in Python.
"""
import glob, re
import numpy as np, pandas as pd
from scipy import stats

def paired(m):
    w = m.pivot(index="subject", columns="ExGuess", values="angle")
    t, p = stats.ttest_rel(w["experimental"], w["guessing"])
    n = len(w)
    return n, w, t, p, t / np.sqrt(n)

# ---------- Route A: the .dta
dat = pd.read_stata("download/Data/Alvarez_Data.dta", convert_categoricals=False)
print("dta shape:", dat.shape, "subjects:", dat.subject.nunique())
print(pd.crosstab([dat.ExGuess, dat.one_vs_four], dat.tar_vs_dis.fillna(-1)).to_string())
sel = dat[(dat.one_vs_four != 1) & (dat.tar_vs_dis != 1)]
m = sel.groupby(["subject", "ExGuess"]).angle.mean().reset_index()
n, w, t, p, dz = paired(m)
print(f"\nRoute A (.dta): rows used {len(sel)}; n = {n}")
print(w.mean().round(3).to_dict())
print(f"  paired t({n-1}) = {t:.4f}, two-sided p = {p:.3g}, dz = {dz:.4f}")

# ---------- Route B: raw txt -> angle
def centroid4(xs, ys, stata_sentinel=False):
    pts = sorted(zip(xs, ys), key=lambda q: q[0])          # leftmost first (Stata rank by x)
    x1, y1 = pts[0]
    def slope(q):
        with np.errstate(divide="ignore", invalid="ignore"):
            s = (q[1] - y1) / (q[0] - x1)
        return 0.0 if not np.isfinite(s) else s              # Stata: missing -> 0
    if stata_sentinel:   # the do-file gives the leftmost point tanA = -50, so a slope below -50 sorts ahead of it
        P = sorted(pts, key=lambda q: -50.0 if q == pts[0] else slope(q))
    else:
        P = [pts[0]] + sorted(pts[1:], key=slope)            # order by angle from leftmost
    (ax, ay), (bx, by), (cx, cy), (dx, dy) = P
    s123 = 0.5 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
    s341 = 0.5 * (cx*(dy-ay) + dx*(ay-cy) + ax*(cy-dy))
    g123 = ((ax+bx+cx)/3, (ay+by+cy)/3)
    g341 = ((cx+dx+ax)/3, (cy+dy+ay)/3)
    X = (g123[0]*s123 + g341[0]*s341) / (s123 + s341)
    Y = (g123[1]*s123 + g341[1]*s341) / (s123 + s341)
    return X, Y

rows = []
for f in sorted(glob.glob("download/Data/Alvarez_*.txt")):
    sid = int(re.search(r"Alvarez_(\d+)\.txt", f).group(1))
    first = open(f).readline()
    hdr = first.strip().startswith("v1")          # files 1 and 2 carry a v1..v19 header, the rest none
    r = pd.read_csv(f, sep=r"\s+", header=0 if hdr else None)
    r.columns = [f"v{j}" for j in range(1, 20)]
    r["subject"] = sid
    rows.append(r)
raw = pd.concat(rows, ignore_index=True).copy()
print("\nraw txt rows:", len(raw), "subjects:", raw.subject.nunique())
raw["one_vs_four"] = np.where(raw.v2.isin([3, 4]), 4, 1)
raw["tar_vs_dis"] = np.where(raw.v2.isin([1, 3]), 11, 1).astype(float)
raw["ExGuess"] = np.where(raw.v4 == 0, "guessing", "experimental")
raw.loc[raw.ExGuess == "guessing", "tar_vs_dis"] = np.nan
def routeB(sentinel):
    mx, my = raw.v7.astype(float).copy(), raw.v8.astype(float).copy()
    four = raw.one_vs_four == 4
    for i in raw.index[four]:
        xs = raw.loc[i, ["v12", "v14", "v16", "v18"]].astype(float).values
        ys = raw.loc[i, ["v13", "v15", "v17", "v19"]].astype(float).values
        mx[i], my[i] = centroid4(xs, ys, sentinel)
    dxcm = (mx - raw.v9) / (1600 / 34.5)
    dycm = (my - raw.v10) / (900 / 19.5)
    cm = np.sqrt(dxcm**2 + dycm**2)
    raw["angle"] = np.degrees(2 * np.arctan((cm / 2) / 43))
    selB = raw[(raw.one_vs_four != 1) & (raw.tar_vs_dis != 1)]
    mB = selB.groupby(["subject", "ExGuess"]).angle.mean().reset_index()
    n, w, t, p, dz = paired(mB)
    print(f"Route B (raw txt, stata_sentinel={sentinel}): rows used {len(selB)}; n = {n}")
    print(w.mean().round(3).to_dict())
    print(f"  paired t({n-1}) = {t:.4f}, two-sided p = {p:.3g}, dz = {dz:.4f}")
    return raw.copy()

rawS = routeB(True)
angS = rawS["angle"].copy()
raw = routeB(False)
# trial-level agreement with the .dta
k = ["subject", "v1"]
chk = raw.rename(columns={"v1": "trial"})[["subject", "trial", "ExGuess", "angle"]].merge(
    dat[["subject", "trial", "ExGuess", "angle"]], on=["subject", "trial", "ExGuess"], suffixes=("_py", "_dta"))
diff = (chk.angle_py - chk.angle_dta).abs()
print(f"[geometric ordering] trial-level |angle_py - angle_dta|: matched rows {len(chk)}, max {diff.max():.2e}, rows > 1e-3: {(diff>1e-3).sum()}")
chkS = rawS.rename(columns={"v1": "trial"})[["subject","trial","ExGuess","angle"]].merge(dat[["subject","trial","ExGuess","angle"]], on=["subject","trial","ExGuess"], suffixes=("_py","_dta"))
print(f"[stata sentinel ordering] trial-level max |diff| = {(chkS.angle_py-chkS.angle_dta).abs().max():.2e}")
bad = chk[diff > 1e-3].merge(raw.rename(columns={"v1": "trial"}), on=["subject", "trial", "ExGuess"])
print("\ntrials where the rebuilt angle differs from the .dta:")
print(bad[["subject", "trial", "ExGuess", "v2", "angle_py", "angle_dta", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19"]].to_string())
