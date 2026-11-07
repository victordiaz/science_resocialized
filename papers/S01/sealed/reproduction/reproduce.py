"""Row.151 (node apidb), Study 2 data: one-way between-subjects ANOVA (= Student t, equal variances) of the
mean rating of six moral vignettes by condition (0 = no hand-washing, 1 = hand-washing, per the codebook),
excluding participants who said all answers were made up (Madeup_dummy == 1) or had an experimenter error
(Exp_Error == 1). Composite rebuilt from the six vignette items and checked against the stored mean_vignettes.
Cohen's d with pooled SD; sign = hand-washing minus no hand-washing (the claim predicts negative)."""
import os, numpy as np, pandas as pd, pyreadstat
from scipy import stats
here = os.path.dirname(os.path.abspath(__file__))
df, meta = pyreadstat.read_sav(os.path.join(here, "download", "Study 2 Dataset", "Exp2_Data.sav"))
print("raw shape", df.shape, "| Condition counts", df.Condition.value_counts().to_dict())
items = ["Dog", "Trolley", "Wallet", "Plane", "Resume", "Kitten"]
print("item range:", float(df[items].min().min()), "-", float(df[items].max().max()))
comp = df[items].mean(axis=1)
print("max |rebuilt composite - mean_vignettes|:", float((comp - df.mean_vignettes).abs().max()))
print("Madeup_dummy x Exp_Error:\n", pd.crosstab(df.Madeup_dummy, df.Exp_Error))
d = df[(df.Madeup_dummy != 1) & (df.Exp_Error != 1)].copy()
d["comp"] = d[items].mean(axis=1)
print("after exclusions:", len(d), "| by Condition", d.Condition.value_counts().to_dict())
g0, g1 = d.loc[d.Condition == 0, "comp"], d.loc[d.Condition == 1, "comp"]
print("means: no-wash %.4f (n=%d), wash %.4f (n=%d)" % (g0.mean(), len(g0), g1.mean(), len(g1)))
F, p = stats.f_oneway(g0, g1)
t = stats.ttest_ind(g1, g0, equal_var=True)
sp = np.sqrt(((len(g0) - 1) * g0.var(ddof=1) + (len(g1) - 1) * g1.var(ddof=1)) / (len(g0) + len(g1) - 2))
dd = (g1.mean() - g0.mean()) / sp
print(f"KEY F(1,{len(d)-2}) = {F:.5f}, p = {p:.4f}; t({len(d)-2}) = {t.statistic:.4f}; d (wash - no wash, pooled) = {dd:.4f}")
