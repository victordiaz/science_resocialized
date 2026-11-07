**Claim (hypothesis).** Listing only reasons in favour of an already chosen piece of advice (condition 1) leaves people with less mixed feelings about an unrelated social issue than listing reasons both for and against it (condition 2). Direction: the mixed-feelings index is lower in condition 1 than in condition 2, with a neutral control as the third group. The key test is the omnibus difference among the three conditions.

**Design.** Between-subjects, three conditions (`Condition`): 0 = neutral (participants describe seven things they normally do on a typical day); 1 = reasons in favour only (participants choose an area to write advice on, sexual inexperience or honesty in romantic relationships, then list three reasons why giving that advice could be desirable and easy); 2 = reasons for and against (same choice and the three desirable reasons, plus three reasons why it could be undesirable and difficult). All participants then report their attitude toward making the list of convicted sex offenders available to the general public rather than only to the police.

**Measures.** Three mixed-feelings items about the sex-offender list: `StrongMixed` (-3 to 3), `NotTorn` ("I do not find myself feeling torn between the two sides", -3 to 3, reverse-coded as -NotTorn), `Indecisive` (1 to 7, recoded as Indecisive - 4 to a -3..3 scale). Mixed-feelings index = mean of the three recoded items (higher = more mixed feelings). A participant missing one item gets the mean of the items answered.

**Sample.** College students. 89 rows in the analysis file, 70 after exclusions (about 23-24 per condition).

**Exclusions.** Participants who answered "Yes" to "Have you had experience with sexual offenders, or the list of convicted sex offenders?" are excluded (the file's `Include` column, 0 = excluded, is exactly this rule). No other exclusions.

**Test.** One-way between-subjects ANOVA of the mixed-feelings index on `Condition` (three levels), F with df (2, n - 3). Effect size eta^2 = SS_condition / (SS_condition + SS_error). Not the key test: the pairwise t-test of condition 1 vs 2.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d05.txt` (text, 46 KB): 89 rows 32 columns tab-separated, 3 summary lines above the header; Include column; free-text responses inside
- `d06.tsv` (TSV, 37 KB)
<!-- files:end -->
