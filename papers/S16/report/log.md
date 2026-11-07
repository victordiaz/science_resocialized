# Log — S16

Recognition: I believe I recognise the paradigm (object words with typical locations cueing up/down letter identification; likely Estes, Verges & Barsalou 2008). I carry on as if I did not; nothing below uses recalled results.

## Plan (written 17:02, before any look at the data)

- Variables: Subj (participant), typisch (1 = typical, 2 = atypical), resp_corr (1 correct, 0 incorrect). Error = 1 − resp_corr.
- Exclusions: none (card: no participants excluded, all 60 experimental trials count for error rates). I will only check that resp_corr agrees with the Correct string, that each participant has 60 trials (30 per condition), and drop rows only if resp_corr is missing (will report if any).
- DV: per-participant error rate in each condition (proportion of trials incorrect).
- Primary test: one-way repeated-measures ANOVA by subjects (F1), location (typical vs atypical), F(1, n−1), p, partial eta² = SS_loc/(SS_loc+SS_err), with 95% CI for partial eta² (via noncentral F inversion) and the mean difference with a 95% CI.
- Claim holds if: error rate typical > atypical AND p < .05 (two-sided F). If p ≥ .05 → "no" (claim not supported on this data); if the direction is reversed and significant → "no".
- Robustness (not primary): paired t-test (equivalent), Wilcoxon signed-rank, trial-level logistic GLMM-ish check (GEE clustered by subject).

## Commands
1. `cd .../env/runs/S16 && cat PROMPT.md; ls -R papers score` — read brief.
2. `cat papers/S16/card.md papers/S16/data/MANIFEST.json` — read card.
3. (plan above written here, before data)
4. `.venv/bin/python -I -c "...read_sav; head; dtypes; value labels; value_counts; trials per Subj"` — structure check only: 1320 rows, 22 participants × 60, resp_corr 0/1 (45 errors), typisch 1/2 balanced. No missing values. No outcome by condition looked at.
5. Wrote `papers/S16/report/analysis.py`; ran `.venv/bin/python -I papers/S16/report/analysis.py | tee papers/S16/report/analysis.out`.
   Result: F(1,21) = 1.45, p = .242, partial η² = .065 [0, .31]; typical 4.09% vs atypical 2.73% errors.
6. Wrote report.md; rendered `.venv/bin/python -I score/md2pdf.py papers/S16/report/report.md papers/S16/report/report.pdf`.
7. Wrote conclusion.json last.

No change of plan. No exclusions applied (none needed: no missing data, all 22 × 60 trials present). Extra file: fig1.png (the figure, under report/).
