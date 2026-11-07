"""S14 analysis: 3 (sound, within) x 2 (instruction, between) mixed ANOVA, sphericity assumed.
Run from env/runs/S14:  .venv/bin/python -I papers/S14/report/analysis.py"""
import numpy as np, pandas as pd, pyreadstat, pingouin as pg
from scipy import stats, optimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = "papers/S14/data/"
df, _ = pyreadstat.read_sav(D + "d04.sav")
x = pd.read_excel(D + "d05.xlsx", sheet_name=0)
cols = ["NUMBER", "TASK", "R_QUIET", "R_DISSIMILAR", "R_SIMILAR"]
a = df[cols].sort_values("NUMBER").reset_index(drop=True)
b = x[cols].sort_values("NUMBER").reset_index(drop=True)
print("d05.xlsx identical to d04.sav on analysis columns:",
      a["TASK"].equals(b["TASK"]) and np.allclose(a.iloc[:, 2:].astype(float), b.iloc[:, 2:].astype(float))
      and np.allclose(a.NUMBER, b.NUMBER))

print("N rows:", len(df), "| duplicated ids:", df.NUMBER.duplicated().sum())
print("missing on analysis vars:", df[cols].isna().any(axis=1).sum())
d = df[cols].dropna().copy()
print("N after exclusions:", len(d)); print(d.TASK.value_counts().to_string())
print("LANG counts:", df.LANG.value_counts().to_dict())

long = d.melt(id_vars=["NUMBER", "TASK"], var_name="sound", value_name="recall")
long["sound"] = long.sound.str.replace("R_", "")
print("\nCell means (SD):")
print(long.groupby(["TASK", "sound"]).recall.agg(["mean", "std", "count"]).round(4).to_string())

# ---- Primary test
aov = pg.mixed_anova(data=long, dv="recall", within="sound", between="TASK", subject="NUMBER",
                     correction=False, effsize="np2")
print("\nMixed ANOVA (sphericity assumed):"); print(aov.round(5).to_string())
row = aov[aov.Source == "Interaction"].iloc[0]
F, df1, df2, p = row.F, int(row.DF1), int(row.DF2), row["p_unc"]
np2 = df1 * F / (df1 * F + df2)

def ncp_ci(F, df1, df2, conf):
    lo_q, hi_q = (1 + conf) / 2, (1 - conf) / 2
    f = lambda nc, q: stats.ncf.cdf(F, df1, df2, nc) - q if nc > 0 else stats.f.cdf(F, df1, df2) - q
    lo = 0.0 if stats.f.cdf(F, df1, df2) < lo_q else optimize.brentq(lambda nc: f(nc, lo_q), 1e-9, 1000)
    hi = 0.0 if stats.f.cdf(F, df1, df2) < hi_q else optimize.brentq(lambda nc: f(nc, hi_q), 1e-9, 1000)
    N = df1 + df2 + 1
    return lo / (lo + N), hi / (hi + N)

ci90, ci95 = ncp_ci(F, df1, df2, .90), ncp_ci(F, df1, df2, .95)
print(f"\nPRIMARY: sound x instruction F({df1}, {df2}) = {F:.3f}, p = {p:.4f}, partial eta^2 = {np2:.4f}, "
      f"90% CI [{ci90[0]:.4f}, {ci90[1]:.4f}], 95% CI [{ci95[0]:.4f}, {ci95[1]:.4f}]")
spher = pg.sphericity(data=long, dv="recall", within="sound", subject="NUMBER")
print("Mauchly sphericity (pooled):", spher)
gg = pg.mixed_anova(data=long, dv="recall", within="sound", between="TASK", subject="NUMBER", correction=True)
print("GG check:"); print(gg.round(5).to_string())

# ---- Direction of the interaction: extra disruption = dissimilar - similar
d["extra"] = d.R_DISSIMILAR - d.R_SIMILAR
d["speech_vs_quiet"] = d.R_QUIET - (d.R_DISSIMILAR + d.R_SIMILAR) / 2
print("\nExtra disruption (dissimilar - similar) by group:")
print(d.groupby("TASK").extra.agg(["mean", "std", "count"]).round(4).to_string())
for g in ["FREE", "SERIAL"]:
    s = d[d.TASK == g]
    t = stats.ttest_rel(s.R_DISSIMILAR, s.R_SIMILAR)
    dz = s.extra.mean() / s.extra.std(ddof=1)
    ci = stats.t.interval(.95, len(s) - 1, s.extra.mean(), stats.sem(s.extra))
    print(f"  {g}: paired t({len(s)-1}) = {t.statistic:.3f}, p = {t.pvalue:.4f}, dz = {dz:.3f}, "
          f"mean diff 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]")
fr, se = d[d.TASK == "FREE"].extra, d[d.TASK == "SERIAL"].extra
t2 = stats.ttest_ind(fr, se)
diff = fr.mean() - se.mean()
sp = np.sqrt(((len(fr)-1)*fr.var() + (len(se)-1)*se.var()) / (len(fr)+len(se)-2))
cid = (diff - stats.t.ppf(.975, t2.df) * sp*np.sqrt(1/len(fr)+1/len(se)),
       diff + stats.t.ppf(.975, t2.df) * sp*np.sqrt(1/len(fr)+1/len(se)))
print(f"Similarity-contrast x group (1-df): t({t2.df:.0f}) = {t2.statistic:.3f}, p = {t2.pvalue:.4f}, "
      f"diff of diffs = {diff:.4f} 95% CI [{cid[0]:.4f}, {cid[1]:.4f}], d = {diff/sp:.3f}")
print("Speech-vs-quiet by group:"); print(d.groupby("TASK").speech_vs_quiet.agg(["mean", "std"]).round(4).to_string())

# ---- Figure
m = long.groupby(["TASK", "sound"]).recall.agg(["mean", "sem"]).reset_index()
order = ["QUIET", "DISSIMILAR", "SIMILAR"]
fig, ax = plt.subplots(figsize=(5, 3.4))
for g, mk in [("FREE", "o-"), ("SERIAL", "s--")]:
    mm = m[m.TASK == g].set_index("sound").loc[order]
    ax.errorbar(range(3), mm["mean"], yerr=1.96 * mm["sem"], fmt=mk, capsize=3, label=g.lower() + " recall")
ax.set_xticks(range(3)); ax.set_xticklabels(["quiet", "dissimilar", "similar"])
ax.set_ylabel("proportion correct"); ax.set_xlabel("background sound"); ax.legend(frameon=False)
ax.set_title(f"Mean recall (±95% CI), N = {len(d)}", fontsize=9)
fig.tight_layout(); fig.savefig("papers/S14/report/fig1.png", dpi=150)
print("figure saved: papers/S14/report/fig1.png")
