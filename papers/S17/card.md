**Claim (hypothesis).** Both young children and adults locate a picture of a snake among pictures of caterpillars faster than the reverse: people locate **a snake among caterpillars faster than a caterpillar among snakes**. Directional: mean latency is lower in the snake-target condition. The key effect is the **main effect of target stimulus** (not its interaction with age).

**Design.** 2 × 2 between subjects: target stimulus (snake target among 8 caterpillar distractors / caterpillar target among 8 snake distractors) × age group (children / adults, each adult being a child participant's parent). Each participant does 24 test trials on a touch screen (a tablet in a frame), after 7 practice trials; each trial shows a 3 × 3 matrix of photographs with one target and eight distractors, and the participant touches the target as fast as possible, starting with hands on handprints. A smiley face between trials is pressed by the experimenter once the participant looks at it. The child is tested first, the parent afterwards, without being told the hypothesis or watching the child. Picture order is one of two fixed orders (1–24 or 24–1).

**Measure.** Latency in ms from matrix onset to the touch, per trial; only trials where the correct target was touched count (incorrect touches are set to missing; when a tap registered twice, the first time is kept). The DV is each participant's mean latency over their valid trials (`average` in the analysis file; trial columns `M1`–`M24`).

**Sample.** 48 participants after exclusions: 25 children aged 3–5 years (12 snake, 13 caterpillar) and 23 parents (11 snake, 12 caterpillar), recruited through childcare centres.

**Exclusions.** From 56 tested: children who touched the wrong picture on more than half of the trials (5 removed), and outliers with an average z score above 3 (2 children, 1 adult), as described by the replication team. A child's snake experience was recorded but is dropped from the model.

**Test.** Two-way between-subjects ANOVA on mean latency, age group × target stimulus, type-III sums of squares with sum-to-zero (effect) coding. Key term: **target stimulus main effect**, F with df (1, 44), two-tailed p, and partial eta squared = SS_effect / (SS_effect + SS_error).

**Not the key test.** The age main effect and the age × stimulus interaction come out of the same model; the interaction is not the claim.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.xls` (Excel (old), 70 KB): raw data before screening; not opened
- `d05.sav` (SPSS, 36 KB): 48 rows 48 columns one row per participant; cells children/snakes 12, children/caterpillars 13, parent/snakes 11, parent/caterpillars 12; average has no NA
<!-- files:end -->
