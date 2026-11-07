**Claim.** A preference measured by response speed, rather than by self-report, carries over from one individual to other members of his group straight away. Immediately after learning about one mostly-positive and one mostly-negative individual from two different fictional groups, the response-speed preference people show between two *new* members of those groups is as large as the one others show between the two *original* individuals. The prediction for this key test is no difference between the original-pair and new-pair raters on the response-speed measure. (The companion self-report prediction is a difference at the immediate session; it is not the key test here.)

**Design.** Between-participants, run online on a volunteer research website, immediate session only. All participants learn about the original pair (12 positive + 4 negative behaviours vs 12 negative + 4 positive, 3 s each), then meet two new individuals, one from each group, described as evaluatively equivalent. They are then randomly assigned to rate either the original pair (`rateorig == 1`) or the new pair (`rateorig == 0`) on both a self-report questionnaire and a timed sorting task, in random order. In the sorting task, pictures of the two rated individuals and positive and negative words appear one at a time and are sorted with two keys; in one block one individual shares a key with positive words and the other with negative words, and in another block the pairing is reversed. Target sex, picture assignment and which group is positive are counterbalanced.

**Measure.** Response-speed person preference `imppref`: the difference in mean response time between the two key pairings divided by the standard deviation of response times across both (with trials under 400 ms deleted and trials over 10 s excluded), signed so that positive values mean a preference for the positive individual, or for the new individual from the positive individual's group.

**Sample.** Visitors aged 18 or over. 4,267 rows in `d04.csv`; 3,597 analysed.

**Exclusion rules, in order.** Missing self-reported preference (`exppref` NA, i.e. skipped questionnaire items); missing sorting-task score (`d` NA); more than 10% of sorting trials faster than 300 ms (`fastpct10 == 1`); not exactly 200 scored sorting trials (`alltrials != 200`).

**Test.** Welch two-sample t-test of `imppref`, new-pair group vs original-pair group, two-sided. Effect size: Cohen's d using the pooled SD.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.csv` (CSV, 4.1 MB): 4267 rows 122 columns processed per-participant file: exppref, imppref, d, fastpct10, alltrials, rateorig
<!-- files:end -->
