# S15: Information quantity and choosing confirming vs disconfirming information

## Question
After deciding whether Mr. Miller's contract should be extended, are people more likely to pick a piece of information that confirms their decision when ten pieces are offered (five for, five against) than when two are offered (one for, one against)? The key test is in the control (no focus instruction) condition.

## Data and sample
Independent replication, online volunteers (US citizens), file `d11.csv`: 496 participants across the 2 (options: two / ten) × 3 (focus: control / quality / direction) design. Hypothesis-guessers had already been removed from the posted file. Exclusion applied, as planned: **27** participants who did not answer the information-choice question (blank `decision`), leaving 469. The control-focus cell holds **N = 150** (78 two-option, 72 ten-option). I checked that `decision` equals "confirming" exactly when the chosen piece agrees with the participant's first judgment (469/469 rows).

## Test (named before analysis)
Pearson chi-square test of independence, options × decision, control focus only, no continuity correction, df = 1. Claim holds if p < .05 and a higher share chooses confirming information with ten options than with two.

## Result

| Control focus | Confirming | Disconfirming | % confirming |
|---|---|---|---|
| Two options | 46 | 32 | 59.0% |
| Ten options | 57 | 15 | 79.2% |

**χ²(1, N = 150) = 7.10, p = .0077.** Effect size φ = 0.22 (95% CI 0.06 to 0.37, Fisher-z; bootstrap 0.06 to 0.37), Cohen's d = 0.45 (95% CI 0.12 to 0.78). Difference in proportion confirming (ten − two) = 20.2 points (95% CI 5.8 to 34.6); odds ratio 2.64. The direction is the predicted one.

**Robustness (not the basis of the conclusion).** Fisher exact p = .009; Yates-corrected χ² = 6.19, p = .013. Within quantity (control): at ten options confirming choices clearly exceed 50% (79%, χ²(1) = 24.5, p < .001); at two options 59% chose confirming information, which does not differ from 50% (χ²(1) = 2.51, p = .11), so there is **no** preference for disconfirming information with two options; the quantity effect here is a shift from indifference toward confirmation. Other focus conditions: quality 64.5% vs 66.3% (χ²(1, N = 179) = 0.06, p = .80); direction 51.9% vs 65.6% (χ²(1, N = 140) = 2.64, p = .10). The options × focus × decision three-way log-linear interaction was not significant (LR χ²(2) = 3.50, p = .17). Pooled over focus: 58.8% vs 70.3%, χ²(1, N = 469) = 6.74, p = .009.

## Conclusion
**The claim holds on this data:** in the control condition, people chose decision-consistent information more often with ten options than with two (79% vs 59%, χ²(1) = 7.10, p = .008, φ = 0.22), though the claimed preference for inconsistent information with two options was not observed (59% chose consistent information, n.s. against 50%).
