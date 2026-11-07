**Claim (hypothesis).** In English, where the colour adjective comes before the noun, preparing the sounds of the noun is influenced by the sounds of the colour word before it, but not the other way round. Hence, when naming the object in a coloured line drawing, people will be faster when the object's name shares its onset with the colour's name (congruent, e.g. a green goose) than when it does not (incongruent); no such effect is predicted for naming the colour. The tested prediction is the object-naming one: congruent mean RT lower than incongruent mean RT.

**Design.** Participants name coloured line drawings aloud. Task is between subjects (object naming or colour naming); congruency (congruent vs incongruent colour-object pairing) is within subjects. Four colours (red, green, blue, pink), ten line-drawn objects per colour sharing at least the onset consonant (80 experimental items: 40 congruent pairings and 40 incongruent re-pairings with a colour of a different onset), plus 80 fillers, in four pseudorandom blocks with a Latin-square block order. Trial: fixation 700 ms, blank 200 ms, coloured picture 1,500 ms; participants name the object (or, in the other group, the colour) aloud. Familiarisation with object names and 8 training trials first. Speech onsets, detected by a microphone trigger, checked and corrected trial by trial.

**Measure.** Naming latency (ms) on experimental trials, averaged per participant per congruency condition (by-subjects, F1).

**Sample.** 24 native English-speaking psychology students in the UK, for course credit, 12 per task; the key test uses the 12 object-naming participants (data `NamingTask == "naming"`).

**Exclusions.** Drop error trials (`Errors == 1`: naming errors, non-vocal responses, hesitations, no response); then drop trials more than 3 SD above or below that participant's mean RT on error-free trials.

**Test.** Two-sided paired t-test of per-participant mean RT, congruent vs incongruent, object-naming group only, df = 11; effect size dz = t / sqrt(n). Not the colour-naming group, not the by-items (F2) test, and not the task x congruency ANOVA.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.sav` (SPSS, 2 KB): 24 rows 4 columns Per-subject condition means; 12 colour-naming and 12 object-naming ('naming') subjects
- `d03.sav` (SPSS, 4 KB): 80 rows 4 columns By-item means (F2), not used for the key test
- `d06.sav` (SPSS, 128 KB): [year] rows 9 columns Trial-level data (Subject, NamingTask, Item, RT, Errors, Condition, ...); the aggregation into F1 was not re-derived
<!-- files:end -->
