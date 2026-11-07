"""Row.12 (node 7rtcz): Sound (quiet/dissimilar/similar, within) x Task (free/serial, between)
mixed ANOVA on correct recall; key term = Sound x Task interaction, uncorrected (sphericity assumed).
Written from the design, sums of squares by hand; pingouin as an independent check."""
import os, numpy as np, pandas as pd, pyreadstat
from scipy import stats
here = os.path.dirname(os.path.abspath(__file__))
df, meta = pyreadstat.read_sav(os.path.join(here, "download", "replication_marsh.sav"))
print("raw shape", df.shape)
cells = ["R_QUIET", "R_DISSIMILAR", "R_SIMILAR"]
d = df[["NUMBER", "TASK"] + cells].dropna()
print("n after dropping missing on key vars:", len(d), d.TASK.value_counts().to_dict())
print("cell means by task:\n", d.groupby("TASK")[cells].mean().round(3))

Y = d[cells].to_numpy(float); g = d.TASK.to_numpy()
N, k = Y.shape; groups = np.unique(g); a = len(groups)
gm = Y.mean()
subj_m = Y.mean(1)
SS_total = ((Y - gm) ** 2).sum()
SS_between_subj = k * ((subj_m - gm) ** 2).sum()
SS_task = sum(k * (g == G).sum() * (Y[g == G].mean() - gm) ** 2 for G in groups)
SS_subj_w_task = SS_between_subj - SS_task
SS_within = SS_total - SS_between_subj
SS_sound = N * ((Y.mean(0) - gm) ** 2).sum()
cell = {G: Y[g == G].mean(0) for G in groups}
SS_cells = sum((g == G).sum() * ((cell[G] - gm) ** 2).sum() for G in groups)
SS_inter = SS_cells - SS_sound - SS_task
SS_err_w = SS_within - SS_sound - SS_inter
df_inter = (k - 1) * (a - 1); df_err = (k - 1) * (N - a)
F = (SS_inter / df_inter) / (SS_err_w / df_err)
p = stats.f.sf(F, df_inter, df_err)
pes = SS_inter / (SS_inter + SS_err_w)
eta_stratum = SS_inter / (SS_sound + SS_inter + SS_err_w)
F_sound = (SS_sound / (k - 1)) / (SS_err_w / df_err)
F_task = (SS_task / (a - 1)) / (SS_subj_w_task / (N - a))
print(f"main Sound: F({k-1},{df_err})={F_sound:.3f}, p={stats.f.sf(F_sound,k-1,df_err):.4g}")
print(f"main Task:  F({a-1},{N-a})={F_task:.3f}, p={stats.f.sf(F_task,a-1,N-a):.4g}")
print(f"KEY Sound x Task: F({df_inter},{df_err})={F:.4f}, p={p:.4f}, partial eta^2={pes:.4f}, within-stratum eta^2={eta_stratum:.4f}")
try:
    import pingouin as pg
    long = d.melt(id_vars=["NUMBER", "TASK"], value_vars=cells, var_name="SOUND", value_name="R")
    print(pg.mixed_anova(long, dv="R", within="SOUND", between="TASK", subject="NUMBER", correction=False).round(4).to_string())
except Exception as e:
    print("pingouin check failed:", e)

# Secondary (not the key test): the follow-up paired t, dissimilar vs similar, within each task
for G in groups:
    s = d[d.TASK == G]
    t = stats.ttest_rel(s.R_DISSIMILAR, s.R_SIMILAR)
    print(f"secondary, {G}: paired t({len(s)-1})={t.statistic:.3f}, p={t.pvalue:.4g}")
