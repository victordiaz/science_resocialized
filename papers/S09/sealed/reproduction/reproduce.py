"""Row.22 (node p9thw): Group (monolingual vs bilingual) x Lag (1,3,5,8) mixed ANOVA
on T2|T1 proportion correct; key effect = Group x Lag interaction, Greenhouse-Geisser corrected.
Written from the key-test definition, not from the R script's numbers.
Run: .venv/bin/python -I reproduce.py"""
import os, numpy as np, pyreadstat
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
SAV = os.path.join(HERE, "download", "4qmsg__Colzato_et_al_replication_final.sav")
LAGS = ["Lag1_T2_correct", "Lag3_T2_correct", "Lag5_T2_correct", "Lag8_T2_correct"]

df, meta = pyreadstat.read_sav(SAV)
print("raw shape", df.shape)
d = df[["Code", "Group"] + LAGS].dropna()
print("rows after dropping missing in key columns", len(d), "| Group counts", d.Group.value_counts().to_dict(),
      "| labels", meta.variable_value_labels.get("Group"))

Y = d[LAGS].to_numpy(float)            # n x k
g = d["Group"].to_numpy()
n, k = Y.shape
groups = np.unique(g)
a = len(groups)

# --- mixed ANOVA by hand (balanced within, unbalanced between; type 3 == type 2 here
# because only the between factor is unbalanced and the interaction is within-subject)
grand = Y.mean()
subj_mean = Y.mean(1)
# within-subject decomposition
SS_within_total = ((Y - subj_mean[:, None]) ** 2).sum()
cell = np.array([Y[g == gr].mean(0) for gr in groups])            # a x k
ng = np.array([(g == gr).sum() for gr in groups])
lag_mean = Y.mean(0)
# Lag main effect (unweighted == weighted for the within factor, use subject-weighted)
SS_lag = n * ((lag_mean - grand) ** 2).sum()
# interaction: sum over groups of n_g * sum_j (cell - group_mean - lag_mean + grand)^2
group_mean = np.array([Y[g == gr].mean() for gr in groups])
SS_int = sum(ng[i] * ((cell[i] - group_mean[i] - lag_mean + grand) ** 2).sum() for i in range(a))
# within error: residual from subject x lag after removing subject and group*lag
resid = np.vstack([Y[g == gr] - Y[g == gr].mean(1, keepdims=True) - cell[i] + group_mean[i]
                   for i, gr in enumerate(groups)])
SS_err = (resid ** 2).sum()
df_int, df_err = (a - 1) * (k - 1), (n - a) * (k - 1)
F_int = (SS_int / df_int) / (SS_err / df_err)
p_unc = stats.f.sf(F_int, df_int, df_err)
peta = SS_int / (SS_int + SS_err)
print(f"check: SS_within_total {SS_within_total:.6f} = SS_lag+SS_int+SS_err {SS_lag+SS_int+SS_err:.6f}")

# Greenhouse-Geisser epsilon from the pooled within-group covariance matrix (as SPSS GLM / ez)
S = sum(np.cov(Y[g == gr].T, ddof=1) * (ng[i] - 1) for i, gr in enumerate(groups)) / (n - a)
# orthonormal contrasts
C = np.linalg.qr(np.column_stack([np.ones(k), np.eye(k)[:, :k - 1]]))[0][:, 1:]
M = C.T @ S @ C
eps_gg = np.trace(M) ** 2 / ((k - 1) * np.trace(M @ M))
p_gg = stats.f.sf(F_int, df_int * eps_gg, df_err * eps_gg)
F_lag = (SS_lag / (k - 1)) / (SS_err / df_err)

print("\n=== KEY TEST: Group x Lag interaction ===")
print(f"F({df_int},{df_err}) = {F_int:.4f}; p_uncorrected = {p_unc:.4f}")
print(f"GG epsilon = {eps_gg:.4f}; GG df = ({df_int*eps_gg:.3f}, {df_err*eps_gg:.3f}); p_GG = {p_gg:.4f}")
print(f"partial eta^2 = {peta:.4f}")
print(f"(Lag main effect F({k-1},{df_err}) = {F_lag:.3f})")
print("cell means (rows = Group", list(groups), "; cols = lag 1,3,5,8):\n", np.round(cell, 4))

# cross-check with pingouin
try:
    import pingouin as pg
    long = d.melt(id_vars=["Code", "Group"], value_vars=LAGS, var_name="Lag", value_name="Correct")
    aov = pg.mixed_anova(data=long, dv="Correct", within="Lag", between="Group", subject="Code", correction=True)
    print("\npingouin mixed_anova:\n", aov.to_string())
except Exception as e:
    print("pingouin cross-check failed:", e)

# second plausible test the protocol also names: independent t-test at lag 3
t = stats.ttest_ind(d.loc[d.Group == 1, "Lag3_T2_correct"], d.loc[d.Group == 2, "Lag3_T2_correct"])
print(f"\n(secondary, not the table's test) lag-3 t-test mono vs bi: t({n-2}) = {t.statistic:.3f}, p = {t.pvalue:.4f}")
