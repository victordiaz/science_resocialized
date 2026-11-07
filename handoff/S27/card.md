**Claim (hypothesis).** Whether a conciliatory message raises willingness to reconcile depends on the reader's role in the wrong: people in the wronged role become more willing to reconcile after a message praising their professional competence (empowerment), people in the wrongdoer role after a message affirming them as a good, moral person (acceptance). Predicted pattern for willingness to reconcile after the message: a crossover role x message interaction, victims higher after empowerment than after acceptance, perpetrators higher after acceptance than after empowerment.

**Design.** 2 (role: victim vs perpetrator) x 2 (message: acceptance vs empowerment), both between subjects. Participants read a workplace vignette and imagine being its protagonist, gender-matched to themselves: as perpetrator they are promoted for work done jointly with a colleague; as victim they are demoted after the joint work (in this version, after returning from a pre-planned two-week leave for a wedding). They answer needs and willingness questions, then read a message from the colleague that either praises their professional competence (empowerment) or affirms them as a good, moral person (acceptance), and answer again. Computer survey, groups of up to five, lab setting.

**Measure.** Willingness to reconcile after the message (data column `AvgWillingReconcileTime2`): the mean of ten 7-point items (anger, feelings toward the colleague and the relationship, closeness, desired relationship, damage to the bond, future relationship, future atmosphere, willingness to reconcile, owing amends), three reverse-scored, higher = more willing. Factors: `VictimOrPerpV0P1` (0 victim, 1 perpetrator) and `AcceptOrEmpowerA0E1` (0 acceptance, 1 empowerment).

**Sample.** Undergraduates at a US university, for course credit; 146 rows in the data file.

**Exclusions.** None by rule; cases missing the after-message willingness score or a condition code are dropped listwise, leaving 141.

**Test.** Between-subjects 2 x 2 ANOVA on `AvgWillingReconcileTime2`. The term of interest is the **role x message interaction**, F(1, 137), with partial eta squared. This is not the Time x Role x Message term of the mixed ANOVA that also includes before-message willingness; that term is a different test.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.csv` (CSV, 50 KB): csv twin of the .sav, not opened
- `d05.sav` (SPSS, 75 KB): 146 rows 95 columns one row per participant; 2 rows lack the role/message codes, 5 lack the DV; 141 complete cases; cells 33/35/39/37
<!-- files:end -->
