"""Row.161 (node sd7kg): reproduce the replication's key statistic.

Key test, written before running. The audit script RPP_sd7kg.R fits
aov(average ~ parentvschild * Stim_cond) with sum-to-zero contrasts, takes
type-III terms via drop1, and extracts row [[4]] = the age x stimulus
INTERACTION. The table (and the replication report) carry the target-stimulus
MAIN EFFECT: F(1,44) = 1.437, p = .237, eta^2 = .032. I anchor on the table and
the report (the claim is a main effect of stimulus; Type.of.effect = main effect)
and report the script's extracted term alongside.
  data: 'LoBue & DeLoache Replication Final File Ready for Analysis.sav' (OSF nd7we),
        one row per participant; parentvschild (1 children, 2 parent),
        Stim_cond (1 snakes = find a snake among caterpillars, 2 caterpillars = find a
        caterpillar among snakes), M1..M24 trial RTs in ms (blank = incorrect/removed), average.
  exclusions: already applied in the file (8 of 56 cases removed upstream).
  test: 2 x 2 between-subjects ANOVA on average RT, type-III SS, effect-coded factors;
        key term Stim_cond; partial eta^2 = SS_effect / (SS_effect + SS_error).
"""
import numpy as np, pandas as pd, pyreadstat
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

df, meta = pyreadstat.read_sav("download/Data/LoBue & DeLoache Replication Final File Ready for Analysis.sav")
print("raw shape:", df.shape)
print(pd.crosstab(df.parentvschild.map({1: "children", 2: "parent"}), df.Stim_cond.map({1: "snakes", 2: "caterpillars"})).to_string())
M = [f"M{i}" for i in range(1, 25)]
avg = df[M].mean(axis=1, skipna=True)
print("average recomputed from M1..M24 equals the file's 'average':", bool(np.allclose(avg, df["average"])))
print("valid trials:", int(df[M].notna().sum().sum()), "of", 24 * len(df))
def run(dv, label):
    print(f"\n===== {label} =====")
    print(df.groupby(["parentvschild", "Stim_cond"])[dv].agg(["count", "mean", "std"]).round(1).to_string())
    fit = smf.ols(f"{dv} ~ C(parentvschild, Sum) * C(Stim_cond, Sum)", data=df).fit()
    a3 = anova_lm(fit, typ=3)
    print("Type-III ANOVA (sum contrasts):\n", a3.to_string())
    sse = a3.loc["Residual", "sum_sq"]; dfe = int(a3.loc["Residual", "df"])
    for term, lab in [("C(Stim_cond, Sum)", "KEY: target stimulus main effect"),
                      ("C(parentvschild, Sum)", "age main effect"),
                      ("C(parentvschild, Sum):C(Stim_cond, Sum)", "age x stimulus interaction (the script's row [[4]])")]:
        r = a3.loc[term]
        print(f"{lab}: F(1,{dfe}) = {r.F:.4f}, p = {r['PR(>F)']:.4f}, partial eta^2 = {r.sum_sq/(r.sum_sq+sse):.4f}")

pd.set_option("display.width", 200)
run("average", "Route A: DV = the file's 'average' column (what the protocol analysed)")
df["rt_trials"] = avg
run("rt_trials", "Route B: DV = mean of the valid trials M1..M24, recomputed")

# where 'average' and the trial mean disagree
bad = (df["average"] - avg).abs() > 0.01
print(f"\nparticipants whose 'average' != mean(M1..M24): {int(bad.sum())}")
for i in df.index[bad]:
    r = df.loc[i, M].astype(float)
    fits = [lab for lab, sub in [("mean(M5..M24)", r.iloc[4:]), ("mean(M1..M23)", r.iloc[:23])]
            if abs(sub.mean() - df.loc[i, "average"]) < 0.01]
    print(f"  {df.loc[i,'ID']!s:8} average={df.loc[i,'average']:.2f} mean(M1..M24)={avg[i]:.2f} matches: {fits}")
