# S12 log

Recognition: the design looks like the implicit/explicit attitude-generalisation paradigm (Ranganath & Nosek, 2008) and a replication of it; I do not recall the replication's result and carry on from the data only.

Start: 2026-11-07 16:59 CET.

## Plan (written before any analysis)

- Data: `papers/S12/data/d07.csv` (4,267 rows).
- Variables: outcome `imppref` (response-speed preference, positive = preference for the positive individual / its group member); group `rateorig` (1 = rated original pair, 0 = rated new pair).
- Exclusions, applied in the card's order, with counts at each step:
  1. `exppref` NA (skipped questionnaire items);
  2. `d` NA (no sorting-task score);
  3. `fastpct10 == 1` (>10% of trials < 300 ms);
  4. `alltrials != 200`.
  Also drop rows with `rateorig` NA if any remain (cannot be assigned to a group); reported separately.
- Primary test: Welch two-sample t-test of `imppref`, new-pair (rateorig 0) vs original-pair (rateorig 1), two-sided, alpha .05. Effect size Cohen's d with pooled SD, 95% CI (noncentral-t-free normal approximation, Hedges & Olkin SE).
- Decision rule: the claim predicts *no difference*. A null p is not evidence of equivalence, so I state the decision as:
  - Claim holds if the Welch test is not significant (p >= .05) AND the 95% CI of d lies within ±0.2 (a smallest effect of interest I fix now; equivalently, a TOST at ±0.2 is significant). With ~3,600 people this is well powered.
  - Claim does not hold if p < .05 (the new-pair preference differs from the original-pair preference), unless the difference is trivially small (|d| CI entirely within ±0.2), in which case I report it as significant but small and judge the practical claim of "as large" by the equivalence bound — I will report both and treat the significance test as primary.
  - Cannot tell if p >= .05 but the CI extends beyond ±0.2.
- Checks (not primary): group means vs 0 (one-sample t), Student t, Mann-Whitney, the self-report `exppref` difference (companion prediction), randomisation balance in group sizes.

## Commands run

1. `cat PROMPT.md; ls -R papers score` — read brief, listed files.
2. `cat papers/S12/card.md papers/S12/data/MANIFEST.json; head -5 papers/S12/data/d07.csv; wc -l` — card, manifest, data header (4,267 rows).
3. Wrote this plan (above) before any analysis.
4. `.venv/bin/python -I papers/S12/report/analysis.py` — first run: exclusions give N = 3,597 (matches card); Welch t(3511.1) = −6.31, p = 3.2e-10, d = −0.21 [−0.28, −0.15].
5. `.venv/bin/python -I -c "import matplotlib"`; `binomtest(1959, 3597)` — checked plotting is available; group sizes unbalanced (p = 9e-8).
6. Appended an assignment-balance check and the figure to analysis.py; `.venv/bin/python -I papers/S12/report/analysis.py > papers/S12/report/analysis.out 2>&1`.
7. `grep -i image score/md2pdf.py` — confirmed relative images render.
8. Wrote report.md; `.venv/bin/python -I score/md2pdf.py papers/S12/report/report.md papers/S12/report/report.pdf` (the renderer also left report.html).
9. Wrote conclusion.json.

## Changes of plan

None to the primary test. I added two checks after seeing the data: the assignment-balance check and the exclusion rate by group. I added them because the group sizes were visibly unequal. They are descriptive and do not change the conclusion. The decision rule as written applies directly: p < .05 and the CI of d (−0.28 to −0.15) lies mostly outside ±0.2, so the claim does not hold.

End: about 17:02 CET (about 3 minutes of wall time).
