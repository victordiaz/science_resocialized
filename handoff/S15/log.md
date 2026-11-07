# Log — S15

Recognition: [withheld from the bundle; the full line is in the record]

## Plan (written before any analysis)

- **Data:** `papers/S15/data/d11.csv` (the card names it as the file holding `decision`, `options`, `focus`, `_session_id`). Other files (d04, d05, d12–d14) are not named by the card as holding the analysis variables; I will only peek at their headers to check they are raw/unprocessed versions, not use them for the primary test.
- **Variables:** `options` (two / ten), `decision` (confirming / disconfirming), `focus` (control / quality / direction).
- **Exclusions (protocol, as in the card):** drop rows with blank `decision` (did not answer the information-choice question; card says 27 rows). Hypothesis-guessers are already removed from the posted file. Keep `focus == control` for the key test. Expected n = 150; I will report if it differs. No other exclusions. If `_session_id` duplicates exist, I will report them but not drop them unless clearly duplicate rows (identical records), in which case I keep the first and say so.
- **Primary test:** Pearson chi-square test of independence on the 2×2 table options × decision, control-focus only, no Yates correction, df = 1. Effect size phi = sqrt(chi²/N) with 95% CI (bootstrap and/or Fisher-z-style CI on phi as a correlation), converted to Cohen's d = 2·phi/sqrt(1−phi²).
- **Claim holds if:** p < .05 two-sided AND the direction is as predicted — the proportion choosing a confirming piece is higher with ten options than with two. Significant in the opposite direction, or p ≥ .05, → claim does not hold on this data. (If the CI is very wide with p ≥ .05 I will still say "does not hold" for the pre-registered test but comment on precision.)
- **Secondary (not the basis of the conclusion):** within-quantity goodness-of-fit tests (confirming vs 50/50) at two and at ten options in control; the same 2×2 test in quality and direction; a log-linear / logistic check of options × focus; Fisher exact test on the primary table.

## Commands
1. `head` of each data file and MANIFEST.json (structure only). d11.csv is the processed per-participant file with `decision`, `options`, `focus`; d04/d05/d12–d14 are raw platform exports (questionnaire responses, an IAT-type task, demographics, task/session logs). Primary test uses d11.csv as the card directs.
2. Wrote `analysis.py`; ran `.venv/bin/python -I papers/S15/report/analysis.py > papers/S15/report/analysis.out`. Checks: 496 rows, 496 unique ids, no duplicate rows; `decision` matches `infochoice == judgment1` in all 469 non-blank rows; 27 blank `decision` excluded (as the card says); control-focus n = 150 (as the card says). Primary: chi2(1, N=150) = 7.10, p = .0077, phi = .22 in the predicted direction (79% vs 59% confirming at ten vs two).
3. Second run after adding warning suppression (statsmodels perfect-fit warning from the saturated log-linear model, which is expected) and wider pandas display; numbers unchanged. No change of plan.
4. Wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S15/report/report.md papers/S15/report/report.pdf`; wrote conclusion.json last.
