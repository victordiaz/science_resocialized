# S09 log

Recognition: I think I recognise the design (a bilingual vs monolingual attentional-blink study, likely an original and its replication); I do not rely on any memory of its results and proceed from the data only.

Start: 2026-11-07 16:58 CET.

## Plan (written before any analysis)

- Data: `d09.sav` is expected to hold the per-participant T2|T1 proportions, one column per lag (1, 3, 5, 8), plus a group variable. `d01.zip` holds the raw E-Prime trial files; I will use it only as a check if time allows (not for the primary test).
- Variables: Group (monolingual vs bilingual, between); Lag (1, 3, 5, 8, within); DV = T2|T1 proportion correct.
- Exclusions: none, per the card (all 32 participants with complete data: 18 mono, 14 bi). If the file holds extra rows (e.g. incomplete cases), I will keep only complete cases and say how many were dropped.
- Primary test: mixed-design ANOVA, Type III SS, Group (between) × Lag (within); Group × Lag interaction F with Greenhouse-Geisser-corrected df and p; partial eta² = SS_int/(SS_int+SS_error), with a 90% CI (noncentral F inversion, standard for partial eta²).
- Claim holds if: Group × Lag interaction significant at GG-corrected p < .05 AND the pattern is in the predicted direction (bilinguals lower than monolinguals at short lags, especially lag 3). Significant interaction in the opposite direction = does not hold. Non-significant = does not hold on this data (with note on power/CI).
- Checks: cell means; Mauchly/epsilon; lag-3 Welch t-test (descriptive only); exploratory without late L2 learners if the variable exists (not the primary test).

## Commands
1. `cat PROMPT.md; cat papers/S09/card.md; cat MANIFEST.json; unzip -l d01.zip` — brief, card, file listing (zip: 32 E-Prime session folders).
2. `python -c "pyreadstat.read_sav('papers/S09/data/d09.sav') ..."` — d09.sav: 32 rows × 62 cols; T2|T1 columns `Lag{1,3,5,8}_T2_correct`; `Group` coded 1/2 without value labels.
   - Group coding decided from the questionnaire, not from outcomes: Q1 ("How many languages do you speak fluently?") is 1 for every Group=1 row and 2 for every Group=2 row, so 1 = monolingual, 2 = bilingual (verified in analysis.py).
   - Noted: participant 24145 (bilingual) has T2|T1 of .05/.02/.10/.17 while T1 accuracy is normal — looks like a scoring/response-order anomaly. Card says no exclusions, so kept in the primary test; a sensitivity analysis without it is added as a check (decided before running any test).
3. Wrote `analysis.py` (manual split-plot ANOVA + pingouin cross-check, GG epsilon, noncentral-F CI for partial eta², lag-3 Welch t, sensitivity without 24145, exploratory without late-L2 bilinguals, figure).
4. `.venv/bin/python -I papers/S09/report/analysis.py | tee papers/S09/report/analysis.out` — primary: Group × Lag F(2.33, 69.84) = 0.38, p_GG = .717, partial η² = .012, 90% CI [0, .055]. Manual and pingouin agree. Bilinguals are not lower at lag 3 (.491 vs .513, diff .022); at lags 1, 5, 8 they are slightly higher.
   - Late-L2 bilinguals identified as Group 2 with Q15 (age began English) > 12 — gives exactly the 4 the card mentions (10111, 28042, 31798, 31996). Exploratory only.
   - No change of plan. d01.zip (raw E-Prime files) not re-scored: the card states the T2|T1 cells in d09.sav were computed from those files by the replication team, and the primary test is specified on them.
5. Wrote report.md; `.venv/bin/python -I score/md2pdf.py papers/S09/report/report.md papers/S09/report/report.pdf`.
6. Wrote conclusion.json last.

End: about 17:03 CET (~5 minutes).
