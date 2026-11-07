"""Row.117 (node rzjvn): independent reproduction of the replication's key test.

Key test (replication report, Analysis Plan + Table 2; RPP_rzjvn.R; the spreadsheet's own
note: Matlab anovan(z, {me ta so}, 'model', 'full')): a full-factorial fixed-effects ANOVA
on 720 per-subject cell values (12 subjects x 3 measures x 2 targets x 10 SOAs), with
subject NOT in the model (every cell treated as an independent observation, as the
original did). Key statistic: the three-way interaction measure x target x SOA,
F(18, 660).

Column labels: the spreadsheet heads the factor columns 'efficacy', 'latency', 'precision'.
They are the factors measure (3 levels: efficacy, latency, precision), target (2: T1, T2)
and SOA (10: 1-10 items); the sheet's note maps me -> 'efficacy', ta -> 'latency',
so -> 'precision', and the level counts (3, 2, 10) confirm it.
"""
import warnings
import numpy as np
import pandas as pd
import openpyxl
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

warnings.filterwarnings("ignore", category=UserWarning)
F = "data/findings/Row.117/download/Dataset/Vul_etal_Original_Replication_ANOVA_datasets.xlsx"
ws = openpyxl.load_workbook(F, data_only=True)["Sheet1"]
rows = list(ws.iter_rows(min_row=6, values_only=True))
rep = pd.DataFrame([r[6:11] for r in rows if r[6] is not None],
                   columns=["y", "measure", "target", "soa", "subject"])
orig = pd.DataFrame([r[0:5] for r in rows if r[0] is not None],
                    columns=["y", "measure", "target", "soa", "subject"])
for name, d in (("replication", rep), ("original (for reference only)", orig)):
    print(f"\n== {name}: rows={len(d)}, subjects={d.subject.nunique()}, levels: measure={sorted(d.measure.unique())}, target={sorted(d.target.unique())}, soa={sorted(d.soa.unique())}")
    print("   cells per subject:", d.groupby("subject").size().unique())
    m = smf.ols("y ~ C(measure, Sum) * C(target, Sum) * C(soa, Sum)", data=d).fit()
    for typ in (2, 3):
        a = anova_lm(m, typ=typ)
        key = "C(measure, Sum):C(target, Sum):C(soa, Sum)"
        r = a.loc[key]; sse = a.loc["Residual", "sum_sq"]
        print(f"   [type {typ}] measure x target x SOA: F({int(r['df'])},{int(m.df_resid)}) = {r['F']:.3f}, p = {r['PR(>F)']:.3g}, partial eta^2 = {r['sum_sq']/(r['sum_sq']+sse):.3f}")
    if name == "replication":
        # Sensitivity, not the key test: the same term with subject as a blocking factor.
        m2 = smf.ols("y ~ C(subject) + C(measure, Sum) * C(target, Sum) * C(soa, Sum)", data=d).fit()
        r2 = anova_lm(m2, typ=2).loc["C(measure, Sum):C(target, Sum):C(soa, Sum)"]
        print(f"   [sensitivity, subject as block] F({int(r2['df'])},{int(m2.df_resid)}) = {r2['F']:.3f}, p = {r2['PR(>F)']:.3g}")
