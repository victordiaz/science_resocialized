**Claim (hypothesis).** When two cued letters appear in one rapid stream and the second follows the first by a short interval, which item gets reported for the second cued letter changes in three separable ways: fewer reports come from around its position (suppressed), the reports are centred later in the stream (delayed), and they are spread over more positions (diffused); these three changes follow different time courses across the interval between the two cued letters. Predicted: a significant three-way interaction of measure (efficacy, latency, precision) x target (first, second) x SOA (1 to 10 items).

**Design.** Rapid serial visual presentation of all 26 letters in random order, 12 items/s (25 ms letter + 58.3 ms blank), white on black. Two letters on each trial are cued by a ring shown with the letter; the first cue falls at stream position 6 to 10, and the second follows after 1 to 10 items (83 to 833 ms). After each trial participants type the two cued letters, first then second; small cash bonus per correct letter. 2 practice trials, then 4 blocks of 100 trials (2 of each of 50 position x SOA combinations per block). Fully within subjects.

**Measures.** From the serial positions of the reported letters, relative to each target, within a seven-item window (three before to three after): efficacy = mean probability of reporting an item from the window; latency = centre of mass of reports in the window; precision = variance of that centre of mass. One value per participant x measure (3) x target (2) x SOA (10) = 60 values per participant, 720 in all. In the shared spreadsheet the factor columns are headed 'efficacy' (= measure, 3 levels), 'latency' (= target, 2 levels) and 'precision' (= SOA, 10 levels); the value column is 'temporal selection'.

**Sample.** 12 adults aged 18 to 27, paid, university participant pool. Participants unable to do the task in practice were to be replaced.

**Exclusions.** Practice trials discarded; no other exclusions.

**Test.** Full-factorial fixed-effects ANOVA on the 720 values with factors measure x target x SOA, treating every value as an independent observation (participant not in the model; equivalent to Matlab `anovan(z, {measure target SOA}, 'model', 'full')`). The term of interest is the **three-way interaction measure x target x SOA**, F(18, 660), with partial eta squared. Not a repeated-measures ANOVA with participant as a factor, which gives a different F.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.csv` (CSV, 14 KB)
<!-- files:end -->
