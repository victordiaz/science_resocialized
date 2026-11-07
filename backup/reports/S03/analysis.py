"""S03 analysis: one-way ANOVA of mixed-feelings index on Condition (d05.txt, Include==1)."""
import sys, numpy as np, pandas as pd
from scipy import stats, optimize
import pingouin as pg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)
D = "papers/S03/data/"
OUT = "papers/S03/report/"
df = pd.read_csv(D + "d05.txt", sep="\t", skiprows=3, na_values=[".", " ", ""], keep_default_na=True)
print("rows read:", len(df), "cols:", df.shape[1])
inc = [c for c in df.columns if c.startswith("Include")][0]
df = df.rename(columns={inc: "Include"})
print("Include counts:\n", df["Include"].value_counts(dropna=False))
print("Include x SexOffender:\n", pd.crosstab(df["Include"], df["SexOffender"], dropna=False))
for c in ["StrongMixed", "NotTorn", "Indecisive", "Condition"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

def index(d):
    items = pd.DataFrame({"sm": d["StrongMixed"], "nt": -d["NotTorn"], "ind": d["Indecisive"] - 4})
    return items.mean(axis=1, skipna=True), items.notna().sum(axis=1)

df["Ambiv"], df["n_items"] = index(df)
a = df[df["Include"] == 1].copy()
print("\nExcluded (Include==0):", (df["Include"] == 0).sum())
print("Included rows by condition:\n", a["Condition"].value_counts().sort_index())
print("Items answered among included:\n", a["n_items"].value_counts())
a = a[a["n_items"] > 0]
n = len(a)
print("n analysed:", n)

print("\nDescriptives (index):")
desc = a.groupby("Condition")["Ambiv"].agg(["count", "mean", "std"])
desc["se"] = desc["std"] / np.sqrt(desc["count"])
print(desc.round(3))
print("\nItem means by condition (recoded):")
print(a.assign(NotTorn_R=-a["NotTorn"], Ind_RC=a["Indecisive"] - 4).groupby("Condition")[["StrongMixed", "NotTorn_R", "Ind_RC"]].mean().round(3))
items = pd.DataFrame({"sm": a["StrongMixed"], "nt": -a["NotTorn"], "ind": a["Indecisive"] - 4}).dropna()
print("Cronbach alpha:", pg.cronbach_alpha(items))

# Primary: one-way ANOVA
groups = [a.loc[a["Condition"] == k, "Ambiv"].values for k in (0, 1, 2)]
F, p = stats.f_oneway(*groups)
aov = pg.anova(data=a, dv="Ambiv", between="Condition", detailed=True)
print("\nPRIMARY one-way ANOVA:\n", aov)
ss_b, ss_w = aov.loc[0, "SS"], aov.loc[1, "SS"]
df1, df2 = 2, n - 3
eta2 = ss_b / (ss_b + ss_w)

def nc_ci(F, df1, df2, conf=0.95):
    def lam_for(q):
        f = lambda lam: stats.ncf.cdf(F, df1, df2, lam) - q
        if f(0) < 0:
            return 0.0
        return optimize.brentq(f, 0, 1000)
    lo = lam_for(1 - (1 - conf) / 2)
    hi = lam_for((1 - conf) / 2)
    N = df1 + df2 + 1
    return lo / (lo + N), hi / (hi + N)

lo, hi = nc_ci(F, df1, df2)
print(f"F({df1}, {df2}) = {F:.3f}, p = {p:.4f}, eta^2 = {eta2:.3f}, 95% CI [{lo:.3f}, {hi:.3f}]")
print("Levene (median):", stats.levene(*groups))
print("Shapiro on residuals:", stats.shapiro(np.concatenate([g - g.mean() for g in groups])))

# Secondary
print("\nWelch ANOVA:\n", pg.welch_anova(data=a, dv="Ambiv", between="Condition"))
print("Kruskal-Wallis:", stats.kruskal(*groups))
print("\nCond 1 vs 2 (Student and Welch):")
print(pg.ttest(groups[1], groups[2], correction=False))
print(pg.ttest(groups[1], groups[2], correction=True))
print("\nTukey HSD:\n", pg.pairwise_tukey(data=a, dv="Ambiv", between="Condition"))

# Cross-check on d06
b = pd.read_csv(D + "d06.tsv", sep="\t", na_values=[".", " ", ""])
for c in ["StrongMixed", "NotTorn", "Indecisive", "Condition", "Ambiv"]:
    b[c] = pd.to_numeric(b[c], errors="coerce")
b["Ambiv_re"], b["n_items"] = index(b)
print("\n[d06] rows:", len(b), "SexOffender:", b["SexOffender"].value_counts(dropna=False).to_dict())
print("[d06] max |Ambiv - recomputed|:", np.nanmax(np.abs(b["Ambiv"] - b["Ambiv_re"])))
bb = b[(b["SexOffender"].str.strip() == "No") & (b["n_items"] > 0)]
print("[d06] SexOffender==No by condition:", bb["Condition"].value_counts().sort_index().to_dict())
print("[d06] ANOVA:\n", pg.anova(data=bb, dv="Ambiv_re", between="Condition", detailed=True))
print("[d06] means:", bb.groupby("Condition")["Ambiv_re"].mean().round(3).to_dict())

# Figure
fig, ax = plt.subplots(figsize=(4.5, 3.2))
labels = ["0 neutral", "1 favour only", "2 for & against"]
rng = np.random.default_rng(1)
for k, g in enumerate(groups):
    ax.scatter(k + rng.uniform(-0.12, 0.12, len(g)), g, s=10, alpha=0.4, color="grey")
    m, se = g.mean(), g.std(ddof=1) / np.sqrt(len(g))
    ax.errorbar(k, m, yerr=1.96 * se, fmt="o", color="black", capsize=4)
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("Mixed-feelings index (-3..3)")
ax.set_title(f"F({df1},{df2}) = {F:.2f}, p = {p:.3f}", fontsize=9)
fig.tight_layout(); fig.savefig(OUT + "fig1.png", dpi=150)
print("figure written")
