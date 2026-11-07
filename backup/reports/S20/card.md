**Claim.** Seeing two digits makes their sum come to mind without being asked for, and this happens more when the digits are preceded by a pair of words that relate to each other the way addends do. The measure of the sum coming to mind is how much slower people are to reject a digit target equal to the sum of the cue digits (e.g. 8 for 5 3) than a neutral digit (e.g. 9): the sum − neutral slowing. The prediction is that this slowing is larger after word pairs from one category (AC, e.g. tulips–daisies) than after pairs of unrelated words (MU, e.g. hens–radios): (sum − neutral) for AC > (sum − neutral) for MU.

**Design.** Within-subjects. 160 trials per participant, made up of word triplets (four conditions: AC word pair with matching or non-matching target, MU word pair with matching or non-matching target) crossed with digit triplets (sum, neutral, cue control, target control) and target order (digit first or word first), five trials per cell, in an individually randomised order. Participants decide whether a target matches the cue items.

**Analysed trials.** Only trials where a non-matching digit target came first, with a sum or neutral target: 40 trials, half after AC word pairs and half after MU word pairs. This gives a 2 (word pair: AC vs MU) × 2 (digit target: sum vs neutral) within-subjects design.

**Measure.** Mean latency of correct responses (ms) per participant in each of the four cells (`avg_time_sum_ac`, `avg_time_neutral_ac`, `avg_time_sum_mu`, `avg_time_neutral_mu` in `d02.sav`).

**Sample.** 50 university students fluent in English were tested. One was excluded for failing to respond correctly on 90% of trials, leaving 49. The file holds those 49 rows; rows 50–320 are empty.

**Test.** 2 × 2 repeated-measures ANOVA on the four cell means. The key term is the word pair × target interaction, F(1, 48), equal to the square of the one-sample t of the double difference (sum_AC − neutral_AC) − (sum_MU − neutral_MU). The replication reports it with its error mean square (MSE).

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.sav` (SPSS, 14 KB): 320 rows 21 columns rows 50-320 are empty; 49 participants with data
- `d04.sav` (SPSS, 14 KB): 320 rows 21 columns rows 50-320 are empty; 49 participants with data
<!-- files:end -->
