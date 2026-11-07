# S08 — Do "more practice would have helped" statements lower later math accuracy?

**Question.** After failure feedback on a math test, do people who read statements that more practice would have improved performance answer a *smaller proportion* of attempted items correctly on a surprise second math test than people who read only neutral statements? (Directional: control > more-practice.)

**Data and sample.** One file from the independent replication (`d02.csv`, 61 rows). Condition 1 = more-practice statements (n = 32), condition 2 = control (n = 29). No exclusions were planned and none were needed: no missing values, no participant with zero items attempted, no case with more correct than attempted. **N = 61.** Two participant ids (1 and 55) are reused across 9 rows, but those rows have different session dates, times and scores, so I treated them as separate people (consistent with the stated N of 61).

**Measure.** Proportion correct on the second exam = Correct / Attempted, computed per participant (matches the file's `percent` column to 1e-9).

**Primary test (fixed before analysis).** Independent-samples Student t-test, equal variances, one-tailed, H1: control mean > more-practice mean. Criterion: claim holds if one-tailed p < .05 in the predicted direction.

## Result

| Group | n | Attempted M (SD) | Correct M (SD) | Proportion correct M (SD) |
|---|---|---|---|---|
| More-practice statements | 32 | 11.13 (6.28) | 4.91 (2.67) | 0.466 (0.169) |
| Control | 29 | 10.34 (5.10) | 6.07 (3.47) | 0.584 (0.224) |

- **t(59) = 2.33, one-tailed p = .012** (two-tailed p = .024).
- Mean difference (control − practice) = 0.117, 95% CI [0.016, 0.218].
- **Cohen's d = 0.60, 95% CI [0.08, 1.11]** (noncentral-t interval).

**Robustness (not primary).** Welch t = 2.29, one-tailed p = .013; Mann–Whitney U = 605.5, one-tailed p = .021. Normality is not rejected in either group (Shapiro p = .64, .24); Levene p = .09. Exploratory counts: items attempted did not differ (10.34 vs 11.13, t(59) = −0.53, p = .60); items correct were lower in the practice group, but not significantly (6.07 vs 4.91, t(59) = 1.47, two-tailed p = .15). The difference therefore lies in accuracy, not in how many items people tried.

**Caveats.** The sample is small, so the effect estimate is imprecise: the interval for d runs from near zero (0.08) to large (1.11). The test is one-tailed, as specified; the two-tailed p (.024) would also be below .05.

## Conclusion

**The claim holds on this data:** participants who read more-practice statements answered a smaller proportion of attempted items correctly than controls (t(59) = 2.33, one-tailed p = .012, d = 0.60 [0.08, 1.11]).

*Script: `analysis.py`; output: `analysis.out`; log: `log.md`.*
