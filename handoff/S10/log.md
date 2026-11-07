# S10 log

Recognition: [withheld from the bundle; the full line is in the record]

Start: 2026-11-07 16:59 CET.

## Plan (written before any analysis)

- Data: trial-level file `d06.sav` (primary source; per-participant means will be re-derived from it). `d02.sav` (given condition means) used only as a cross-check.
- Variables: Subject, NamingTask (keep `naming` = object naming), Condition (congruent vs incongruent; fillers, if present, dropped), RT (ms), Errors.
- Exclusions, as in the card: (1) drop trials with `Errors == 1`; (2) per participant, on error-free experimental trials, drop trials with RT more than 3 SD above or below that participant's mean (mean/SD computed across both congruency conditions of that participant's error-free experimental trials). Also drop missing/zero RTs (no response) if any remain.
- Primary test: two-sided paired t-test on per-participant mean RT, congruent vs incongruent, object-naming group only (n = 12, df = 11). Effect size dz = t/sqrt(n), with 95% CI (noncentral-t interval), and mean difference with 95% CI.
- Claim holds if congruent mean RT < incongruent mean RT with p < .05 (two-sided). Does not hold if p >= .05 or the difference goes the other way. "Cannot tell" only if data are unusable.
- Checks (not primary): same test on given `d02.sav` means; colour-naming group (claim predicts no effect); exclusion variants (no SD trim, 2.5 SD); Wilcoxon signed-rank.

## Commands
1. `cat PROMPT.md; cat papers/S10/card.md; cat papers/S10/data/MANIFEST.json` - read brief and card.
2. `.venv/bin/python -I -c "...pyreadstat.read_sav..."` - inspected d02/d03/d06: d06 has 1920 trials = 24 subjects x 80 experimental items (no fillers in the file), 52 error trials.
3. `.venv/bin/python -I -c "..."` - listed RT <= 100 and > 1500: every negative/-10 RT is flagged Errors == 1, so rule (1) removes them; no extra exclusion needed. Subject IDs are 01-24 except 03 absent and 53 present (noted; treated as a valid subject ID).
4. Wrote `papers/S10/report/analysis.py`; `.venv/bin/python -I papers/S10/report/analysis.py | tee papers/S10/report/analysis.out` - first run failed (noncentral-t CI root bracket gave NaN at large noncentrality); changed bracket to t +/- 10 with `sed -i ''` and reran. No change to the planned test.
   Result: 47 error + 14 SD-trimmed trials dropped of 960; n = 12; C - I = -12.3 ms, t(11) = -1.882, p = .0866, dz = -0.54 [-1.14, 0.08]. Re-derived means match d02 exactly.
5. `grep image score/md2pdf.py` - confirmed relative images render.
6. Wrote report.md; `.venv/bin/python -I score/md2pdf.py papers/S10/report/report.md papers/S10/report/report.pdf` (rendered by chrome; also left report.html).
7. Wrote conclusion.json last. holds = "no" (primary p = .087 > .05, per the pre-stated criterion). No change of plan. End ~17:01, about 2 minutes of wall time.
