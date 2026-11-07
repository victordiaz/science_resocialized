"""Row.24 (node sqim7): 2 (prime: AC aligned-categorical vs MU misaligned-unrelated)
x 2 (digit target: sum vs neutral) within-subject ANOVA on mean correct-response latency;
the key statistic is the prime x target interaction.
Written from the replication report and RPP_sqim7.R before opening data:
  data = EXP 1s.sav, rows 1-49 (rows 50-320 are empty); table F(1,48) = 4.22, p = .045,
  'Effect.Size.R' = 'MSE = 9,999' (an error term, not an effect size).
"""
import os, math
import pandas as pd, numpy as np
from scipy import stats
import pyreadstat
from statsmodels.stats.anova import AnovaRM

HERE = os.path.dirname(os.path.abspath(__file__))
df, meta = pyreadstat.read_sav(os.path.join(HERE, "download", "Data", "EXP 1s.sav"))
print("EXP 1s.sav shape:", df.shape)
cols = ["avg_time_sum_ac", "avg_time_neutral_ac", "avg_time_sum_mu", "avg_time_neutral_mu"]
df = df.dropna(subset=["id"])            # empty trailing rows
print("rows with an id:", len(df), " unique ids:", df["id"].nunique(), " NA in the four cells:", int(df[cols].isna().sum().sum()))
n = len(df)
print("cell means (ms):", {c: round(df[c].mean(), 1) for c in cols})
print("cell SEMs (ms):", {c: round(df[c].std(ddof=1) / math.sqrt(n), 1) for c in cols})

long = df.melt(id_vars="id", value_vars=cols, var_name="cell", value_name="RT")
long["prime"] = np.where(long["cell"].str.endswith("_ac"), "AC", "MU")
long["target"] = np.where(long["cell"].str.contains("_sum_"), "sum", "neutral")
res = AnovaRM(long, depvar="RT", subject="id", within=["prime", "target"]).fit()
print("\nstatsmodels AnovaRM (2x2 within):\n", res.anova_table)

# interaction by hand: F = t^2 of the difference of differences; SS and MSE from it
dd = (df["avg_time_sum_ac"] - df["avg_time_neutral_ac"]) - (df["avg_time_sum_mu"] - df["avg_time_neutral_mu"])
t, p = stats.ttest_1samp(dd, 0)
ss_eff = n * dd.mean() ** 2 / 4
ss_err = ((dd - dd.mean()) ** 2).sum() / 4
F = ss_eff / (ss_err / (n - 1))
print(f"\n[hand] interaction contrast (sum-neutral)AC - (sum-neutral)MU: mean = {dd.mean():.2f} ms")
print(f"[hand] F(1,{n-1}) = {F:.4f} (t^2 = {t**2:.4f}), p = {p:.6f}")
print(f"[hand] SS_effect = {ss_eff:.1f}, SS_error = {ss_err:.1f}, MSE = {ss_err/(n-1):.1f}, partial eta^2 = {ss_eff/(ss_eff+ss_err):.4f}")
# simple effects the report also gives
for pr in ("ac", "mu"):
    tt, pp = stats.ttest_rel(df[f"avg_time_sum_{pr}"], df[f"avg_time_neutral_{pr}"])
    print(f"[simple] sum vs neutral within {pr.upper()}: t({n-1}) = {tt:.3f}, p = {pp:.4f}")
