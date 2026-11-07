# S19 — Numerical distance effect on "different" judgements across notations

**Question.** When people judge whether two briefly shown digits (Arabic, Indian, or one of each) have the same numerical value, are correct "different" responses faster for pairs far apart in value (6+ apart) than for pairs close in value (1 apart)?

**Data.** Independent replication, trial-level file of the numerical-value task (`d06.csv`, 32 participants x 264 trials); task order from `d07.csv`.

**Sample and exclusions (fixed in advance, as on the card).** 8,448 trials loaded. Removed: participant 24 (dropped by the replication's coding sheet; 264 trials), filler trials with digits 3–7 (2,232), same-value pairs (1,984), error trials (107), RTs < 200 ms or > 2,500 ms (45). **Analysed: 3,816 trials from 31 participants** (16 numerical-task-first, 15 second); every participant has all 6 cells (at least 12 trials per cell). My per-participant cell means are identical to the replication's own aggregate file (`d36.csv`).

**Test (primary, named before analysis).** 3 (notation: Arabic / Indian / mixed, within) x 2 (numerical difference: small / large, within) x 2 (task order, between) mixed ANOVA on per-participant cell-mean RTs, type III sums of squares; the term tested is the main effect of numerical difference. The claim holds if this effect is significant (alpha = .05) with large-difference RTs lower than small-difference RTs.

**Cell means (ms, mean over 31 participants).**

| Notation | Small difference | Large difference | Large − small |
|---|---|---|---|
| Arabic–Arabic | 780.9 | 735.5 | −45.4 |
| Indian–Indian | 804.2 | 740.6 | −63.6 |
| Mixed | 829.8 | 761.2 | −68.6 |
| All | 804.9 | 745.7 | −59.2 |

**Result.** Main effect of numerical difference: **F(1, 29) = 45.27, MSE = 3,575, p = 2.2 × 10⁻⁷**, partial η² = .61 (90% CI .40 to .72). Large-difference pairs were answered 59.0 ms faster than small-difference pairs (unweighted over task order; 95% CI 41.1 to 77.0 ms); 28 of 31 participants showed the effect. The difference x order interaction was not significant (F(1, 29) = 0.38, p = .54), nor was difference x notation (F(2, 58) = 0.76, p = .47).

**Checks (not the basis of the conclusion).** The effect is present within each notation separately: Arabic −45 ms, t(30) = −2.39, p = .023; Indian −64 ms, t(30) = −4.97, p < .001; mixed −69 ms, t(30) = −6.80, p < .001 — so it holds when the two digits are in different notations. A full R `aov` with sequential sums of squares gives F(1, 29) = 45.59 with the same MSE.

**Conclusion.** The claim holds on this data: correct "different" responses were reliably faster for numerically far than for numerically close digit pairs (F(1, 29) = 45.27, p < .001), including for mixed-notation pairs.

*Files: `analysis.py` produces every number above; output in `analysis.out`; plan and commands in `log.md`.*
