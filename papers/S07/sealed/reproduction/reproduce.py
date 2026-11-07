"""Row.39 (node 38ges): reproduce the replication's key statistic.

Key test as RPP_38ges.R defines it, written before running:
  data: table6data.dta inside data_cleaned.zip (OSF 7xzkb): id, KS, KC, RS, RC
        (adjusted ART score = mean casts on rounds the participant stopped
        fishing, per condition Keep/Release x Sunny/Cloudy), polydrug.
  exclusion: drop rows with missing polydrug.
  test: Meng, Rosenthal & Rubin (1992) contrast of correlated correlations:
        r_i = cor(polydrug, ART_i), i in KS, KC, RS, RC; Fisher z;
        lambda = (+1, -1, +1, -1) i.e. sunny minus cloudy;
        r_x = median inter-correlation of the four ART scores;
        f = (1 - r_x) / (2 (1 - mean r^2)) (capped at 1), h = (1 - f mean r^2)/(1 - mean r^2);
        Z = sum(lambda z) * sqrt((N - 3) / (sum lambda^2 (1 - r_x) h)), two-sided p.
  expected (table): z = 1.25, p = 0.21, N = 153.
Written independently from the formula in the 1992 paper, plus a second route
that rebuilds KS..RC and polydrug from the trial-level fishingData.dta and
DrugData.dta following clean_data.do.
"""
import numpy as np, pandas as pd
from scipy import stats

D = "download/unz/"

def mrr(df, cols=("KS", "KC", "RS", "RC"), lam=(1, -1, 1, -1)):
    lam = np.array(lam, float)
    N = len(df)
    r = np.array([stats.pearsonr(df["polydrug"], df[c])[0] for c in cols])
    z = np.arctanh(r)
    R = df[list(cols)].corr().values
    rx = np.median(R[np.triu_indices(4, 1)])
    r2 = np.mean(r ** 2)
    f = min(1.0, (1 - rx) / (2 * (1 - r2)))
    h = (1 - f * r2) / (1 - r2)
    Z = (lam @ z) * np.sqrt((N - 3) / ((lam @ lam) * (1 - rx) * h))
    p = 2 * stats.norm.sf(abs(Z))
    return N, r, rx, Z, p

t6 = pd.read_stata(D + "table6data.dta", convert_categoricals=False)
print("table6data raw shape:", t6.shape, list(t6.columns))
print("missing polydrug:", int(t6.polydrug.isna().sum()))
a = t6.dropna(subset=["polydrug"])
N, r, rx, Z, p = mrr(a)
print(f"\nRoute A (table6data): N={N}  r(polydrug, KS,KC,RS,RC)={np.round(r,4)}  median r_x={rx:.4f}")
print(f"  MRR contrast sunny-cloudy: Z = {Z:.4f}, two-sided p = {p:.4f}")

# Route B: rebuild from trial-level data, as clean_data.do does
fish = pd.read_stata(D + "fishingData.dta", convert_categoricals=False,
                     columns=["id", "practice", "release_rule", "weather", "casts", "bluefish"])
print("\nfishingData rows:", len(fish), "subjects:", fish.id.nunique())
def build(f):
    g = f[f.bluefish == 0].groupby(["id", "release_rule", "weather"]).casts.mean().unstack([1, 2])
    g.columns = [{(1, 1): "KS", (1, 2): "KC", (2, 1): "RS", (2, 2): "RC"}[c] for c in g.columns]
    return g
poly = pd.read_stata(D + "polydrug.dta", convert_categoricals=False)[["id", "polydrug"]]
for label, f in [("do-file as written (practice rounds included)", fish),
                 ("practice rounds dropped", fish[fish.practice == 2])]:
    g = build(f).reset_index().merge(t6[["id", "polydrug"]], on="id", how="left")
    b = g.dropna(subset=["polydrug", "KS", "KC", "RS", "RC"])
    N, r, rx, Z, p = mrr(b)
    same = np.allclose(build(f).loc[t6.id.values, ["KS","KC","RS","RC"]].values,
                       t6[["KS","KC","RS","RC"]].values, equal_nan=True)
    print(f"Route B, {label}: ART scores identical to table6data: {same}")
    print(f"  N={N}  r={np.round(r,4)}  Z = {Z:.4f}, p = {p:.4f}")

# polydrug check against polydrug.dta
m = t6[["id", "polydrug"]].merge(poly, on="id", how="left", suffixes=("_t6", "_pd"))
print("\npolydrug in table6data equals polydrug.dta where both present:",
      bool((m.dropna().polydrug_t6 == m.dropna().polydrug_pd).all()))
