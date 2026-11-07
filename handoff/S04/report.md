# S04: Statistical learning of colour triplets in a stream of coloured shapes

**Question.** After passively watching a stream of coloured nonsense shapes in which colours recur in fixed triplets (with shape only loosely tied to colour), do people judge real colour-only triplets as more familiar than foil triplets at a rate above chance (50%)?

**Data.** Independent replication, 15 adults (mostly cognitive-science undergraduates, tested in German). Each did 32 two-alternative forced-choice familiarity trials; the 16 "real triplet vs foil" trials are analysed, the 16 "pseudo-triplet vs foil" trials are set aside as the card specifies. The 15 subject files inside the zip archive are byte-identical to the 15 loose .mat files; every participant has exactly 16 real trials with 0/1 responses.

**Exclusions.** None, as pre-specified: N = 15 analysed, 0 excluded. (The replicators' own script also runs a secondary analysis dropping two participants as "explicit learners"; this is reported below only as a sensitivity check.)

**Primary test (fixed before analysis).** Two-sided one-sample t-test of the 15 per-participant proportions of real triplets chosen against 0.5; effect size d = t/√n with a 95% CI from the noncentral t distribution. Criterion: the claim holds if the mean is above 0.5 with p < .05.

## Result

| | value |
|---|---|
| Mean proportion real triplet chosen | 0.700 (SD 0.209), 95% CI [0.584, 0.816] |
| t-test vs 0.5 | **t(14) = 3.71, p = .0023** |
| Effect size | d = 0.96, 95% CI [0.33, 1.56] |
| Participants above / at / below 50% | 10 / 4 / 1 |

Per-participant proportions (16 trials each): .81, .63, .94, .81, 1.00, 1.00, .38, .56, .50, .50, .69, .94, .50, .75, .50.

**Robustness (not the basis of the conclusion).**
- Wilcoxon signed-rank vs 0.5 (four ties at 0.5 dropped): W = 2.5, p = .0066.
- Pooled trials: 168/240 = 70% real chosen (binomial p < .0001; ignores clustering within participant).
- Dropping participants 3 and 5 (the replicators' "explicit learner" exclusion): mean 0.659, t(12) = 2.98, p = .012.
- Pseudo-triplet trials (set aside): mean 0.621, t(14) = 2.36, p = .033. Pseudo-triplets were also preferred over foils; since the card does not say how pseudo-triplets were built, I do not interpret this further, but it suggests participants were sensitive to colour transitions that partly overlap the real triplets.

## Conclusion

**The claim holds on this data:** participants chose the real colour triplet over the foil on 70% of trials, reliably above chance (t(14) = 3.71, p = .002, d = 0.96, 95% CI 0.33 to 1.56), and the result survives a non-parametric test and the removal of the two most likely explicit learners. With only 15 participants the effect size is imprecisely estimated.

*Files:* `analysis.py` produces every number above; `analysis.out` holds its output.
