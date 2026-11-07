# S29 log

Recognition: [withheld from the bundle; the full line is in the record]

## Plan (written before any analysis; I had only viewed raw file heads to identify columns)

- Data: `papers/S29/data/d05.csv` (identical bytes to d08.csv per manifest sha256). CR-only line endings; read with universal newlines.
- Variables: `ERN` (µV, error-minus-correct, 0–100 ms), `EPS` (µV, error-minus-correct startle). One row per participant: the `startle_type == "error"` rows.
- Exclusions: none beyond the posted file (card says it holds retained participants only, 42 ids). I will check that there are 42 unique ids, ERN/EPS constant within participant, and no missing ERN/EPS. Any participant missing ERN or EPS would be dropped (pairwise) and reported.
- Primary test: Pearson r between ERN and EPS, df = n − 2, one-tailed in the predicted negative direction (H1: rho < 0). Effect size r with 95% CI (Fisher z, two-sided).
- Claim holds if r < 0 and one-tailed p < .05. If r > 0 or one-tailed p ≥ .05: does not hold.
- Robustness (not primary): Spearman rho; Pearson with outliers (|z| > 3 on either variable) removed; two-tailed p reported.
- Not used: d02.csv (combined original+replication, secondary), d03/d04 (waveforms).

## Commands
Sat Nov  7 17:10:41 CET 2026
- `.venv/bin/python -I papers/S29/report/analysis.py > papers/S29/report/analysis.out 2>&1`
- Wrote report.md
- `.venv/bin/python -I score/md2pdf.py papers/S29/report/report.md papers/S29/report/report.pdf`
- No change of plan. Primary result one-tailed p = .053 > .05, so per the pre-stated criterion the claim does not hold. Outlier and Spearman checks were pre-listed robustness checks.
Sat Nov  7 17:11:19 CET 2026
- Wrote conclusion.json (last)
