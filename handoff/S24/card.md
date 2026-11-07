**Claim (hypothesis).** When participants study a short list of words and then judge whether a single test word was in that list, the group that studied the long-list version of the task is less accurate than the group that studied the short-list version. The original study predicted the effect for test words that were not in the list; the test below is the list-type main effect pooled over all three test-word types, which is the term the replication's analysis carries.

**Design.** 2 × 3 mixed design. Between subjects: list type, two levels coded `long-short` and `short-long` (the data file's labels; which level counts as "long" is the first word of the label as far as the files show). Within subjects: test-word type, three levels: `correct` (a word from the current list), `intrusion` (a word not in the current list that appeared in an earlier list), `new` (a word not in the current list and never shown). Each trial shows a list of words, then one test word; the participant answers whether the test word was in the current list.

**Measure.** Proportion of correct responses per participant per test-word type, from 8 blocks of trials (one row per participant in the wide file: `subject, listtype, correct, intrusion, new`).

**Sample.** 21 participants, first-year university students (German speakers), 11 in `long-short` and 10 in `short-long`.

**Exclusions.** None applied at the analysis stage: every participant in the wide file enters the test.

**Test.** Mixed ANOVA, type-III sums of squares, DV = proportion correct, between = list type, within = test-word type, subject as the unit. The key term is the **list-type main effect**: F with df (1, 19), its p (two-tailed), and partial eta squared = SS_effect / (SS_effect + SS_error).

**A second plausible test, not the key one.** A one-way comparison of list-type groups on the `new` column alone, which is the narrower reading of the original's claim.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d03.sav` (SPSS, 2 KB)
- `d05.csv` (CSV, 752 KB)
<!-- files:end -->
