**Claim (hypothesis tested).** When a White man makes a potentially offensive remark about a social group in the presence of a member of that group, bystanders look at the group member to see how he reacts: observers look longer at the Black discussant when he can hear the remark than when he cannot. In the analysis this is the **Condition × Discussant interaction** on look time: the difference between conditions should be concentrated on the Black discussant.

**Design.** 2 (Condition: headphones on vs headphones off; between subjects) × 4 (Discussant 1–4; within subjects), eye tracking.

**Conditions.** Participants watch a short video of four men in four screen quadrants, each apparently in his own room, discussing university admissions. Headphones on: all four men can hear the discussion. Headphones off: only two White men can hear each other; the Black man and the third White man have their headphones off. In both versions the second White discussant makes the potentially offensive remark (criticizing affirmative action); the critical second half of the video is the same footage in both conditions. Discussant 3 is the Black man; discussant 2 is the man making the remark. In the data file, Condi = 4 is headphones on, Condi = 2 is headphones off.

**Measures.** Look time (ms) at each of the four discussants' screen regions during the remark, from gaze samples at 60 Hz. The data file is long: 120 rows, four blocks of 30 (one per discussant), with no subject column; the subject is the row position within each block.

**Sample.** 30 non-Black participants, 15 per condition, from one of the replication's sites (the test uses this site's sample alone).

**Exclusions.** Already applied before the data file: participants who were dark-skinned, who did not understand the discussion well enough (exit interview, two judges), or whose eye-tracking failed (calibration or port-code errors).

**Test to run.** Mixed-design ANOVA, between factor Condition, within factor Discussant, DV look time; report the **Condition × Discussant interaction** F with Greenhouse-Geisser-corrected degrees of freedom and p (sphericity is violated), and partial eta squared = SS_interaction / (SS_interaction + SS_error). Not the discussant-3 contrast alone.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.txt` (text, 1 KB): 120 rows 3 columns long format, no subject column; rows ordered by Discussant, subject = position within block
- `d04.zip` (zip archive, 3.2 MB): listed only: ~41 pp*.txt raw files; named 'Part 1', no part 2 in the Data child
<!-- files:end -->
