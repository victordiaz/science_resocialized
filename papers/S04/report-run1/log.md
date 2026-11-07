# S04 log

Recognition: the design resembles Turk-Browne, Isola, Scholl & Treat (2008), "Multidimensional visual statistical learning"; I do not recall its numbers and proceed as if I did not recognise it.

Start: see first command timestamp below.

## Plan (written before any data were opened)

- Variables: per participant, proportion correct on the 16 trials with `triplet_type == "real"` (field `correct`). Pseudo trials discarded.
- Data source: the 15 subjectNN.mat files inside d02.zip (the card's described structure). d04–d18.mat (15 loose files) are presumably the same subjects; I will check they are identical/consistent but use the zip contents as primary. If the zip and loose files disagree I will log it.
- Exclusions: none (as specified on the card). Only check that each subject has 16 real trials and valid 0/1 correct values.
- Primary test: two-sided one-sample t-test of the 15 proportions vs 0.5; d = t/sqrt(n), with a 95% CI for d (noncentral t) and 95% CI for the mean proportion.
- Claim holds if mean > 0.5 and p < .05 (two-sided). Does not hold if p >= .05 (data do not support above-chance familiarity; with n=15 I will say whether the CI is compatible with a meaningful effect). If mean < 0.5 with p < .05, claim does not hold.
- Robustness (not for the conclusion): Wilcoxon signed-rank vs 0.5; trial-level binomial test pooled; pseudo-trial accuracy reported descriptively.

## Commands
- 16:55 `cat PROMPT.md card.md; ls data` (read brief, card)
- 16:56 wrote plan above
- 16:57 listed d02.zip; it holds subject01-15.mat and analysis.m (the replicators' MATLAB script: per-subject mean of correct on real trials, ttest vs 0.5, plus a secondary run excluding subjects 3 and 5 as "explicit learners"). Plan unchanged; that exclusion is reported only as sensitivity since the card says no exclusions.
- 16:59 wrote analysis.py; ran `.venv/bin/python -I papers/S04/report/analysis.py | tee papers/S04/report/analysis.out`
- 17:02 wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S04/report/report.md papers/S04/report/report.pdf`
- No change of plan. Result: claim holds (t(14)=3.71, p=.0023).
- 17:03 wrote conclusion.json (last).
