# S19 log

Recognition: the design (Arabic vs Indian digits, same/different numerical vs physical judgement, distance effect) looks like a known across-notation numerical-comparison study (I believe by Ganor-Stern & Tzelgov); I do not remember its numbers and proceed as if I did not recognise it.

Start: 17:04 (wall clock).

## Commands before the plan (inspection only, no outcome computed)
- `cat PROMPT.md`, `cat papers/S19/card.md`, `cat papers/S19/data/MANIFEST.json`
- `head` of every CSV in papers/S19/data
- Python crosstab of Notation x Distance x Res x SD, Distraction x filter_$, trials per participant in d06.csv and d09.csv (to identify which file is the numerical task). Result: in d06 mixed-notation same-value pairs are mostly answered "same" -> numerical-value task; in d09 they are mostly answered "dif" -> physical task. The card also names d06 as the trial-level file whose filter matches the script. No RTs were summarised.

## Plan (written before any RT analysis)
- Data: d06.csv (numerical task, trial level, 32 participants x 264 trials). Task order from d07.csv (Order 1/2; participant 24 absent).
- Exclusions, as the card specifies: drop participant 24; drop fillers (Distraction == 1); drop same-value pairs (Distance == 0); drop errors (correct == 0); drop RT < 200 or > 2500 ms. I will report trial counts lost at each step and check the result against the filter_$ column.
- Variables: Distance 1 = small (pairs 12,21,89,98), Distance 2 = large; Notation 1/2/3 (Arabic, Indian, mixed). DV = per-participant mean RT within each Notation x Distance cell (6 cells).
- Primary test: 3 (notation, within) x 2 (difference, within) x 2 (order, between) mixed ANOVA, type III SS, on cell means; term of interest = main effect of numerical difference, F(1, 29), with MSE and partial eta squared (CI for the large-small mean difference via paired t on participant means collapsed over notation; a 90% CI for partial eta^2 from the noncentral F).
- Implementation: univariate repeated-measures ANOVA with subject error strata (R aov with Error(subject/(notation*distance)), sum-to-zero contrasts; with 2 levels of distance the distance F is unaffected by sphericity and by SS type in a balanced within design; order groups unequal 16/15 so I set contr.sum and also compute it in Python by hand as a cross-check).
- Claim holds if: main effect of difference significant at alpha = .05 (two-sided F) AND mean RT large < small. If p >= .05, does not hold (with a note on power/CI). If the direction is reversed and significant, does not hold.
- Robustness (not primary): same analysis within the mixed-notation cells only (the claim's "holds across notations" clause); compare my cell means to d33.csv/d36.csv aggregated files.

## Commands run after the plan
1. Wrote `papers/S19/report/analysis.py`; ran `.venv/bin/python -I papers/S19/report/analysis.py | tee papers/S19/report/analysis.out`. Primary result F(1, 29) = 45.27, p = 2.2e-07. The cross-check against d33.csv did not match (max |diff| 655 ms).
2. Diagnostic: `.venv/bin/python -I -c ...` comparing my cell means with d33.csv and d36.csv, and tabulating `correct` within filter_$ == 1. Findings: filter_$ already excludes P24, fillers, same-value pairs and out-of-range RTs but keeps 105 error trials; dropping those gives exactly my 3816 trials. My cell means match d36.csv exactly (max |diff| 0.0); d33.csv must be the other (physical) task's aggregate. 
3. Change (cross-check only, not the plan): pointed the cross-check at d36.csv instead of d33.csv; fixed a column-name bug (`sed -i` on analysis.py); reran `.venv/bin/python -I papers/S19/report/analysis.py > papers/S19/report/analysis.out`.
4. No change to the primary test. Note: R's aov uses sequential SS (F = 45.59 for distance); the primary, type III value from the per-subject contrast model is F = 45.27 (groups are 16/15, so they differ slightly). Same MSE (3575).
5. Wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S19/report/report.md papers/S19/report/report.pdf`; wrote conclusion.json last.
