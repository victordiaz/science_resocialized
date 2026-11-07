**Claim (hypothesis).** Spoken words that participants are told to ignore, heard while they memorise a list of written words, disrupt recall more when they rhyme with the memorised words (sound similar to them) than when they do not, and they do so when recall may be in any order but not when recall must be in the presented order. The predicted effect is an interaction: the extra disruption from similar over dissimilar sound is larger under any-order recall instructions than under in-order recall instructions.

**Design.** 2 × 3 mixed design. Between participants: recall instruction (free recall, in any order, vs serial recall, in the presented order), randomly assigned. Within participants: background-sound condition (quiet; dissimilar-sounding speech; similar-sounding speech).

**Conditions and procedure.** Each trial shows a list of 10 visual to-be-remembered words, one at a time (500 ms each, no gap); all 10 words of a list share one end rhyme. A 9 s retention period follows, then 30 s of written recall. During presentation and retention, participants hear through headphones a sequence of 6 spoken to-be-ignored words (each repeated, 500 ms each), or silence. Similar sound: the spoken words share the list's end rhyme. Dissimilar sound: the spoken words come from another rhyme category. Quiet: no sound. Each participant does 15 lists, 5 per sound condition, sound conditions counterbalanced within blocks of three lists. Free-recall participants write the words in any order; serial-recall participants write them in their presented positions and may leave gaps. Stimuli were German words (participants were German speakers).

**Measure.** Proportion of words correctly recalled per sound condition (variables `R_QUIET`, `R_DISSIMILAR`, `R_SIMILAR`). Free recall is scored correct regardless of position; serial recall is scored correct only in the presented position (strict serial criterion). Group variable: `TASK` (FREE / SERIAL). Participant id: `NUMBER`. File: `d04.sav`.

**Sample and exclusions.** Students, paid participants; planned N = 118. Exclusions under the protocol: participants whose data cannot be scored (lost data file, recall sheet not filled out as instructed). The posted file already holds only the analysed participants: 118, 59 per instruction group. No further exclusions.

**The test.** Repeated-measures mixed ANOVA, sphericity assumed (no Greenhouse–Geisser correction), sound (3 levels, within) × instruction (2 levels, between), on proportion correct. The key term is the **sound × instruction interaction F, df (2, 232)**; effect size partial eta squared for that term. Not the key test: the main effect of sound, and the follow-up paired t-tests (similar vs dissimilar within each instruction group), which are a second, plausible reading of the claim.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.sav` (SPSS, 9 KB): 118 rows 16 columns 59 free / 59 serial
- `d05.xlsx` (Excel, 14 KB)
<!-- files:end -->
