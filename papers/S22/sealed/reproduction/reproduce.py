"""Row.33 (node swrhy): timing task (Rhythm?==1). Per participant and per instruction condition
(ungrouped / grouped), average the output latencies at positions 1-6 over trials, fit a quadratic to the
mean latencies at positions 2,3,5,6, take the deviation of the mean 4th latency from the fit's prediction
at position 4. Paired t-test grouped vs ungrouped on these deviations; d_av = diff / sqrt((sd1^2+sd2^2)/2).
Written from the report's description; no intermediates copied from any R script."""
import os, numpy as np, pandas as pd
from scipy import stats
here = os.path.dirname(os.path.abspath(__file__))
raw = pd.read_csv(os.path.join(here, "download", "OSF-Farrell-results-csv.csv"))
print("raw shape", raw.shape, "subjects", raw.Subject.nunique())
print("trials per subject x grouped x rhythm:\n", raw.groupby(["Grouped?", "Rhythm?"]).size() / raw.Subject.nunique())
lat = [f"Out sec {i}" for i in range(1, 7)]
t = raw[raw["Rhythm?"] == 1]
means = t.groupby(["Subject", "Grouped?"])[lat].mean()
print("missing latencies in timing trials:", int(t[lat].isna().sum().sum()))

def dev4(row, item=4):
    x = np.array([p for p in range(2, 7) if p != item], float)
    y = row[[f"Out sec {int(p)}" for p in x]].to_numpy(float)
    coef = np.polyfit(x, y, 2)
    return row[f"Out sec {item}"] - np.polyval(coef, item)

dev = means.apply(dev4, axis=1).unstack("Grouped?")
dev.columns = ["ungrouped", "grouped"]
print("n subjects with both conditions:", dev.dropna().shape[0])
print("mean deviation (s): ungrouped %.4f, grouped %.4f" % (dev.ungrouped.mean(), dev.grouped.mean()))
res = stats.ttest_rel(dev.grouped, dev.ungrouped)
diff = dev.grouped - dev.ungrouped
d_av = diff.mean() / np.sqrt((dev.grouped.std(ddof=1) ** 2 + dev.ungrouped.std(ddof=1) ** 2) / 2)
d_z = diff.mean() / diff.std(ddof=1)
print(f"KEY paired t({len(dev)-1}) = {res.statistic:.4f}, p = {res.pvalue:.4f} (two-sided), d_av = {d_av:.4f}, d_z = {d_z:.4f}")

# Secondary, not the key test: 2 (grouping) x 6 (position) repeated-measures ANOVA interaction, timing task
import pingouin as pg
long = means.reset_index().melt(id_vars=["Subject", "Grouped?"], value_vars=lat, var_name="pos", value_name="lat")
long.columns = ["Subject", "grouped", "pos", "lat"]
aov = pg.rm_anova(long, dv="lat", within=["grouped", "pos"], subject="Subject", correction=True)
print(aov.round(4).to_string())
