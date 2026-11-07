import hashlib, numpy as np, pandas as pd
from scipy import stats
P = "papers/S08/data/d02.csv"
print("sha256", hashlib.sha256(open(P,"rb").read()).hexdigest())
d = pd.read_csv(P)
print("rows", len(d), "Cond counts", d.Cond.value_counts().sort_index().to_dict())
print("missing Cond/Attempted/Correct:", d[["Cond","Attempted","Correct"]].isna().sum().to_dict())
print("Attempted==0:", int((d.Attempted==0).sum()), " Correct>Attempted:", int((d.Correct>d.Attempted).sum()))
print("duplicate Subject ids:", int(d.Subject.duplicated().sum()))
d = d.dropna(subset=["Cond","Attempted","Correct"])
d = d[d.Attempted>0].copy()
d["prop"] = d.Correct/d.Attempted
print("max |prop - percent|:", float((d.prop-d.percent).abs().max()))
print("N after exclusions", len(d))
print(d.groupby("Cond")[["Attempted","Correct","prop"]].agg(["count","mean","std"]).round(4).to_string())
pr = d.loc[d.Cond==1,"prop"].values; ct = d.loc[d.Cond==2,"prop"].values
n1,n2 = len(ct),len(pr)
t,p = stats.ttest_ind(ct, pr, equal_var=True, alternative="greater")
df = n1+n2-2
print(f"\nPRIMARY Student t (control - practice): t({df}) = {t:.3f}, one-tailed p = {p:.4f}, two-tailed p = {2*min(p,1-p):.4f}")
sp = np.sqrt(((n1-1)*ct.var(ddof=1)+(n2-1)*pr.var(ddof=1))/df)
diff = ct.mean()-pr.mean(); se = sp*np.sqrt(1/n1+1/n2)
tc = stats.t.ppf(.975, df)
print(f"mean diff = {diff:.4f}, 95% CI [{diff-tc*se:.4f}, {diff+tc*se:.4f}]")
dz = diff/sp
# noncentral-t CI for d
from scipy.optimize import brentq
k = np.sqrt(1/n1+1/n2)
lo = brentq(lambda nc: stats.nct.sf(t, df, nc)-0.025, -20, 20)
hi = brentq(lambda nc: stats.nct.cdf(t, df, nc)-0.025, -20, 20)
print(f"Cohen's d = {dz:.3f}, 95% CI [{lo*k:.3f}, {hi*k:.3f}]")
tw,pw = stats.ttest_ind(ct, pr, equal_var=False, alternative="greater")
print(f"\nCheck Welch: t = {tw:.3f}, one-tailed p = {pw:.4f}")
u,pu = stats.mannwhitneyu(ct, pr, alternative="greater")
print(f"Check Mann-Whitney U = {u:.1f}, one-tailed p = {pu:.4f}")
print("Levene p =", round(stats.levene(ct,pr).pvalue,4), " Shapiro p (ctrl, prac) =", round(stats.shapiro(ct).pvalue,4), round(stats.shapiro(pr).pvalue,4))
for v in ["Attempted","Correct"]:
    a=d.loc[d.Cond==2,v]; b=d.loc[d.Cond==1,v]
    tt,pp = stats.ttest_ind(a,b,equal_var=True)
    print(f"Exploratory {v}: control {a.mean():.2f} vs practice {b.mean():.2f}, t({df}) = {tt:.3f}, two-tailed p = {pp:.4f}")
