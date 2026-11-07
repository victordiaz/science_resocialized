"""Row.53 (node wkgpq): HiLoCat (HighIMS-LowEMS vs HighIMS-HighEMS, between) x Task (Weapons vs Flankers,
within) mixed ANOVA on process-dissociation control estimates (PD); key = HiLoCat x Task interaction.
The audit script and the authors' own analysis file both fit aov(PD ~ HiLoCat*Task + Error(ID/Task)) on the
long file in which each ID has TWO Weapons rows (Black, White trial types) and ONE Flankers row. This file
re-implements that multistratum model from projections (no R numbers copied), then runs the 'clean'
alternative (Weapons rows averaged per ID) as a secondary.
Run: .venv/bin/python -I reproduce.py"""
import os, numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, "download", "Dataset", "repdatalong.csv"))
print("raw shape", d.shape, "| unique IDs", d.ID.nunique())
print(d.groupby(["Task", "TrialType"]).size().to_dict())
print("IDs per HiLoCat", d.groupby("HiLoCat").ID.nunique().to_dict())
d = d.sort_values(["ID", "Task", "TrialType"]).reset_index(drop=True)
y = d.PD.to_numpy(float)
N = len(y)

def indicator(keys):
    codes, uniq = pd.factorize(keys)
    Z = np.zeros((N, len(uniq))); Z[np.arange(N), codes] = 1
    return Z

def proj(Z):
    return Z @ np.linalg.pinv(Z)

P_id = proj(indicator(d.ID.astype(str)))
P_cell = proj(indicator(d.ID.astype(str) + "_" + d.Task))
P_1 = np.full((N, N), 1.0 / N)  # intercept stratum removed, as R does
strata = {"ID": P_id - P_1, "ID:Task": P_cell - P_id, "Within": np.eye(N) - P_cell}

hi = (d.HiLoCat == "HighIMSLowEMS").astype(float).to_numpy()   # effect-coded below
task = (d.Task == "Weapons").astype(float).to_numpy()
X_terms = [("HiLoCat", (hi - hi.mean())[:, None]),
           ("Task", (task - task.mean())[:, None]),
           ("HiLoCat:Task", ((hi - hi.mean()) * (task - task.mean()))[:, None])]

results = {}
for sname, P in strata.items():
    ys = P @ y
    df_stratum = int(round(np.trace(P)))
    fitted_cols, ss_prev, rows = [], 0.0, []
    for tname, X in X_terms:
        Xs = P @ X
        if np.linalg.norm(Xs) < 1e-8 * np.sqrt(N):
            continue
        cols = np.column_stack(fitted_cols + [Xs])
        beta, *_ = np.linalg.lstsq(cols, ys, rcond=None)
        ss_model = ((cols @ beta) ** 2).sum()
        rows.append((tname, 1, ss_model - ss_prev))
        fitted_cols.append(Xs); ss_prev = ss_model
    ss_res = (ys ** 2).sum() - ss_prev
    df_res = df_stratum - len(rows)
    print(f"\nStratum {sname}: df {df_stratum}")
    for tname, df1, ss in rows:
        F = (ss / df1) / (ss_res / df_res)
        p = stats.f.sf(F, df1, df_res)
        results[(sname, tname)] = (ss, F, p, df1, df_res, ss_res)
        print(f"  {tname:13s} df {df1}  SS {ss:.5f}  F {F:.4f}  p {p:.4f}")
    print(f"  Residuals     df {df_res}  SS {ss_res:.5f}")

ss, F, p, df1, df2, ss_res = results[("ID:Task", "HiLoCat:Task")]
print("\n=== KEY TEST: HiLoCat x Task interaction (ID:Task stratum, as fit by the authors and the audit) ===")
print(f"F({df1},{df2}) = {F:.4f}, p = {p:.4f}, partial eta^2 = {ss/(ss+ss_res):.4f}, n IDs = {d.ID.nunique()}")

# Secondary: average the two Weapons rows per ID, then 2x2 mixed ANOVA == t-test on (Flankers - Weapons)
w = d.pivot_table(index=["ID", "HiLoCat"], columns="Task", values="PD", aggfunc="mean").reset_index()
w["diff"] = w["Flankers"] - w["Weapons"]
a = w.loc[w.HiLoCat == "HighIMSLowEMS", "diff"]; b = w.loc[w.HiLoCat == "HighIMSHighEMS", "diff"]
t = stats.ttest_ind(a, b)
df_t = len(a) + len(b) - 2
F2 = t.statistic ** 2
print(f"\n(secondary, Weapons averaged per ID) interaction F(1,{df_t}) = {F2:.4f}, p = {t.pvalue:.4f}, "
      f"partial eta^2 = {F2/(F2+df_t):.4f}")
print("cell means (Weapons averaged):\n", w.groupby("HiLoCat")[["Flankers", "Weapons"]].mean().round(4))
