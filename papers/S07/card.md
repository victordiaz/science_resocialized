**Claim (hypothesis).** In a sequential risk-taking game, the correlation between a person's risk taking in the game and their real-world drug use is predicted to be **larger in the sunny conditions (the pond's contents are visible) than in the cloudy conditions (they are hidden)**: under cloudy weather the participant has to learn the odds while playing, and that learning process is predicted to weaken the game's power to pick out people who use more drugs. The test is the contrast sunny minus cloudy over the four correlations; the predicted sign is positive.

**Design.** Within subjects, 2 × 2: release rule (Keep: each caught red fish is kept, so the pond empties and the chance of the blue fish rises with every cast / Release: each caught fish is thrown back, so the chance stays constant) × weather (Sunny: the fish in the pond are visible; Cloudy: they are not). Each participant plays rounds in all four conditions (KS, KC, RS, RC). On each round the participant casts repeatedly; each cast earns money, but catching the one blue fish ends the round and loses the round's earnings. The participant can stop at any time and bank the earnings.

**Measures.** Adjusted casting score per condition: the mean number of casts on rounds in which the participant chose to stop (rounds that ended with the blue fish are left out). Drug use (the weighted polydrug score): for each of 11 drug classes, the participant rates how often they used it at the time in life they used it most (never, once, monthly or less, 2–4 times a month, 2–3 times a week, 4+ times a week); the score is the sum of (rank − 1) across classes.

**Sample.** Adults recruited for a laboratory session; 161 completed the game, 153 have a drug-use score.

**Exclusions.** Participants with no drug-use score (did not complete the drug questionnaire) are dropped. Duplicate program entries are removed during cleaning and one participant whose session restarted is dropped. All rounds in the trial file enter the per-condition means as the cleaning script computes them (the file also flags practice rounds; the cleaning script does not filter on that flag).

**Test.** Pearson correlation of polydrug with each of KS, KC, RS, RC; Fisher z transform; Meng, Rosenthal & Rubin (1992) test for a contrast among correlated correlations with weights (+1, −1, +1, −1) on (KS, KC, RS, RC), i.e. sunny minus cloudy, using the median inter-correlation of the four casting scores as r_x. Statistic: Z, two-sided p. N = number of participants with all five values.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.zip` (zip archive, 2.5 MB)
- `d05.xlsx` (Excel, 49 KB)
- `d08.dta` (Stata, 74.8 MB)
- `d09.dta` (Stata, 3 KB)
- `d10.dta` (Stata, 8 KB)
- `d11.dta` (Stata, 279 KB)
<!-- files:end -->
