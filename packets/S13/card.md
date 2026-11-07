**Claim (hypothesis).** While attention is held on a set of moving target dots, people still register summary information about the ignored distractor dots: when all four distractors vanish, people can point to the **centroid** (the centre of mass) of the missing distractors **more accurately than chance**. Directional: localization error on distractor-centroid trials is smaller than the empirical chance error measured in a guessing phase.

**Design.** Within subjects, two phases.
- **Test phase (80 trials, conditions randomly intermixed).** Eight dots; four flash for 2 s to mark them as targets. All dots then move for 6–10 s inside a square with two red diagonals; targets and distractors stay in separate halves of the box the whole time. The primary task is to count how often any target touches or crosses a red line. At the end all dots vanish for 200 ms and some return. Individual test: one target or one distractor is missing. Centroid test: all four targets or all four distractors are missing. A central cue ("1" or "4") says how many are missing; the participant clicks the location of the single missing dot, or the centroid of the four, then types the count.
- **Guessing phase (40 trials: 20 with one missing, 20 with four missing).** No tracking; participants see only the final frame of a display generated the same way and guess where the missing dot or the centroid of the missing dots is. This gives an empirical chance level.

**Measure.** Localization error per trial: the distance between the click and the true location (for four missing dots, the area-weighted centroid of the quadrilateral they form), converted from pixels to cm (screen 34.5 × 19.5 cm at 1600 × 900) and then to degrees of visual angle at a 43 cm viewing distance (chin rest).

**Sample.** 17 adult students aged 18–35, paid.

**Exclusions.** None at the participant level. The key comparison uses, per participant: the test-phase trials where all four **distractors** were missing (centroid test), and all guessing-phase trials with four dots missing.

**Test.** Per participant, the mean localization error on those test-phase trials and the mean on those guessing trials; **paired t-test**, two-tailed, test phase minus guessing phase (a negative t means better than chance); df = n − 1; effect size dz = t / √n.

**Not the key test.** The same comparison for single distractors (individual test), and the target-versus-distractor comparisons, are secondary.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.txt` (text, 8 KB)
- `d03.txt` (text, 8 KB)
- `d04.txt` (text, 8 KB)
- `d05.txt` (text, 8 KB)
- `d06.txt` (text, 8 KB)
- `d07.txt` (text, 8 KB)
- `d08.txt` (text, 8 KB)
- `d09.txt` (text, 8 KB)
- `d10.txt` (text, 8 KB)
- `d11.txt` (text, 8 KB)
- `d12.txt` (text, 8 KB)
- `d13.txt` (text, 8 KB)
- `d14.txt` (text, 8 KB)
- `d15.txt` (text, 8 KB)
- `d16.txt` (text, 8 KB)
- `d17.txt` (text, 8 KB)
- `d18.txt` (text, 8 KB)
- `d19.dta` (Stata, 136 KB): [year] rows 22 columns Stata file the key test reads. 120 trials per subject (80 experimental, 40 guessing). 'angle' is the localization error in degrees, derived by the do-file from mouse and dot coordinates.
<!-- files:end -->
