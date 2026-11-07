"""Row.84 (node v8vft): control-focus participants only; 2x2 Pearson chi-square without Yates correction,
options (two vs ten pieces of new information) x decision (selected piece confirming vs disconfirming the
participant's own prior judgment). Exclusions from the report: no answer on the primary DV (choice);
participants judged aware of the hypothesis are already absent from all.sas7bdat (removed in its SAS build).
Effect size: phi = sqrt(chi2/N); d by the standard conversion 2*phi/sqrt(1-phi^2), and by the audit
script's formula 2*phi/(1-phi^2) for comparison."""
import os, numpy as np, pandas as pd, pyreadstat
from scipy import stats
here = os.path.dirname(os.path.abspath(__file__))
ds = os.path.join(here, "download", "Dataset - Replication of Fischer et al. (2008, JPSP)")
df, _ = pyreadstat.read_sas7bdat(os.path.join(ds, "all.sas7bdat"))
print("raw shape", df.shape)
df["decision"] = df["decision"].replace("", np.nan)
print("blank decision:", df.decision.isna().sum())
script_ids = {1901775, 1902268, 1902419, 1903277, 1903508, 1903545, 1903573, 1903817, 1904356, 1904722, 1904780,
              1904834, 1905222, 1905269, 1905391, 1905498, 1906500, 1907320, 1907839, 1907960, 1908232, 1908540,
              1908556, 1908581, 1908720, 1909591, 1909951}
blank_ids = set(df.loc[df.decision.isna(), "_session_id"].astype(float).astype(int))
print("blank-decision ids == audit script's 27 listed ids:", blank_ids == script_ids)
aware = ['1901549','1902091','1902335','1903358','1903606','1903694','1904148','1904677','1904989','1905015','1905289',
         '1905474','1905484','1905509','1905560','1906197','1906317','1906539','1906585','1906695','1906888','1907043',
         '1908016','1908093','1908418','1908580','1908585','1909075','1909171','1909473']
print("aware ids (SAS build list) still present:", df._session_id.astype(float).astype(int).astype(str).isin(aware).sum())
d = df.dropna(subset=["decision"])
print("after excluding blank DV:", len(d), d.focus.value_counts().to_dict())
c = d[d.focus == "control"]
tab = pd.crosstab(c.options, c.decision)
print("control-focus table (N=%d):\n%s" % (len(c), tab))
print("row % confirming:", (tab["confirming"] / tab.sum(axis=1)).round(3).to_dict())
chi2, p, dof, exp = stats.chi2_contingency(tab.to_numpy(), correction=False)
phi = np.sqrt(chi2 / len(c))
print(f"KEY chi2({dof}, N={len(c)}) = {chi2:.4f}, p = {p:.5f}; phi = {phi:.4f}; "
      f"d (2phi/sqrt(1-phi^2)) = {2*phi/np.sqrt(1-phi**2):.4f}; d (script, 2phi/(1-phi^2)) = {2*phi/(1-phi**2):.4f}")
chi2y, py, _, _ = stats.chi2_contingency(tab.to_numpy(), correction=True)
print(f"with Yates correction (not the key test): chi2 = {chi2y:.4f}, p = {py:.5f}")
for f in ["quality", "direction"]:
    s = d[d.focus == f]; ch, pp, _, _ = stats.chi2_contingency(pd.crosstab(s.options, s.decision).to_numpy(), correction=False)
    print(f"secondary, {f} focus: chi2(1, N={len(s)}) = {ch:.3f}, p = {pp:.4f}")
