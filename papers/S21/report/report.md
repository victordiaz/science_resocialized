# S21 — Stimulus quality x word frequency on ex-Gaussian mu

**Question.** In lexical decision with pseudohomophone nonwords, is the frequency effect (low- minus high-frequency) on the ex-Gaussian mu of correct word RTs larger for degraded than for clear words?

**Data and sample.** Replication file `d07.csv`: 71 participants, 22,481 trials. The file already contains only correct trials with RTs between 200 and 3,000 ms (all accuracy codes = 1, RT range 203–2,998 ms), so the error and 200/3,000 ms exclusions were applied before the file was shared; how many trials they removed cannot be recovered from it. I then applied the 2.5-SD trim as specified (per participant, separately for word and nonword trials): it removed 598 trials (359 word, 239 nonword). Analysed: 11,457 correct word trials, 71 participants (none excluded), 18–50 trials per participant x condition cell (median 41). Frequency coding: `ldtfreq` level 1 has more correct trials from an equal number of items (higher accuracy) and was taken as high frequency; it is also faster overall, consistent with that.

**Measure.** For each participant x condition, an ex-Gaussian was fitted to the RTs by quantile maximum likelihood (my own implementation: likelihood of the counts between the 10th, 20th, ... 90th percentiles of the data; QMPE v2.18 itself was not available). mu is the analysed value. All 284 fits converged.

**Primary test (pre-specified).** 2 (quality) x 2 (frequency) repeated-measures ANOVA on mu; key term the quality x frequency interaction, F(1, 70); partial eta^2 = SS_int / (SS_int + SS_error).

| mu (ms), mean over 71 participants | High frequency | Low frequency | Frequency effect |
|---|---|---|---|
| Clear | 560.8 | 578.5 | 17.7 |
| Degraded | 679.2 | 783.8 | 104.6 |

**Result.** Interaction: F(1, 70) = 11.41, p = .0012; partial eta^2 = .140, 95% CI [.024, .289]. The interaction contrast (LF−HF)degraded − (LF−HF)clear = +86.9 ms, 95% CI [35.6, 138.2], in the predicted direction. Main effects: quality F(1, 70) = 22.07, p < .001 (degraded slower by 162 ms on mu); frequency F(1, 70) = 21.90, p < .001 (61 ms).

**Robustness.** (a) mu by continuous maximum likelihood: interaction +98.4 ms, F(1, 70) = 13.17, p = .0005, partial eta^2 = .158. (b) Without the 2.5-SD trim, QMLE mu: +84.3 ms, F(1, 70) = 9.83, p = .0025, partial eta^2 = .123. (c) Not the key test: on mean RT the interaction is absent and slightly in the other direction, −13.3 ms [−37.0, 10.3], F(1, 70) = 1.26, p = .26 — the larger degraded-word frequency effect appears in the leading edge (mu), not in the means.

**Caveats.** Fits use about 40 trials per cell, so individual mu estimates are noisy (wide participant-level spread in the quality effect); my QMLE is not QMPE v2.18 and its quantile set may differ, but two estimators and both trimming choices agree. The upstream exclusions could not be audited.

**Conclusion.** The claim holds on this data: the frequency effect on ex-Gaussian mu is larger for degraded than for clear words (interaction F(1, 70) = 11.41, p = .0012, partial eta^2 = .14).

Files: `analysis.py` (run from the S21 directory; `--no-trim` for robustness b), `analysis.out`, `analysis_notrim.out`, `cell_estimates.csv`, `log.md`.
