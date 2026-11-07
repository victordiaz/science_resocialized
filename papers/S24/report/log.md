# S24 log

Recognition: I do not recognise this specific study (a German-language short-term recognition task with long-short / short-long list types); proceeding from the data only.

Start: 2026-11-07 17:07 CET.

## Plan (written before any analysis)

- Data: `d03.sav` is expected to be the wide file (`subject, listtype, correct, intrusion, new`), one row per participant; `d05.csv` is trial-level data (one row per trial, with `condition`, `correct`, `listtype`). I will use the wide file as the card describes; I will recompute per-participant proportions from the trial file only as a consistency check.
- Variables: DV = proportion correct per participant per test-word type; between = `listtype` (`long-short` vs `short-long`); within = test-word type (`correct`, `intrusion`, `new`).
- Exclusions: none (as stated in the card). Every participant in the wide file enters. Expected N = 21 (11 / 10).
- Primary test: 2 x 3 mixed ANOVA (type-III SS; with one between and one within factor in a balanced-within design this equals the standard split-plot decomposition), key term = list-type main effect, F(1, 19), two-tailed p, partial eta squared = SS_between / (SS_between + SS_subjects-within-groups), with a 90%/95% CI for partial eta squared by noncentral-F inversion.
- Direction: the claim holds if the list-type main effect is significant at alpha = .05 AND the `long-short` group's mean accuracy is lower than the `short-long` group's. A significant effect in the opposite direction, or p >= .05, means the claim does not hold on this data.
- Secondary (not the basis of the conclusion): Welch t / one-way ANOVA on the `new` column alone; the type and interaction terms; trial-file recomputation check.

## Commands
1. `cat PROMPT.md; cat papers/S24/card.md; cat papers/S24/data/MANIFEST.json; head -c 1500 papers/S24/data/d05.csv; wc -l` (read brief, card, data head).
2. Wrote the plan above.
3. `.venv/bin/python -I -c "...pyreadstat.read_sav('papers/S24/data/d03.sav')..."`: d03.sav is the wide file, 21 rows, 11 long-short / 10 short-long, columns as the card says. Subject 1012 (not 112) looks like a typo for 112 in the ID only; kept, no exclusions.
4. `.venv/bin/python -I -c "...pd.read_csv('papers/S24/data/d05.csv')..."`: trial file, 5376 rows = 21 x 256 trials (8 blocks x 32); 128 correct / 64 intrusion / 64 new probes per participant. Note: every list in both groups has 6 words, so the trial file does not show a list-length difference between the groups; `long-short` / `short-long` must code something the file does not record (e.g. timing). I follow the card's labelling. No change to the plan.
5. Wrote `papers/S24/report/analysis.py`; ran `.venv/bin/python -I papers/S24/report/analysis.py > papers/S24/report/analysis.out 2>&1`. Wide file matches trial-file recomputation exactly (max diff 0). Primary: F(1,19) = 3.66, p = .071, partial eta^2 = .16 (95% CI [0, .43]); direction opposite to the claim (long-short group M = .900 vs short-long M = .807). Robustness checks (drop lowest-accuracy participant 106, Mann-Whitney) were added after seeing the data, as checks only; they do not change the primary test.
6. Wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S24/report/report.md papers/S24/report/report.pdf`.
7. Wrote conclusion.json last.
