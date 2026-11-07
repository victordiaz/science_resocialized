# S27: Does the effect of a conciliatory message on willingness to reconcile depend on role?

**Question.** Do victims become more willing to reconcile after an *empowerment* message (praise of competence) than after an *acceptance* message (affirmation as a moral person), with perpetrators showing the reverse, i.e. a crossover role x message interaction?

**Data and sample.** Independent replication, SPSS file `d05.sav` (146 rows; the CSV twin has the same rows). Design: 2 (role: victim / perpetrator) x 2 (message: acceptance / empowerment), between subjects. No exclusions by rule. Rows missing the after-message willingness score or a condition code were dropped listwise: 5 rows (2 lacked condition codes, and these were among the 5 lacking the outcome), leaving **N = 141**.

**Measure.** `AvgWillingReconcileTime2`, the mean of ten 7-point items after the message (higher = more willing). The stored score equals the mean of the ten stored item columns exactly; Cronbach's alpha = .92 (n = 135 with all items).

**Plan (fixed before analysis, see log.md).** Primary test: between-subjects 2 x 2 ANOVA (Type III SS), role x message interaction, with partial eta squared and a 95% CI. The claim holds only if the interaction has p < .05 **and** the cell means show the predicted signs (victims: empowerment > acceptance; perpetrators: acceptance > empowerment).

## Results

| Role | Message | n | Mean | SD |
|---|---|---|---|---|
| Victim | Acceptance | 33 | 4.08 | 1.35 |
| Victim | Empowerment | 34 | 3.87 | 1.26 |
| Perpetrator | Acceptance | 37 | 4.86 | 1.11 |
| Perpetrator | Empowerment | 37 | 5.11 | 0.83 |

**Primary test: role x message interaction, F(1, 137) = 1.42, p = .235, partial eta squared = .010, 95% CI [.000, .067].**

The pattern also runs the *opposite* way to the prediction: victims were slightly more willing after acceptance than after empowerment (difference -0.21, pooled-error t(137) = -0.77, p = .44, d = -0.17), and perpetrators slightly more willing after empowerment than after acceptance (+0.25, t(137) = 0.93, p = .36, d = 0.25). Neither simple effect is reliable.

Other terms: a large main effect of role (perpetrators more willing than victims, F(1, 137) = 27.4, p < .001); no main effect of message (F(1, 137) = 0.01, p = .93).

**Robustness.** Type II SS gives the same interaction (F = 1.42, p = .235). A heteroskedasticity-robust (HC3) test of the interaction coefficient: z = -1.16, p = .25. Levene's test: p = .10. Mann-Whitney tests of message within each role: p = .47 (victims), p = .45 (perpetrators). Adjusting for before-message willingness (ANCOVA): interaction F(1, 136) = 0.15, p = .70. Gains from before to after the message were nearly identical across messages within each role (victims +0.59 vs +0.65; perpetrators +0.94 vs +0.98).

## Conclusion

**The claim does not hold on this data:** the role x message interaction is small and not significant (F(1, 137) = 1.42, p = .235, partial eta squared = .010), and the cell means point in the direction opposite to the predicted crossover.

*Limits.* With about 35 per cell the study can detect only moderate interactions (the 95% CI reaches partial eta squared = .067), so a small effect in the predicted direction cannot be ruled out; but the point estimate is in the wrong direction. Files: `analysis.py` produces every number above; output in `analysis.out`.
