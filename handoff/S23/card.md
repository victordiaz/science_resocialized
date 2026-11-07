**Claim (hypothesis).** Averaging two estimates of the same quantity given by one person, the second given in a later session, is more accurate than that person's first estimate alone. Direction: the mean squared error of the average of guess 1 and guess 2 is lower than the mean squared error of guess 1. The key test uses the delayed condition only.

**Design.** Within-subjects comparison in the delayed condition: participants answer eight percentage-estimation trivia questions online (e.g. "What percent of the world's airports are in the United States?") in session 1, and answer the same eight questions again, unannounced, in session 2 about three weeks later. A separate immediate condition (both guesses in one sitting) exists in the data and is not part of the key test.

**Measures.** Answers `q1`..`q8` from each session (session 1 is `d04.txt`, session 2 is `d05.txt`; merged on `student_number_simple`; `d06.txt` is the immediate condition and is not part of this test). True values: 6.3, 43.3, 32.3, 13.4, 53.6, 54.8, 26.4, 22.4. Per participant: MSE of guess 1 = mean over the 8 questions of (guess1 - truth)^2; MSE of the average = mean over the 8 questions of ((guess1 + guess2)/2 - truth)^2.

**Sample.** Undergraduate students who took part in both delayed sessions; 174 matched participants before exclusions, 140 after (125 women, 15 men, mean age 22.0, SD 3.1).

**Exclusions.** A participant is excluded if, in either session, the browser window was defocused while answering any question (any `defocus_q*` = 1), if any of the 16 answers is missing, or if the participant admitted looking up answers (session-2 `peaking` not equal to "Nee").

**Test.** Paired t-test of MSE(guess 1) vs MSE(average of the two guesses), df = n - 1; the replication's analysis plan predicts MSE(guess 1) > MSE(average). Effect size d_z = t / sqrt(n). Not the key test: guess 2 vs the average, or the immediate condition.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.txt` (text, 35 KB): 231 rows 32 columns tab-separated, NaN for missing
- `d05.txt` (text, 21 KB): 171 rows 29 columns carries 'peaking' exclusion column
- `d06.txt` (text, 95 KB): 484 rows other condition, not used by key test
<!-- files:end -->
