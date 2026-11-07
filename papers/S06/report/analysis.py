"""S06 analysis. Run from the S06 run directory:
    .venv/bin/python -I papers/S06/report/analysis.py > papers/S06/report/analysis.out
Runs the primary R analysis (analysis.R: aov with error strata, checks, figure),
then cross-checks the interaction in Python (pingouin mixed ANOVA on Weapons mean vs Flankers)."""
import subprocess, sys
import pandas as pd, pingouin as pg

r = subprocess.run(["/opt/homebrew/bin/Rscript", "papers/S06/report/analysis.R"], capture_output=True, text=True)
print(r.stdout); print(r.stderr, file=sys.stderr)

d = pd.read_csv("papers/S06/data/d11.csv")
pp = d.groupby(["ID", "HiLoCat", "Task"], as_index=False)["PD"].mean()
print("== PYTHON CROSS-CHECK: pingouin mixed_anova (Weapons mean vs Flankers) ==")
print(pg.mixed_anova(data=pp, dv="PD", within="Task", between="HiLoCat", subject="ID").round(4).to_string())
