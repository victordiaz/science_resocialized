# Log — S15

**Recognition.** I think I recognise this paradigm (selective exposure under varying information quantity, the "Mr. Miller" contract case; likely Fischer et al., JPSP ~2008). I do not recall the replication's result and will proceed as if I did not recognise it; the conclusion rests only on the analysis below.

## Plan (written before any analysis)

- **Data:** `papers/S15/data/d11.csv` (the card names it as the file holding `decision`, `options`, `focus`, `_session_id`). Other files (d04, d05, d12–d14) are not named by the card as holding the analysis variables; I will only peek at their headers to check they are raw/unprocessed versions, not use them for the primary test.
- **Variables:** `options` (two / ten), `decision` (confirming / disconfirming), `focus` (control / quality / direction).
- **Exclusions (protocol, as in the card):** drop rows with blank `decision` (did not answer the information-choice question; card says 27 rows). Hypothesis-guessers are already removed from the posted file. Keep `focus == control` for the key test. Expected n = 150; I will report if it differs. No other exclusions. If `_session_id` duplicates exist, I will report them but not drop them unless clearly duplicate rows (identical records), in which case I keep the first and say so.
- **Primary test:** Pearson chi-square test of independence on the 2×2 table options × decision, control-focus only, no Yates correction, df = 1. Effect size phi = sqrt(chi²/N) with 95% CI (bootstrap and/or Fisher-z-style CI on phi as a correlation), converted to Cohen's d = 2·phi/sqrt(1−phi²).
- **Claim holds if:** p < .05 two-sided AND the direction is as predicted — the proportion choosing a confirming piece is higher with ten options than with two. Significant in the opposite direction, or p ≥ .05, → claim does not hold on this data. (If the CI is very wide with p ≥ .05 I will still say "does not hold" for the pre-registered test but comment on precision.)
- **Secondary (not the basis of the conclusion):** within-quantity goodness-of-fit tests (confirming vs 50/50) at two and at ten options in control; the same 2×2 test in quality and direction; a log-linear / logistic check of options × focus; Fisher exact test on the primary table.

## Commands
1. `head` of each data file and MANIFEST.json (structure only). d11.csv is the processed per-participant file with `decision`, `options`, `focus`; d04/d05/d12–d14 are raw platform exports (questionnaire responses, an IAT-type task, demographics, task/session logs). Primary test uses d11.csv as the card directs.
