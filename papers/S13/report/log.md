# S13 log

**Recognition.** The design (MOT with distractor-centroid localisation vs a guessing phase) looks like the ensemble-statistics-outside-attention study (Alvarez & Oliva, 2008, I believe). I do not recall its replication outcome and carry on as if I did not recognise it; nothing below uses recall.

Start: 2026-11-07 17:00 CET.

## Plan (written before any analysis of the data)

- **Data.** `d19.dta` (the file the card says the key test reads): per-trial rows, 120 trials per subject (80 test, 40 guessing); `angle` = localisation error in degrees. The `.txt` files (17, one per participant presumably) are raw per-participant logs; used only for cross-checks if needed.
- **Variables.** Per participant: (a) mean `angle` over test-phase trials with all four **distractors** missing (centroid test, distractors); (b) mean `angle` over all guessing-phase trials with four dots missing.
- **Exclusions.** None at participant level (per the card). At trial level: none planned; trials with missing `angle` are dropped (counted and reported). No outlier trimming.
- **Primary test.** Paired t-test, two-tailed, (a) − (b), df = n − 1; dz = t/√n with 95% CI (noncentral-t). Also mean difference with 95% CI.
- **Claim holds if** t < 0 and p < .05 (distractor-centroid error smaller than guessing error). Holds "no" if p ≥ .05 or t > 0; "cannot tell" only if the data cannot form the comparison.
- **Secondary (not for conclusion).** Single-distractor vs single-guess; target centroid vs guess; Wilcoxon signed-rank on primary as robustness.

The first step after this plan is only structural inspection (column names, value labels, counts per condition) to map the card's conditions to codes; no outcome comparisons until the script is written.

## Commands
1. `.venv/bin/python -I -c "import pyreadstat; ..."` — inspect d19.dta columns, labels, condition counts (structure only).
2. `head`/`sed` on d02.txt and d18.txt; crosstab of condition × one_vs_four × tar_vs_dis × ExGuess (structure only).

### Structural findings and a plan addition (before any outcome comparison)
- 17 subjects × 120 trials; no missing `angle`. `condition` 1–4 is crossed with `one_vs_four` (1,2 = one missing; 3,4 = four missing) and, in the test phase, with `tar_vs_dis` (conditions 1,3 → code 11; conditions 2,4 → code 1). In the guessing phase `tar_vs_dis` is missing but `condition` still runs 1–4 (10 trials each per subject; the display was generated the same way). No value labels anywhere, so **which code (1 or 11) means "distractor" is not stated in the data**.
- `missing_x/y` in d19 for four-missing trials is the area-weighted centroid (differs from the plain mean in the raw .txt v7/v8), consistent with the card; I use `angle` from d19 as given.
- **Plan addition (made now, before looking at any errors):** identify the distractor code with a manipulation check that is not the primary test: in the test phase, *individual* (one-missing) trials, the tracked targets must be localised more accurately than the untracked distractors (that is what tracking means). The code with the larger mean single-dot error is taken as "distractor". If the two codes do not differ clearly on that check (paired p ≥ .05), the mapping is undetermined and I will report the primary test under both mappings and conclude "cannot tell" unless both agree.
- Primary comparison: test phase, `one_vs_four==4` & distractor code, vs guessing phase `one_vs_four==4` (conditions 3 and 4 pooled, 20 trials per subject).
3. `.venv/bin/python -I papers/S13/report/analysis.py | tee papers/S13/report/analysis.out` — mapping check, primary test, secondary/robustness, figure.
4. First run failed in the noncentral-t CI root-finder (bracket ±50 gave NaN); narrowed bracket to t±10 with `sed`, reran: `.venv/bin/python -I papers/S13/report/analysis.py > papers/S13/report/analysis.out`. No change to the analysis plan.
5. Secondary test hit a NaN in the noncentral-t root-finder; replaced brentq with a fine grid search over nc (t±8, step 0.001) via a short python edit; reran same command. Primary numbers unchanged apart from the CI method.
6. Wrote `report.md`; rendered with `.venv/bin/python -I score/md2pdf.py papers/S13/report/report.md papers/S13/report/report.pdf`.

## Outcome
Mapping check fixed code 11 = distractor (p < .001). Primary: t(16) = −9.59, p = 4.9e-8, dz = −2.33 → claim holds. Also holds under the reversed mapping. Surprise: distractor centroid error < target centroid error.
7. Wrote `conclusion.json` last.
