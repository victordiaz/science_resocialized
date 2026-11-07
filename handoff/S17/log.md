# S17 log

Recognition: [withheld from the bundle; the full line is in the record]

## Plan (written before any analysis)

- Data: `papers/S17/data/d05.sav` (48 rows, one per participant, post-exclusion analysis file per the card). `d08.csv` will be inspected only to understand its content (possibly the raw/unexcluded file) and to check exclusions.
- Variables: DV = `average` (participant mean latency, ms, over valid correct trials). Factors: target stimulus (snake vs caterpillar target), age group (child vs parent), identified from the variable labels in the .sav.
- Exclusions: those already applied by the replication team per the card (5 children >50% errors; 3 z>3 outliers), giving N = 48. I apply no further exclusions. If d05.sav does not contain 48 rows in the stated cells, I will reconstruct from d08.csv and say so.
- Primary test: two-way between-subjects ANOVA, average ~ stimulus * age, effect (sum-to-zero) coding, type-III SS. Key term: stimulus main effect, F(1, 44), two-tailed p, partial eta^2 with 95% CI (noncentral-F based).
- Claim holds if: stimulus main effect p < .05 AND the snake-target cell marginal mean latency is lower than the caterpillar-target one. Significant in the opposite direction or p >= .05 -> does not hold.
- Robustness (not the basis of the conclusion): Welch t-test snake vs caterpillar overall; per-age-group t-tests; log-latency ANOVA; Rscript cross-check of the type-III ANOVA.

## Commands
1. `.venv/bin/python -I -c "...pyreadstat.read_sav('papers/S17/data/d05.sav')..."` — inspect columns, labels, value labels; `head -c 1500 papers/S17/data/d08.csv; wc -l` — inspect CSV.
2. Wrote `papers/S17/report/analysis.py` (primary type-III ANOVA + robustness + figure).
3. `.venv/bin/python -I papers/S17/report/analysis.py > papers/S17/report/analysis.out 2>&1`
4. inline python: rows where `average` differs from mean(M1..M24).
5. Added a sensitivity refit using the recomputed mean of M1..M24 (9 rows' stored `average` differ from it; the card names `average` as the DV, so the primary stays on `average`). Re-ran: `.venv/bin/python -I papers/S17/report/analysis.py > papers/S17/report/analysis.out 2>&1`.
   No change to the primary plan. d08.csv (56 raw rows with selections) was only inspected, not used: the card defines the analysis file as d05.sav with exclusions applied.
6. Wrote `papers/S17/report/report.md`; rendered: `.venv/bin/python -I score/md2pdf.py papers/S17/report/report.md papers/S17/report/report.pdf`.
7. Change of plan: the planned Rscript cross-check of the type-III ANOVA was not run (the statsmodels result is reported; the robustness set is otherwise as planned plus a median-latency ANOVA and the recomputed-mean refit).
8. Wrote `papers/S17/report/conclusion.json` (last).
