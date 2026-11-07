# S07 log

Recognition: I recognise the task as the Angling Risk Task (Pleskac, 2008, J Exp Psych: LMC); I do not recall the replication's result and will proceed as if I did not recognise it.

Start: 2026-11-07 17:11 CET.

## Plan (written before any analysis)

Variables
- KS, KC, RS, RC: per participant, mean number of casts on rounds that ended with the participant stopping (blue-fish rounds left out), per condition (Keep/Release x Sunny/Cloudy). Computed from the trial-level file, all rounds included (no practice filter, as in the card's cleaning description).
- polydrug: sum over 11 drug classes of (rank - 1), rank 1 = never ... 6 = 4+/week. If a ready-made polydrug variable exists in the files, I will check it against my own recomputation and use the recomputed one if they agree.

Exclusions
- Drop duplicate program entries (exact duplicate trial rows / duplicate subject-round records).
- Drop the one participant whose session restarted, if identifiable in the data (e.g. a subject with a restarted/duplicated set of rounds or a flag).
- Drop participants without a drug-use score.
- Primary N = participants with all five values (KS, KC, RS, RC, polydrug).

Primary test
- Pearson r of polydrug with each of KS, KC, RS, RC; Fisher z; Meng, Rosenthal & Rubin (1992) contrast test with weights (+1, -1, +1, -1) on (KS, KC, RS, RC), r_x = median of the six inter-correlations among the four casting scores.
  Z = sum(lambda_j z_j) * sqrt((N-3) / ((1 - r_x) * h * sum(lambda_j^2))),
  where h = (1 - f * rbar^2) / (1 - rbar^2), f = (1 - r_x) / (2 * (1 - rbar^2)) capped at 1, rbar^2 = mean of the squared r's.
  Two-sided p from the standard normal.
- Effect size: the contrast in Fisher-z units (mean sunny z minus mean cloudy z), and the MRR contrast effect size r_contrast = Z / sqrt(N) ... I will report the contrast in z units with a 95% bootstrap CI (participants resampled, 5000 draws) as the interval.

What counts as the claim holding: Z > 0 with two-sided p < .05. Z > 0 with p >= .05, or Z <= 0, means it does not hold on this data (with "cannot tell" reserved for a case where the data cannot produce the test, e.g. N too small).

Robustness (not primary): Spearman correlations; excluding practice rounds; log(1+polydrug).

## Commands
- 17:11 `cat PROMPT.md; cat papers/S07/card.md; cat papers/S07/data/MANIFEST.json`
- 17:12 wrote plan above.
- 17:12 `.venv/bin/python -I scratchpad/inspect.py` (column names/labels/first values of every .dta; scratchpad = session temp dir outside the run folder, scripts only). Found: d08 = trial file (20722 rounds: id, practice, release_rule Keep/Release, weather Clear/Cloudy, casts, bluefish); d09 = id, polydrug, testeddrugs (153); d10 = per-participant KS, KC, RS, RC, polydrug, age, gender (161); d11 = drug questionnaire item level (153 ids); d14 = demographics + dup flag (161, all dup = 0); d15 = another questionnaire (not used).
- 17:14 `.venv/bin/python -I scratchpad/insp2.py` (structure only: value counts, ids, rows per id, no correlations). 161 ids in trial file + 150 rows with missing id; 150 ids have 128 rounds, 11 have 120-126. No exact duplicate rows. d11: qType 0 = ever used (yes/no) for 11 classes (qID 0,3,..,30); qType 2 (qID+2) rated 1-6, read as frequency at time of most use.
- Decision (no outcome seen): primary analysis uses KS/KC/RS/RC and polydrug recomputed from the raw files (d08, d11); these are cross-checked against the cleaned file d10/d09. Rows with missing id in d08 cannot be attributed and are dropped. "Clear" weather = Sunny.
- 17:13 wrote `papers/S07/report/analysis.py`; ran `.venv/bin/python -I papers/S07/report/analysis.py > papers/S07/report/analysis.out`. First run gave a polydrug score for only 147 participants: bug in my script (participants who never used any drug have no frequency rows, so they fell out of the pivot). Also the duplicate check had been run on a column subset (meaningless). Neither is a change of plan.
- 17:13 fixed both (reindex frequency table to all questionnaire ids, scoring them 0; duplicate check on all columns) and reran the same command. Raw recomputation now matches the cleaned files exactly (KS/KC/RS/RC and polydrug, max abs diff 0). N = 153.
- Exclusions as applied: 150 trial rows with missing id dropped (unattributable; I take these to be the restarted/duplicate program entries the card mentions; no further duplicate rows exist and no other restarted session is identifiable); 8 of 161 game completers have no drug score and are dropped. Final N = 153.
- Result of the pre-named primary test: Z = 1.248, p = .212 (positive direction, not significant) -> claim does not hold by the pre-set criterion.
- 17:15 wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S07/report/report.md papers/S07/report/report.pdf`; wrote conclusion.json last.
