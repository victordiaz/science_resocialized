"""Row.167 (node vwnit): one-way within-subjects ANOVA (F1, by subjects), factor = target location relative to
the cue word's typical location (typisch 1 = typical, 2 = atypical), DV = per-subject error rate; the table's
row is the error-rate test (its p .24 and F 1.45 match the error-rate line of the report; the RT test is also
computed here as a secondary). Predicted direction: worse performance (more errors, slower RT) at the typical
location. Error-rate analysis uses all 60 experimental trials per subject; RT analysis excludes incorrect
trials and RT > 1000 ms.
Run: .venv/bin/python -I reproduce.py"""
import os, numpy as np, pandas as pd, pyreadstat
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
df, meta = pyreadstat.read_sav(os.path.join(HERE, "download", "Dataset", "Data_Replication_EstesEtAl_PS2008_20130622150957.sav"))
print("raw shape", df.shape, "| subjects", df.Subj.nunique(), "| trials per subject", df.groupby("Subj").size().unique().tolist())
print("typisch labels", meta.variable_value_labels.get("typisch"), "| resp_corr labels", meta.variable_value_labels.get("resp_corr"))
assert ((df.Correct.str.strip() == "True") == (df.resp_corr == 1)).all()
print("Correct (string) and resp_corr agree on every trial: yes")

def rm_anova_2level(wide):
    """one-way RM ANOVA with 2 levels, by hand: returns F, df1, df2, p, partial eta^2"""
    Y = wide.to_numpy(float); n, k = Y.shape
    gm = Y.mean()
    ss_cond = n * ((Y.mean(0) - gm) ** 2).sum()
    ss_subj = k * ((Y.mean(1) - gm) ** 2).sum()
    ss_err = ((Y - gm) ** 2).sum() - ss_cond - ss_subj
    df1, df2 = k - 1, (n - 1) * (k - 1)
    F = (ss_cond / df1) / (ss_err / df2)
    return F, df1, df2, stats.f.sf(F, df1, df2), ss_cond / (ss_cond + ss_err)

df["error"] = 1 - df.resp_corr
er = df.groupby(["Subj", "typisch"]).error.mean().unstack()
F, d1, d2, p, pe = rm_anova_2level(er)
print("\n=== KEY TEST: location typicality on error rate (F1, by subjects) ===")
print(f"mean error rate typical = {er[1].mean():.4f}, atypical = {er[2].mean():.4f}  (n = {len(er)})")
print(f"F({d1},{d2}) = {F:.4f}, p = {p:.4f}, partial eta^2 = {pe:.4f}")
t = stats.ttest_rel(er[1], er[2]); print(f"paired t check: t^2 = {t.statistic**2:.4f}, p = {t.pvalue:.4f}")
# generalized eta^2 (what the audit script's ez 'ges' line would print), for the comparison
Y = er.to_numpy(); n = len(Y); gm = Y.mean()
ss_cond = n * ((Y.mean(0) - gm) ** 2).sum(); ss_subj = 2 * ((Y.mean(1) - gm) ** 2).sum()
ss_err = ((Y - gm) ** 2).sum() - ss_cond - ss_subj
print(f"generalized eta^2 = {ss_cond/(ss_cond+ss_subj+ss_err):.4f}")

rt = df[(df.resp_corr == 1) & (df.RT <= 1000)]
print(f"\n(secondary) RT analysis: kept {len(rt)} of {len(df)} trials "
      f"({(df.resp_corr==0).mean()*100:.1f}% incorrect, {(df.RT>1000).mean()*100:.1f}% > 1000 ms)")
m = rt.groupby(["Subj", "typisch"]).RT.mean().unstack()
F2, a1, a2, p2, pe2 = rm_anova_2level(m)
print(f"RT typical = {m[1].mean():.2f} ms, atypical = {m[2].mean():.2f} ms; F({a1},{a2}) = {F2:.4f}, p = {p2:.4f}, partial eta^2 = {pe2:.5f}")
