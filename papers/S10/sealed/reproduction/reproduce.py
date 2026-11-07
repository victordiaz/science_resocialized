"""Row.146 (node dncxa): independent reproduction of the replication's key test.

Key test (replication report, Analysis Plan + Results; RPP_dncxa.R; the .sps syntax):
object-naming group only (NamingTask == 'naming', 12 participants), by-subjects (F1)
two-sided paired t-test of mean naming RT, congruent vs incongruent picture-colour pairs.
Effect size dz = t / sqrt(n).
Exclusions (report + .sps): error trials (Errors == 1: errors, non-vocal responses,
hesitations, no responses) dropped; then trials more than 3 SD above or below that
participant's own mean RT (computed on error-free trials) dropped.

Two routes: (A) the replication's own per-subject means file F1RT_readyforanalysis.sav
(the file the audit script uses); (B) rebuilt from the trial-level alldata.sav with the
rules above, to check the aggregation.
"""
import numpy as np
import pandas as pd
import pyreadstat
from scipy import stats

D = "data/findings/Row.146/download/Data"

def paired(con, inc, label):
    t, p = stats.ttest_rel(con, inc)
    n = len(con); diff = inc - con
    print(f"[{label}] n = {n}; congruent M = {con.mean():.1f}, incongruent M = {inc.mean():.1f}, "
          f"mean diff (incong - cong) = {diff.mean():.2f} ms")
    print(f"    paired t({n-1}) = {t:.3f} (congruent minus incongruent), p = {p:.4f}, |dz| = {abs(t)/np.sqrt(n):.3f}")
    return t, p

f1, _ = pyreadstat.read_sav(f"{D}/F1RT_readyforanalysis.sav")
print("F1RT_readyforanalysis.sav:", f1.shape, f1.NamingTask.value_counts().to_dict())
obj = f1[f1.NamingTask == "naming"]
tA, pA = paired(obj.congruent_mean.values, obj.incongruent_mean.values, "A: F1 file, object naming")
col = f1[f1.NamingTask == "colour"]
paired(col.congruent_mean.values, col.incongruent_mean.values, "not key: F1 file, colour naming")

raw, _ = pyreadstat.read_sav(f"{D}/alldata.sav")
print("\nalldata.sav:", raw.shape, "subjects:", raw.Subject.nunique())
ok = raw[raw.Errors == 0].copy()
g = ok.groupby("Subject").RT
ok["lo"] = g.transform("mean") - 3 * g.transform("std")
ok["hi"] = g.transform("mean") + 3 * g.transform("std")
kept = ok[(ok.RT > ok.lo) & (ok.RT < ok.hi)]
for task in ("naming", "colour"):
    r = raw[raw.NamingTask == task]
    print(f"  {task}: trials={len(r)}, errors={int((r.Errors==1).sum())}, outliers={int(((ok.NamingTask==task)).sum() - (kept.NamingTask==task).sum())}")
m = kept.groupby(["Subject", "NamingTask", "Condition"]).RT.mean().unstack("Condition").reset_index()
mo = m[m.NamingTask == "naming"].set_index("Subject")
tB, pB = paired(mo.Congruent.values, mo.Incongruent.values, "B: rebuilt from alldata.sav, object naming")
chk = obj.set_index("Subject")[["congruent_mean", "incongruent_mean"]].join(mo)
print("  max |rebuilt - F1 file| per-subject mean:",
      round(float(np.max(np.abs(chk.congruent_mean - chk.Congruent).max())), 4),
      round(float(np.max(np.abs(chk.incongruent_mean - chk.Incongruent).max())), 4))
