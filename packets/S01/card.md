**Claim (hypothesis).** Physical cleansing after experiencing disgust makes moral judgments less severe: people who wash their hands after watching a disgusting film clip rate morally questionable acts as less wrong than people who do not wash. The predicted effect is a lower mean wrongness rating, across six moral vignettes, in the hand-washing group than in the no-washing group.

**Design.** Between-participants, two conditions (hand-washing vs no hand-washing), random assignment; individual lab sessions.

**Conditions and procedure.** All participants first watch the same disgust-inducing film clip (a toilet scene from a commercial feature film). Hand-washing condition: participants are then asked to wash their hands (at a sink next to the testing room). Control: no prompt to wash. Everyone then rates six moral vignettes (a dog eaten after being run over, a dilemma about diverting a runaway trolley so that it kills one person instead of five, keeping money from a found wallet, cannibalism after a plane crash, lying on a résumé, sexual behaviour involving a kitten), then reports the emotions felt after the clip and completes a questionnaire on how closely they attend to their own bodily sensations.

**Measure.** Wrongness of each vignette on a 7-point scale from 1 (nothing wrong at all) to 7 (extremely wrong); the dependent variable is the mean of the six (`mean_vignettes`; items `Dog`, `Trolley`, `Wallet`, `Plane`, `Resume`, `Kitten`). Group: `Condition` (0/1; the codebook labels 0 = no hand-washing, 1 = hand-washing). File: `d12.sav` (the second study's data; a first study's file is posted alongside and is not this test).

**Sample and exclusions.** Undergraduates at a large US public university, course credit; planned N ≥ 104 (power analysis), 132 collected. Pre-registered exclusions: participants who answer yes to "All of my answers are made up" (`Madeup_dummy` = 1) and participants with an experimenter error (`Exp_Error` = 1). Suspicion filters exist in the file (`Final_Rating`) but are not applied in the key test. After exclusions: 126.

**The test.** One-way between-subjects ANOVA (equivalently a two-sample Student t-test, equal variances) of `mean_vignettes` by `Condition`, F with df (1, N − 2); effect size Cohen's d with pooled SD, signed hand-washing minus no hand-washing (the claim predicts a negative d). Not the key test: the six single-vignette ANOVAs, the emotion-rating ANOVA, and the models testing moderation by the bodily-sensations questionnaire.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d11.sav` (SPSS, 527 KB)
- `d12.sav` (SPSS, 218 KB)
<!-- files:end -->
