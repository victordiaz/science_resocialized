# Log, study S01

Recognition: I recognise this design (a hand-washing-after-disgust-clip study of moral judgment and a direct replication of it); I carry on as if I did not and base the conclusion only on the computation below.

Start: 16:55 (Sat 7 Nov 2026).

## Plan (written before opening the data)

- Data: `papers/S01/data/d12.sav` only (the card says d11.sav is the first study and is not this test).
- Variables: DV `mean_vignettes` (mean of the six 1-7 wrongness ratings `Dog`, `Trolley`, `Wallet`, `Plane`, `Resume`, `Kitten`); group `Condition` (0 = no hand-washing, 1 = hand-washing, per codebook labels; I will check the value labels in the file).
- Exclusions (pre-registered, as on the card): drop `Madeup_dummy` == 1 and `Exp_Error` == 1. Do not apply `Final_Rating` suspicion filters in the primary test. Expected N after exclusions: 126. Cases with missing DV or Condition are dropped and reported.
- Check: recompute the mean of the six items and compare to the stored `mean_vignettes`; the primary test uses the stored variable as the card names it (if they disagree, I report it).
- Primary test: one-way between-subjects ANOVA of `mean_vignettes` by `Condition` (= Student t-test, equal variances), F(1, N-2), two-sided p. Effect size: Cohen's d, pooled SD, hand-washing minus control, with 95% CI (noncentral-t CI; normal-approx CI as check).
- Criterion for "the claim holds": d < 0 (hand-washing lower) and two-sided p < .05. If p >= .05, the claim does not hold on this data; I will additionally report whether the CI excludes effects of the size a claim of this kind needs ("cannot tell" only if the data are too few/unusable to decide, e.g. the CI is wide enough to include both a sizeable negative effect and zero and the sample is far below planned N — with N ~126 near the planned 104 I will treat a non-significant result as "does not hold").
- Robustness (not the conclusion): Welch t; Mann-Whitney; with Final_Rating suspicion filter applied; no exclusions; per-item t-tests.

## Commands
- Inspected d12.sav columns, value labels, exclusion flags (python -I, pyreadstat).
- Checked variable/value labels in d12.sav (none for Condition values; relying on the card: 0 = no wash, 1 = wash).
- Wrote analysis.py; ran `.venv/bin/python -I papers/S01/report/analysis.py > papers/S01/report/analysis.out`.
- Checked that score/md2pdf.py supports relative images (grep).
- Wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S01/report/report.md papers/S01/report/report.pdf`.
- Wrote conclusion.json last.

No change of plan. Result: F(1,124) = 0.001, p = .97, d = 0.01 [-0.35, 0.36]; criterion (d < 0 and p < .05) not met -> "no".
Note: the `Disgusted` emotion variable has values around 18 (not a 1-7 item); I reported it only descriptively and it plays no role in the conclusion.
End: about 16:57 (about 2 minutes of wall time).
