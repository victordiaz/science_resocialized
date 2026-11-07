# Log, S18

Recognition: [withheld from the bundle; the full line is in the record]

## Plan (written before opening the data)

- Data: `papers/S18/data/d07.sav`, the only file.
- Variables: condition (achievement words vs control); learning score = mean RT of the two random test blocks minus mean RT of the fixed-sequence test block (ms). If the file holds a precomputed learning score I will use it and check it against one recomputed from block RTs if block RTs are present.
- Exclusions: keep rows with Include1 == "Include for analyses" (the card says this flag already applies the awareness, technical-failure and 4-SD rules and the first-79-per-condition cut). I expect 79 + 79 = 158. If the count differs, I report it and still use the flag.
- Primary test: Student independent-samples t-test (equal variances), two-sided, achievement minus control, on the learning score. Report t, df, p, Cohen's d (pooled SD) with a 95% CI (noncentral-t-free normal approximation: SE_d = sqrt(n1+n2)/(n1 n2) + d^2/(2(n1+n2)))).
- Claim holds if: d > 0 and p < .05 two-sided. Does not hold if p >= .05 (or effect in the wrong direction); I will add the CI to say whether the data can rule out an effect of the size usually claimed in this literature (no: I will simply say whether the CI is narrow enough to exclude d = 0.5).
- Robustness (not the basis of the conclusion): Welch t-test; Mann-Whitney; all participants without the Include1 filter if possible; one-sample test that learning > 0 overall (manipulation check that sequence learning occurred).

## Commands

1. `cat PROMPT.md; ls -R papers/S18 score; cat papers/S18/card.md papers/S18/data/MANIFEST.json`
2. Inspected `d07.sav` variables and labels with pyreadstat (206 rows, 80 columns).
3. Tabulated Condition, Include, Include1, filter_$, exclusion reasons.

Observations that refine (not change) the plan:
- Include1 has no value labels; it is coded 0/1 and the SPSS filter `filter_$` ("Include1=0 (FILTER)") equals 1 exactly when Include1 == 0. Include1 == 0 gives 79 achievement (Condition 1) + 79 control (Condition 2) = 158, matching the card. So "Include for analyses" = Include1 == 0. Two cases moved from Include to Include1 for being > 4 SD from the learning mean.
- The file's `Learning` variable = FSMean - RB12Mean (negative = learning), the opposite sign of the card's definition. I recompute learning = (R1Mean + R2Mean)/2 - FSMean, as the card defines it (verified RB12Mean = (R1Mean+R2Mean)/2 and Learning = -(RB12Mean - FSMean) exactly).
4. Wrote `analysis.py`; ran `.venv/bin/python -I papers/S18/report/analysis.py > papers/S18/report/analysis.out`. Failed only at the figure (matplotlib renamed `labels` to `tick_labels` in boxplot); fixed with sed and reran. All statistics unchanged between runs.
   Excluded 48 of 206: 13 flagged Excludetechknowledge (technical failure or awareness), 2 for > 4 SD learning score, 33 beyond the first 79 per condition (no reason given; Excludetechknowledge = 0).
   Primary: Student t(156) = -1.32, p = .189, d = -0.21 [-0.52, 0.10]; achievement mean 22.3 ms vs control 33.1 ms (wrong direction). Learning itself is robust (t(157) = 6.72).
5. Wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S18/report/report.md papers/S18/report/report.pdf`; wrote conclusion.json last.
No change of plan.
