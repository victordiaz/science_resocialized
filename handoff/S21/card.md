**Claim (hypothesis).** When people decide whether a letter string is a real word, and the nonwords are strings that sound like real words when read aloud (e.g. BRANE), stimulus quality and word frequency interact on the leading edge of the response-time distribution: the slowing for low-frequency words relative to high-frequency words (low-frequency minus high-frequency) is larger for degraded words than for clear words. The key term is the quality x frequency interaction on the ex-Gaussian parameter mu, in that direction.

**Design.** 2 (stimulus quality: clear vs degraded) x 2 (word frequency: high vs low) fully within participants. Each participant sees letter strings one at a time and presses one key for "word" and another for "nonword": 200 words (100 high-frequency, 100 low-frequency) and 200 sound-alike nonwords, in five blocks of 80 trials after 20 practice trials, clear and degraded trials randomly intermixed. Degraded strings alternate rapidly with a random symbol mask of the same length (mask 14 ms, string 28 ms, repeated until response). The item-to-quality assignment is counterbalanced across participants.

**Measures.** Response time on correct word trials. For each participant and each of the four word conditions, an ex-Gaussian distribution (a normal distribution plus an exponential tail) is fitted to the response times, and mu, the mean of its normal part, is the analysed value; the fit is by quantile maximum likelihood (QMPE v2.18). The analysed file holds one row per participant and four columns of mu: `Highfrequencyclear`, `Lowfrequencyclear`, `Highfrequencydegraded`, `Lowfrequencydegraded`.

**Sample.** 71 psychology undergraduates taking part for course credit, normal or corrected-to-normal vision.

**Exclusions.** No participants excluded. Trials removed before mu is estimated: errors; latencies under 200 ms or over 3,000 ms; then latencies more than 2.5 SD from the participant's own mean, the mean and SD computed separately for that participant's word and nonword trials.

**Test.** By-participant 2 x 2 repeated-measures ANOVA on mu; the key statistic is the F for the quality x frequency interaction, df (1, n - 1). Effect size partial eta^2 = SS_interaction / (SS_interaction + SS_error(interaction)). Not the key test: the same ANOVA on mean RTs, or the two main effects.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d07.csv` (CSV, 1.2 MB)
<!-- files:end -->
