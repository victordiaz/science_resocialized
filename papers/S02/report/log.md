# Log — S02

Recognition: I recognise the paradigm in general (continuous identification with recognition, "misses faster than correct rejections", in the line of single-system signal-detection accounts of priming), but not this specific replication or its result. Carrying on as if I did not.

Start: 2026-11-07 (wall clock noted via `date` in commands).

## Plan (written before opening any data file)

- **Data:** `papers/S02/data/d07.dat` (per-participant mean test-phase identification RT per cell; columns include `meanRT_cr`, `meanRT_miss`). This is the file the card says the key test was run on.
- **Variables:** `meanRT_cr` (mean RT, correct rejections) and `meanRT_miss` (mean RT, misses), one pair per participant.
- **Exclusions:** none at participant level (card: none excluded, n = 32). A participant would be dropped only if either of the two key cells is missing (no misses or no CRs), since a paired test needs both; I will report any such case. No trial-level filter on the primary test because the aggregate file has none (as the card states).
- **Primary test:** two-sided paired t-test, `meanRT_cr` vs `meanRT_miss`, df = n − 1. Effect size dz = t/√n (= mean diff / SD diff), with 95% CI for the mean difference and for dz (noncentral-t interval).
- **Claim holds if:** mean(CR − miss) > 0 and p < .05 (two-sided). Holds "no" if p ≥ .05 or the difference goes the other way. "Cannot tell" only if the data are unusable for the test.
- **Robustness (not the basis of the conclusion):** Wilcoxon signed-rank on the same pairs; if the trial-level file (`d14.sav`) allows it, recompute cell means from trials, with and without the protocol's misidentification filter, and rerun the paired t-test.

## Commands
- `cd .../env/runs/S02; cat PROMPT.md; cat papers/S02/card.md; cat papers/S02/data/MANIFEST.json` — brief and card.
- (plan above written here, 16:55)
- `head` of d07.dat, d02.txt, d03/d05/d09.dat; pyreadstat read of d04/d06/d08/d10/d14.sav (shapes, column names, first rows). d07: vpnum, meanRT_hit, meanRT_cr, meanRT_fa, meanRT_miss. d14: 5440 trial rows (32 × 170), with phase, word_type, word_korrekt, rating, tresp, SDT_category. d02.txt says no analysis script was shared.
- value counts of d14 codings (phase, word_type, word_korrekt, rating, SDT_category) and tresp by SDT_category in the test phase. SDT_category 0 (3 trials) all at tresp = 3775 (no response). Mapping of SDT_category codes to cells to be verified in analysis.py against d07.
- `.venv/bin/python -I papers/S02/report/analysis.py` (first version: primary test + code check). Primary: t(31) = 2.398, p = .0227, dz = 0.42. SDT_category codes verified by exact reproduction of all four d07 columns from d14: 1 = hit, 2 = CR, 3 = FA, 4 = miss (word_type 0 = studied, rating 0 = "old"). No change to the plan.
- Added robustness block to analysis.py: cell means recomputed from d14 with the protocol's identification filter (drop test trials with word_korrekt = 0, and studied words misidentified at study), and also dropping no-response trials (tresp ≥ 3750).
- `.venv/bin/python -I papers/S02/report/analysis.py > papers/S02/report/analysis.out 2>&1` — full run. Robustness A (protocol identification filter): 42 study and 42 test misidentifications; one participant lost all miss trials, n = 31, t(30) = 2.43, p = .022. B (also drop 4 no-response trials): t(30) = 2.41, p = .022. C (per-participant medians): t(31) = 2.65, p = .013. Miss cells are small (2 to ~20 trials per participant, median 8). Figure fig1.png written.
- `grep` of score/md2pdf.py for image support.
- Wrote report.md; `.venv/bin/python -I score/md2pdf.py papers/S02/report/report.md papers/S02/report/report.pdf` (renderer also left report.html alongside).
- Wrote conclusion.json last. No change of plan at any point; conclusion rests on the primary test.
