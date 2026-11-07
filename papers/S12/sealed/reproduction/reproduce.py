"""Row.135 (node 2gkjt): implicit person preference (IAT D score, signed so positive = preference for
the positively-described individual, or for the member of that individual's group), compared between
participants who rated the ORIGINAL pair (rateorig == 1) and those who rated the NEW pair (rateorig == 0).
Welch two-sample t-test, immediate session only. The original's prediction: NO difference (implicit
attitudes generalize immediately).
Written from the replication report and RPP_2gkjt.R before opening data:
  exclusions = exppref not NA, d not NA, fastpct10 == 0, alltrials == 200;
  N.R = 3597; table t(3511.1) = -6.31, p ~ 0 (3.14e-10), d = .21.
  The audit script also runs the explicit test (exppref) first; it is not the table's key test.
"""
import os
import pandas as pd, numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "download", "Data_and_Analysis", "impex_final_dataset.csv"), low_memory=False)
print("raw shape:", df.shape)
steps = [("exppref not NA", lambda x: x["exppref"].notna()),
         ("d not NA", lambda x: x["d"].notna()),
         ("fastpct10 == 0", lambda x: x["fastpct10"] == 0),
         ("alltrials == 200", lambda x: x["alltrials"] == 200)]
fin = df
for name, f in steps:
    fin = fin[f(fin)]
    print(f"after {name}: {len(fin)}")
print("rateorig counts:", fin["rateorig"].value_counts(dropna=False).to_dict(), " imppref NA:", int(fin["imppref"].isna().sum()))

# independent check of the DV: rebuild imppref from the raw D score and the counterbalancing flag
re = np.where(fin["reemgood"].astype(bool), -fin["d"], fin["d"])
print("imppref == sign-aligned d (rebuilt) for all rows:", bool(np.allclose(re, fin["imppref"])))

def welch(var):
    new = fin.loc[fin["rateorig"] == 0, var].dropna(); orig = fin.loc[fin["rateorig"] == 1, var].dropna()
    t, p = stats.ttest_ind(new, orig, equal_var=False)
    v1, v2 = new.var(ddof=1) / len(new), orig.var(ddof=1) / len(orig)
    df_w = (v1 + v2) ** 2 / (v1 ** 2 / (len(new) - 1) + v2 ** 2 / (len(orig) - 1))
    sp = np.sqrt(((len(new) - 1) * new.var(ddof=1) + (len(orig) - 1) * orig.var(ddof=1)) / (len(new) + len(orig) - 2))
    d = (orig.mean() - new.mean()) / sp
    print(f"[{var}] new pair n={len(new)} M={new.mean():.4f} SD={new.std(ddof=1):.4f}; original pair n={len(orig)} M={orig.mean():.4f} SD={orig.std(ddof=1):.4f}")
    print(f"[{var}] Welch t({df_w:.1f}) = {t:.4f} (new minus original), p = {p:.3e}; Cohen's d (pooled SD) = {d:.4f}; 2t/sqrt(df) = {2*abs(t)/np.sqrt(df_w):.4f}")

print("\nKEY (implicit):"); welch("imppref")
print("\nother test in the script (explicit):"); welch("exppref")
