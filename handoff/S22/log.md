# S22 log

Recognition: [withheld from the bundle; the full line is in the record]

Start: 2026-11-07 17:07 CET.

## Plan (written before any analysis)

- Data: `papers/S22/data/d03.csv`, one row per trial. Variables: `Subject`, `Grouped?` (0/1), `Rhythm?` (1 = timing trial), `Out sec 1`..`Out sec 6` (output latencies, s).
- Exclusions: none beyond the protocol (file holds the retained 40). I will check that there are 40 subjects with 20 timing trials per instruction condition. Trials with a missing latency are dropped from the mean of that cell (I will report how many, if any). No outlier trimming.
- Measure: per subject x instruction, mean latency at each position over timing trials; fit a quadratic (latency ~ 1 + pos + pos^2) to positions 2, 3, 5, 6; deviation = mean latency at 4 minus the fitted value at 4.
- Primary test: paired t-test, two-sided, deviation grouped vs ungrouped, df = 39. Effect size d_av = mean diff / sqrt((var_g + var_u)/2), with a 95% CI (noncentral-t based / bootstrap if needed; I will use a percentile bootstrap over subjects, 10,000 resamples, seed 1).
- Claim holds if: deviation grouped > ungrouped with p < .05 two-sided. Does not hold if p >= .05 (I will say "does not hold" if the estimate is near zero/opposite with a CI excluding meaningful effects; "cannot tell" only if the data are too noisy to say anything, which I will judge from the CI).
- Secondary (not the basis of the conclusion): 2 x 6 RM ANOVA (instruction x position) on per-subject mean raw latencies, timing trials; Wilcoxon signed-rank on the deviation as robustness check; same measure in the order task for context.

## Commands
- `cat papers/S22/card.md papers/S22/data/MANIFEST.json; head -5 papers/S22/data/d03.csv` (inspect; 3200 rows, 40 subjects)
- wrote `analysis.py`; `.venv/bin/python -I papers/S22/report/analysis.py > papers/S22/report/analysis.out` → 40 subjects, 20 trials per cell, no missing latencies; primary t(39) = 2.084, p = .044, d_av = 0.37.
- Change (addition, not a change of the primary): after seeing a few very long trial latencies (max 27.7 s), I added a post hoc sensitivity block (per-cell medians; latencies > 5 s set missing). The primary test is unchanged and the conclusion rests on it. Re-ran the same command.
- wrote `report.md`; `.venv/bin/python -I score/md2pdf.py papers/S22/report/report.md papers/S22/report/report.pdf` (rendered; md2pdf also left `report.html`).
- wrote `conclusion.json` last. End: 2026-11-07 17:09 CET (~3 minutes).
