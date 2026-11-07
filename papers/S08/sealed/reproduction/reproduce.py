"""Row.94 (node mua6d): reproduce the replication's key statistic.

Key test as RPP_mua6d.R defines it, written before running:
  data: McCrea.csv (OSF dy3zn), one row per participant: Subject, Cond, Attempted, Correct, percent, ...
  coding: Cond 1 = Handicap, Cond 2 = Control (stated only in the script's factor relabel;
          the SPSS log runs T-TEST GROUPS=Cond('Control' 'Handicap') on 'percent', filter none).
  DV: accuracy = Correct / Attempted on the math test.
  exclusions: none.
  test: independent-samples Student t (equal variances), one-tailed, H1 Control > Handicap.
  expected (table): t(59) = 2.325, p = 0.01175 (one-tailed), N = 61, d = .197.
"""
import numpy as np, pandas as pd
from scipy import stats

df = pd.read_csv("download/Data/McCrea.csv")
print("raw shape:", df.shape)
df["acc"] = df["Correct"] / df["Attempted"]
print("acc equals the 'percent' column (to 2 dp):", bool(np.allclose(df.acc.round(2), df.percent, atol=0.006)))
print("Attempted values:", df.Attempted.value_counts().to_dict())
print(df.groupby("Cond").acc.agg(["count", "mean", "std"]).round(4).to_string())
ctrl, hand = df.loc[df.Cond == 2, "acc"], df.loc[df.Cond == 1, "acc"]
t, p1 = stats.ttest_ind(ctrl, hand, equal_var=True, alternative="greater")
n1, n2 = len(ctrl), len(hand)
dfree = n1 + n2 - 2
print(f"\nStudent t, Control > Handicap: t({dfree}) = {t:.4f}, one-tailed p = {p1:.5f}, two-tailed p = {2*p1:.5f}")
sp = np.sqrt(((n1-1)*ctrl.var() + (n2-1)*hand.var()) / dfree)
d = (ctrl.mean() - hand.mean()) / sp
print(f"Cohen's d (pooled SD) = {d:.4f};  t*sqrt(1/n1+1/n2) = {t*np.sqrt(1/n1+1/n2):.4f}")
print(f"Script's d: t/sqrt(N) = {t/np.sqrt(n1+n2):.4f};  r = t/sqrt(t^2+df) = {t/np.sqrt(t*t+dfree):.4f};  r^2 = {t*t/(t*t+dfree):.4f}")
tw, pw = stats.ttest_ind(ctrl, hand, equal_var=False, alternative="greater")
print(f"Welch (check): t = {tw:.4f}, one-tailed p = {pw:.5f}")
# same test on raw Correct count (Attempted is constant if all 25)
tc, pc = stats.ttest_ind(df.loc[df.Cond==2,"Correct"], df.loc[df.Cond==1,"Correct"], alternative="greater")
print(f"On Correct count: t = {tc:.4f}, one-tailed p = {pc:.5f}")
