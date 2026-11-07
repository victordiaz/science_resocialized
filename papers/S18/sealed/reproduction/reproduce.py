"""Row.107 (node edcr7): independent-samples Student t-test on implicit learning (mean RT of the two random
blocks minus mean RT of the fixed-sequence block), achievement-prime vs control, among rows flagged
Include1 = 'Include for analyses' (first 79 usable per condition). Prediction: prime > control.
Run: .venv/bin/python -I reproduce.py"""
import os, numpy as np, pyreadstat
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
SAV = os.path.join(HERE, "download", "Dataset", "SPSS dataset replication of Study 2 Eitam et al 2008 PS.sav")
df, meta = pyreadstat.read_sav(SAV)
print("raw shape", df.shape)
print("Condition labels", meta.variable_value_labels["Condition"], "| Include1 labels", meta.variable_value_labels["Include1"])
d = df[df.Include1 == 0].copy()
print("after Include1 == 0:", len(d), "| per condition", d.Condition.value_counts().to_dict())

# RB12Mean is documented as the mean of R1Mean and R2Mean; verify rather than trust
print("max |RB12Mean - (R1Mean+R2Mean)/2| =", float(np.nanmax(np.abs(d.RB12Mean - (d.R1Mean + d.R2Mean) / 2))))
d["learn"] = d.RB12Mean - d.FSMean          # positive = faster on the learned sequence
print("max |learn + Learning(stored)| =", float(np.nanmax(np.abs(d.learn + d.Learning))), "(stored Learning = FS - RB)")
print("missing learn:", int(d.learn.isna().sum()))

prime = d.loc[d.Condition == 1, "learn"]; ctrl = d.loc[d.Condition == 2, "learn"]
t = stats.ttest_ind(prime, ctrl, equal_var=True)
n1, n2 = len(prime), len(ctrl)
sp = np.sqrt(((n1 - 1) * prime.var() + (n2 - 1) * ctrl.var()) / (n1 + n2 - 2))
dval = (prime.mean() - ctrl.mean()) / sp
print("\n=== KEY TEST: learning, prime vs control, Student t ===")
print(f"mean learning prime = {prime.mean():.3f} ms (sd {prime.std():.3f}, n {n1}); control = {ctrl.mean():.3f} ms (sd {ctrl.std():.3f}, n {n2})")
print(f"t({n1+n2-2}) = {t.statistic:.4f}, p two-sided = {t.pvalue:.4f}, Cohen's d (pooled sd, prime - control) = {dval:.4f}")
w = stats.ttest_ind(prime, ctrl, equal_var=False)
print(f"(Welch, for reference: t = {w.statistic:.4f}, p = {w.pvalue:.4f})")
