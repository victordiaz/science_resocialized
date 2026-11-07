**Claim (hypothesis).** People who, after being told they failed a math test, read statements that more practice would have made them do better ("if I had practised more, I would have done better") perform **worse** on a following surprise math test than people who read neutral statements. Directional: control > more-practice statements, on the proportion of attempted items answered correctly.

**Design.** Between subjects, two conditions, random assignment. All participants: a self-esteem questionnaire, an insufficient 2-minute practice session, a first math exam, then failure feedback (told 11 of 20 correct, 35th percentile). Then they read 10 statements said to come from previous participants, each shown 30 s in random order:
- **More-practice statements (Cond 1):** 5 statements that more practice would have improved performance, plus 5 neutral statements.
- **Control (Cond 2):** 10 neutral statements.
Then: instructions for a surprise timed second math exam said to be affected by concentration and stress, a 32-item stress questionnaire, and the second exam (4 minutes).

**Measure.** On the second exam, items attempted and items correct in 4 minutes; the DV is **proportion correct = items correct / items attempted** per participant. In the data file: `Cond` (1 = more-practice statements, 2 = control), `Attempted`, `Correct`.

**Sample.** 61 undergraduate psychology students taking part for course credit.

**Exclusions.** None.

**Test.** Independent-samples Student t-test (equal variances assumed) on proportion correct, **one-tailed**, H1: control mean > more-practice-statements mean; df = N − 2. Report t, df, one-tailed p.

**Not the key test.** The same comparison on items attempted or on items correct (counts) are exploratory side tests.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.csv` (CSV, 7 KB): 61 rows 32 columns Subject, Cond (1=32, 2=29), Attempted, Correct, percent, Date, Time, SMT1-25
<!-- files:end -->
