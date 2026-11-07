# S25 log

Recognition: [withheld from the bundle; the full line is in the record]

Started: (see `date` output below, first command).

## Plan (written before any analysis)

- Data: one tab-separated file per participant, 80 trials each. Columns used: `list` (EN/NL), `length` (1 = short, 2 = long), `nr_correct` (0-8).
- File-count note: the card says 15 participants, but 17 files are given (d06-d20 have 81 lines = header + 80 trials; d21, d22 have 86 lines). Before analysis I will inspect only the structure of d21/d22 (row counts, columns, whether rows are trials or duplicates/extra rows) to decide whether they are participant files. Rule I fix now: a file counts as one participant if it contains 80 trials with the expected structure (any extra lines that are not trials, e.g. blank or comment lines, are dropped). If d21/d22 turn out to be duplicates of other files, they are dropped. If all 17 are valid distinct participants, the primary test uses all valid participant files (the card's "no exclusions" rule), and I report the 15-vs-17 discrepancy.
- DV: per participant and cell, mean of nr_correct/8 over the 20 lists of that cell, rounded to 3 decimals (as the card specifies).
- Exclusions: none (per card), apart from the file-validity rule above.
- Primary test: paired t-test, English short vs English long, one-sided H1: short > long, df = n - 1; d_z = t/sqrt(n), with a 95% CI for d_z (noncentral-t) and for the mean difference.
- Claim holds if one-sided p < .05 with mean difference > 0. If p >= .05: "does not hold" (with an equivalence-style comment on the CI if informative).
- Robustness (not the basis of the conclusion): Wilcoxon signed-rank; unrounded DV; Dutch lists; language x length ANOVA-type check.

## Commands
- `date` -> Sat Nov  7 17:07:58 CET 2026
- `awk/cut/md5` structure checks on d21, d22 (row counts, field counts, non-trial lines, hash of trial rows cols 1-12 for every file). Finding: d21 and d22 each contain a 1-field header line ("1_newnew", "7new") plus 4 demographic footer lines, and 80 trial rows. Their trial rows are identical to d06 (d21) and d17 (d22). Per the pre-set rule they are duplicates and are dropped; n = 15 distinct participants (d06-d20), matching the card. No other duplicates.
- `.venv/bin/python -I papers/S25/report/analysis.py > papers/S25/report/analysis.out`
- `awk` sanity checks on d06-d20: English length 1 words are one-syllable (BOSS, CHILD...), length 2 words are multi-syllable (PROSECUTOR, ELEPHANT...), so the coding matches the card; recomputing nr_correct from presented vs clicked words gives 0 mismatches across all 1,200 English trials.
- No change of plan. Primary result: t(14) = 0.496, one-sided p = .314, d_z = 0.13 -> claim does not hold on this data.
- `.venv/bin/python -I score/md2pdf.py papers/S25/report/report.md papers/S25/report/report.pdf`
- Finished Sat Nov  7 17:09:09 CET 2026; wrote conclusion.json last.
