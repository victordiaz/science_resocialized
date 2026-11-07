**Claim (hypothesis tested).** Among low-prejudice people, those who say their motivation to respond without prejudice comes from personal values but not from social pressure (high internal, low external) exert better response control than those who report both (high internal, high external), and this advantage is specific to control when race is involved: it appears on the gun/tool task that follows a flashed face and not on the race-neutral arrow-type task. In the analysis this is the **Group × Task interaction** on the control estimate: the group difference should be larger (favouring high-internal/low-external) on the gun/tool task (`Weapons` in the data) than on the race-neutral task (`Flankers` in the data).

**Design.** 2 (Group: high internal/low external vs high internal/high external; between subjects) × 2 (Task: gun/tool classification vs race-neutral central-target classification; within subjects).

**Conditions.** Group comes from two self-report questionnaires: one asks how far the person's wish to respond without prejudice comes from their own values (internal), the other how far it comes from wanting to avoid others' disapproval (external). All participants are high on the internal questionnaire and are split by the external one. Gun/tool task: a face (Black or White) is flashed, then a picture of a gun or a hand tool, which the participant classifies by key press under time pressure; errors in the stereotyped direction (a tool called a gun after a Black face) count as failed control. Race-neutral task: the participant classifies a central target item while the items flanking it call for either the same or the opposite response.

**Measures.** One estimate of controlled responding per participant per measure (the `PD` column), computed from accuracy as the probability of a correct answer on trials where the automatic tendency and the correct answer agree minus the probability of an error on trials where they conflict: on the gun/tool task one estimate for Black-face trials and one for White-face trials; on the race-neutral task one estimate. The long data file therefore has three rows per participant (Weapons-Black, Weapons-White, Flankers).

**Sample.** 75 participants (46 high internal/low external, 29 high internal/high external).

**Exclusions.** None at this stage: every participant in the PD file enters the test.

**Test to run.** Repeated-measures ANOVA with error strata, in R notation `aov(PD ~ Group * Task + Error(ID/Task))`, fitted on the three-rows-per-participant file (the two Weapons rows both stay in); report the **Group × Task interaction** F, df and p from the ID:Task stratum, and partial eta squared = SS_interaction / (SS_interaction + SS_residual of that stratum). (Averaging the two Weapons rows per participant first and running a 2 × 2 mixed ANOVA tests the same contrast.) Not the Group main effect in the between-subjects stratum.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.csv` (CSV, 736 KB)
- `d04.csv` (CSV, 23 KB)
- `d07.csv` (CSV, 991 KB)
- `d08.csv` (CSV, 2.0 MB)
- `d09.csv` (CSV, 9 KB)
- `d11.csv` (CSV, 15 KB): 225 rows 8 columns Derived file: process-dissociation (PD) control estimates per participant per task; Weapons has 2 rows per ID (TrialType), Flankers 1
- `d12.csv` (CSV, 7 KB)
- `d13.csv` (CSV, 24 KB)
<!-- files:end -->
