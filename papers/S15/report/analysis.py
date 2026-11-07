"""S15 analysis: options x decision chi-square in control-focus condition."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

D = "papers/S15/data/d11.csv"
df = pd.read_csv(D, dtype={"zipcode": str})
print("rows in file:", len(df))
print("unique _session_id:", df["_session_id"].nunique(),
      "| fully duplicated rows:", df.duplicated().sum())
print("\nfocus x options (all rows):\n", pd.crosstab(df.focus, df.options, margins=True))
print("\ndecision values (incl. blank):\n", df.decision.value_counts(dropna=False))

# Check coding of decision: confirming iff infochoice == judgment1
chk = df.dropna(subset=["decision"]).copy()
chk["recode"] = np.where(chk.infochoice == chk.judgment1, "confirming", "disconfirming")
print("\ndecision vs recode (infochoice==judgment1):\n", pd.crosstab(chk.decision, chk.recode))

# Exclusions
blank = df.decision.isna()
print("\nexcluded: blank decision =", blank.sum())
d = df[~blank].copy()
print("after exclusion:", len(d))
c = d[d.focus == "control"]
print("control-focus n:", len(c))

def chi2_2x2(sub, label):
    t = pd.crosstab(sub.options, sub.decision).reindex(index=["two", "ten"], columns=["confirming", "disconfirming"])
    chi2, p, dof, exp = stats.chi2_contingency(t.values, correction=False)
    n = t.values.sum()
    pr = (t["confirming"] / t.sum(axis=1))
    sign = np.sign(pr["ten"] - pr["two"])
    phi = sign * np.sqrt(chi2 / n)
    return t, chi2, p, dof, exp, n, pr, phi

print("\n================ PRIMARY TEST (control focus) ================")
t, chi2, p, dof, exp, n, pr, phi = chi2_2x2(c, "control")
print(t)
print("expected counts:\n", np.round(exp, 2))
print("proportion confirming:", pr.round(4).to_dict())
print(f"Pearson chi2({dof}, N={n}) = {chi2:.4f}, p = {p:.4f} (no Yates)")
print(f"signed phi (+ = more confirming with ten) = {phi:.4f}")
# CI for phi: treat as Pearson r between two binary variables, Fisher z
z = np.arctanh(phi); se = 1 / np.sqrt(n - 3)
lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
print(f"phi 95% CI (Fisher z approx) = [{lo:.4f}, {hi:.4f}]")
# bootstrap CI for phi (stratified by options, as assigned)
rng = np.random.default_rng(20261107)
boots = []
groups = {g: c[c.options == g].decision.values for g in ["two", "ten"]}
for _ in range(10000):
    b = pd.DataFrame({"options": np.repeat(["two", "ten"], [len(groups["two"]), len(groups["ten"])]),
                      "decision": np.concatenate([rng.choice(groups["two"], len(groups["two"])),
                                                  rng.choice(groups["ten"], len(groups["ten"]))])})
    tb = pd.crosstab(b.options, b.decision).reindex(index=["two", "ten"], columns=["confirming", "disconfirming"], fill_value=0)
    if (tb.values.sum(axis=0) == 0).any():
        continue
    ch = stats.chi2_contingency(tb.values, correction=False)[0]
    prb = tb["confirming"] / tb.sum(axis=1)
    boots.append(np.sign(prb["ten"] - prb["two"]) * np.sqrt(ch / tb.values.sum()))
blo, bhi = np.percentile(boots, [2.5, 97.5])
print(f"phi 95% CI (bootstrap percentile, 10000) = [{blo:.4f}, {bhi:.4f}]")
d_of = lambda r: 2 * r / np.sqrt(1 - r**2)
print(f"Cohen's d = {d_of(phi):.4f}  95% CI [{d_of(lo):.4f}, {d_of(hi):.4f}] (from Fisher-z CI)")
# Risk difference with Newcombe-ish Wald CI
n2, n10 = t.loc["two"].sum(), t.loc["ten"].sum()
rd = pr["ten"] - pr["two"]
se_rd = np.sqrt(pr["ten"] * (1 - pr["ten"]) / n10 + pr["two"] * (1 - pr["two"]) / n2)
print(f"difference in proportion confirming (ten - two) = {rd:.4f}, 95% Wald CI [{rd-1.96*se_rd:.4f}, {rd+1.96*se_rd:.4f}]")
OR = (t.loc["ten", "confirming"] * t.loc["two", "disconfirming"]) / (t.loc["ten", "disconfirming"] * t.loc["two", "confirming"])
print(f"odds ratio (confirming, ten vs two) = {OR:.4f}")
print("Fisher exact (two-sided):", stats.fisher_exact(t.values))
print("Yates-corrected chi2 (robustness):", stats.chi2_contingency(t.values, correction=True)[:2])

print("\n================ SECONDARY ================")
for g in ["two", "ten"]:
    k = t.loc[g, "confirming"]; m = t.loc[g].sum()
    gof = stats.chisquare([k, m - k])
    bt = stats.binomtest(int(k), int(m), 0.5)
    print(f"control, {g}: confirming {k}/{m} = {k/m:.3f}; GOF chi2(1) = {gof.statistic:.3f}, p = {gof.pvalue:.4f}; binomial p = {bt.pvalue:.4f}")
for f in ["quality", "direction"]:
    t2, c2, p2, dof2, _, n2_, pr2, phi2 = chi2_2x2(d[d.focus == f], f)
    print(f"\n{f} focus:\n{t2}\nprop confirming {pr2.round(3).to_dict()}; chi2({dof2}, N={n2_}) = {c2:.3f}, p = {p2:.4f}, signed phi = {phi2:.3f}")
t3, c3, p3, dof3, _, n3, pr3, phi3 = chi2_2x2(d, "all")
print(f"\nall focus pooled:\n{t3}\nprop confirming {pr3.round(3).to_dict()}; chi2({dof3}, N={n3}) = {c3:.3f}, p = {p3:.4f}, signed phi = {phi3:.3f}")

# Log-linear (Poisson) model: three-way interaction options x focus x decision
cells = d.groupby(["options", "focus", "decision"]).size().rename("n").reset_index()
full = smf.glm("n ~ C(options)*C(focus)*C(decision)", cells, family=sm.families.Poisson()).fit()
red = smf.glm("n ~ (C(options)+C(focus)+C(decision))**2", cells, family=sm.families.Poisson()).fit()
lr = red.deviance - full.deviance; ddf = red.df_resid - full.df_resid
print(f"\nlog-linear 3-way interaction LR chi2({ddf}) = {lr:.3f}, p = {stats.chi2.sf(lr, ddf):.4f}")
# Logistic: options effect across focus conditions
d["conf"] = (d.decision == "confirming").astype(int)
lg = smf.logit("conf ~ C(options, Treatment('two')) * C(focus, Treatment('control'))", d).fit(disp=0)
print(lg.summary2().tables[1].round(4))
