"""Row.64 (node mxryb): 3 (processing style: global / local / control) x 2 (semantic prime:
aggression / neutral) between-participants ANOVA on aggressivenessScore (mean of the two
critical ratings Q5 assertive-hostile and Q8 determined-belligerent); key statistic = interaction.
Written from the replication report and RPP_mxryb.R before opening data:
  exclusions = participants who guessed the purpose (discard == 1; the audit script drops rows
  16, 23, 68 by position); N.R = 71; table F(2,65) = 0.865, p = .426, partial eta^2 = .0259.
"""
import os, csv, io
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "download", "Data", "RPP data.csv")
raw = open(path, "rb").read().decode("utf-8", errors="replace")
print("line endings: CR-only" if "\r" in raw and "\n" not in raw else "line endings: other")
rows = list(csv.DictReader(io.StringIO(raw.replace("\r\n", "\n").replace("\r", "\n"))))
df = pd.DataFrame(rows)
print("raw shape:", df.shape)
df["discard"] = df["discard"].astype(int)
print("discard==1 at 1-based row positions:", [i + 1 for i in df.index[df["discard"] == 1]], "PIDs:", list(df.loc[df["discard"] == 1, "PID"]))
for c in ["Q5", "Q8", "aggressivenessScore"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
print("aggressivenessScore == (Q5+Q8)/2 for all rows:", bool(np.allclose(df["aggressivenessScore"], (df["Q5"] + df["Q8"]) / 2)))
d = df[df["discard"] == 0].copy()
print("after exclusions:", len(d), " unique PID:", d["PID"].nunique(), " (PID 18 rows:", d.loc[d.PID == "18", ["gender", "age"]].values.tolist(), ")")
print("cell n:\n", pd.crosstab(d["mapCondition"], d["puzzleCondition"]))
print("cell means:\n", d.pivot_table(index="puzzleCondition", columns="mapCondition", values="aggressivenessScore", aggfunc="mean").round(2))

m_sum = smf.ols("aggressivenessScore ~ C(mapCondition, Sum) * C(puzzleCondition, Sum)", data=d).fit()
a3 = anova_lm(m_sum, typ=3)
a2 = anova_lm(smf.ols("aggressivenessScore ~ C(mapCondition) * C(puzzleCondition)", data=d).fit(), typ=2)
print("\nType III (sum contrasts, as in the replicators' own script):\n", a3)
print("\nType II (as in RPP_mxryb.R):\n", a2)
row = [i for i in a2.index if ":" in i][0]
ss_e, ss_r = a2.loc[row, "sum_sq"], a2.loc["Residual", "sum_sq"]
print(f"\n[interaction] F({int(a2.loc[row,'df'])},{int(a2.loc['Residual','df'])}) = {a2.loc[row,'F']:.4f}, p = {a2.loc[row,'PR(>F)']:.6f}, partial eta^2 = {ss_e/(ss_e+ss_r):.4f}")
