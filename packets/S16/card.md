**Claim (hypothesis tested).** After reading a word for an object with a typical location (e.g., hat: up; boot: down), people identify a briefly shown letter worse when it appears at that object's typical location than at the opposite location, because reading the word engages seeing at that location. On the error-rate measure: **more identification errors for targets at the typical location than at the atypical location.**

**Design.** One-factor within-subjects design: target location relative to the cue word's typical location (typical vs atypical).

**Conditions.** Each trial: fixation cross 250 ms, a context word 500 ms (e.g., cowboy), then a cue word 250 ms denoting an upper-location (hat) or lower-location (boot) part, a 50 ms delay, then a target letter (X or O) at the top or bottom of the screen; the participant presses a key for X or O as fast and accurately as possible. Cue (upper, lower), target location (top, bottom) and letter are fully crossed and balanced; typical = top target after an upper cue or bottom target after a lower cue. Stimuli were 30 context words each paired with an upper and a lower cue (60 experimental trials), plus filler trials with non-spatial cues and 10 practice trials; the data file holds the 60 experimental trials per participant.

**Measures.** Per participant and condition, the error rate = proportion of experimental trials with an incorrect identification (use the variable resp_corr: 1 correct, 0 incorrect; typisch: 1 typical, 2 atypical).

**Sample.** 22 participants, 60 experimental trials each (1,320 trials).

**Exclusions.** No participants excluded. For error rates, all experimental trials count. (For the separate response-time analysis, incorrect trials and RTs above 1,000 ms are dropped; that rule does not apply to this test.)

**Test to run.** One-way repeated-measures ANOVA by subjects (F1) on per-participant error rates, typical vs atypical; report F(1, n − 1), p, and partial eta squared = SS_location / (SS_location + SS_error). Not the response-time ANOVA and not the by-items (F2) analysis.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.sav` (SPSS, 93 KB): 1320 rows 12 columns Subj, Trial, conditio, item, RT, Correct (string "True "/"False"), resp_corr (factor), typisch
<!-- files:end -->
