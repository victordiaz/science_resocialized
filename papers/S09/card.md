**Claim (hypothesis tested).** When two targets appear close together in a rapid stream, bilingual adults miss the second one more often than monolingual adults: when a second target (T2) follows a correctly identified first target (T1) at a short lag, bilinguals report T2 correctly less often than monolinguals, most of all at lag 3 (T2 two items after T1). In the analysis this is the **Group × Lag interaction** on T2|T1 accuracy: the two groups' lag curves should differ in shape, with the bilingual curve lower at the short lags.

**Design.** 2 (Group: monolingual vs bilingual; between subjects) × 4 (Lag: 1, 3, 5, 8; within subjects). On each trial participants watched a stream of items shown one at a time, in quick succession, at the same place on the screen; two items in the stream were targets, the first target (T1) and the second target (T2), and at the end of the stream the participant reported both. T2 appeared 1, 3, 5 or 8 positions after T1.

**Conditions.** Group is a pre-existing classification from a language questionnaire: monolingual English speakers vs speakers fluent in English plus one other language. Lag is manipulated within subjects across trials.

**Measures.** For each participant and each lag, the proportion of trials on which T2 was reported correctly, counting only trials on which T1 was reported correctly (T2|T1). These four proportions are the per-participant cells of the analysis (computed from the trial files by the replication team and stored as one column per lag).

**Sample.** 32 participants with complete data: 18 monolingual, 14 bilingual.

**Exclusions.** None for this test: all 32 participants in the data file enter the analysis. (A separate, exploratory analysis in the protocol drops the 4 bilinguals who learned their second language after age 12; that analysis is not this test.)

**Test to run.** Mixed-design ANOVA (sums of squares Type III), between factor Group, within factor Lag, dependent variable T2|T1 proportion correct; report the **Group × Lag interaction** F with Greenhouse-Geisser-corrected degrees of freedom and p (sphericity is violated for Lag), and partial eta squared = SS_interaction / (SS_interaction + SS_error). Not the Lag main effect, and not the t-test at lag 3, which the protocol lists separately.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d01.zip` (zip archive, 7.0 MB)
- `d04.sav` (SPSS, 120 KB)
<!-- files:end -->
