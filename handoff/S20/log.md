# S20 log

Recognition: [withheld from the bundle; the full line is in the record]

Start: 2026-11-07 17:04 CET.

## Plan (written before looking at any data values)

- Data: `d02.sav` (card names it as holding the four cell means). `d04.sav` has the same SHA-256 per MANIFEST, so it is the same file; I will confirm equality in code and use `d02.sav`.
- Variables: `avg_time_sum_ac`, `avg_time_neutral_ac`, `avg_time_sum_mu`, `avg_time_neutral_mu` (mean correct RT, ms, per participant).
- Exclusions: rows with no data (rows 50-320, empty). The one participant excluded for <90% accuracy is already removed per card. If any of the 49 has a missing cell mean, I drop them (listwise) and report it. No further RT-based exclusions (the cell means are already aggregated; I have no trial-level data).
- Primary test: 2 (word pair AC/MU) x 2 (target sum/neutral) repeated-measures ANOVA; the key term is the interaction F(1, N-1), computed as the square of the one-sample t of D = (sum_AC - neutral_AC) - (sum_MU - neutral_MU). Report MSE, partial eta^2, and dz with a 95% CI (noncentral t), plus the mean of D with 95% CI.
- Criterion: the claim holds if the interaction is significant at alpha = .05 (two-sided) AND in the predicted direction (mean D > 0, i.e. sum-neutral slowing larger after AC than MU). Significant in the opposite direction or p >= .05 -> "no" (claim does not hold on this data); I will say "cannot tell" only if the data are unusable.
- Checks (not primary): main effects; simple sum-neutral slowing within AC and within MU (paired t); Wilcoxon signed-rank on D; leave-out of outliers |z|>3 on D.

## Commands
- `.venv/bin/python -I -c` inspect columns/labels/describe of d02.sav
- wrote `papers/S20/report/analysis.py`; ran `.venv/bin/python -I papers/S20/report/analysis.py > papers/S20/report/analysis.out`
- `sed` fix of pandas keyword warning (`mean(axis=1)`), re-ran analysis.py > analysis.out (numbers unchanged)
- No change of plan. Primary result: interaction F(1, 48) = 4.22, p = .045, D > 0 (predicted direction) -> criterion met.
- Note: trials per cell vary (2-15, not the 10 the card implies; total over the four cells per participant is 26-39, mean 34.2, not 40 (checked with a one-line python -I -c on d02.sav)); error rates ~20% per cell. Plan said no further exclusions; kept.
- wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S20/report/report.md papers/S20/report/report.pdf`
- End 17:06 CET (~3 minutes). Wrote conclusion.json last.
