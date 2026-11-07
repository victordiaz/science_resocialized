**Claim (hypothesis).** After making a decision, people choosing one new piece of information to read prefer decision-inconsistent information when only two pieces are on offer (one consistent, one inconsistent), but prefer decision-consistent information when many pieces are on offer (five consistent, five inconsistent). The predicted effect is an interaction between information quantity and the direction of the chosen piece: the share of participants choosing a decision-consistent piece is higher with ten options than with two. The key test is in the control (no-focus) condition.

**Design.** Between-participants 2 (information quantity: two vs ten pieces offered) × 3 (focus instruction: quality, direction, control) design, randomly assigned; the outcome is a single categorical choice. The key test uses the control-focus participants only, giving a 2 (quantity) × 2 (choice: confirming vs disconfirming) table.

**Conditions and procedure.** Online. Participants read a short case about a store manager, Mr. Miller, with mixed performance, and decide whether his contract should be extended (yes/no). They are then shown one-sentence summaries of expert opinions: two (one for, one against extension) or ten (five for, five against), and select one to read in full. Control condition: no instruction beyond "you can select only one". Quality focus: select the most important and credible piece. Direction focus: consider whether you want a piece that supports or contradicts your decision. Then a second judgment and an open question on what the study was about.

**Measure.** Whether the chosen piece confirms or disconfirms the participant's own first judgment (`decision`: confirming / disconfirming; built from `judgment1` and `infochoice`). Quantity: `options` (two / ten). Focus: `focus` (control / quality / direction). Participant id: `_session_id`. File: `d02.sas7bdat`.

**Sample and exclusions.** Volunteers on a public research website, restricted to US citizens who completed the session; planned N = 435 across all focus conditions. Exclusions under the protocol: participants who did not answer the information-choice question (blank `decision`; 27 rows of the file); participants whom independent coders judged to have guessed the study's hypothesis from the open response (already removed from the posted file). After exclusions the control-focus cell holds 150 participants.

**The test.** Pearson chi-square test of independence on the 2 × 2 table options × decision, control-focus participants only, **without** Yates continuity correction, df = 1. Effect size: phi = sqrt(chi²/N), converted to Cohen's d. Not the key test: the three-way log-linear model across all focus conditions, the same 2 × 2 test in the quality and direction conditions, and the within-quantity goodness-of-fit tests (confirming vs disconfirming at two options, at ten options).

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.sas7bdat` (SAS, 443 KB): 496 rows 26 columns SAS dataset, read with pyreadstat. This is the merged file the audit script reads (osf.io/c9z3d). Raw txt exports (sessions, sessionTasks, explicit, demographics, iat) also posted and downloaded; not opened beyond listing.
- `d03.txt` (text, 1.0 MB)
- `d04.txt` (text, 807 KB)
- `d05.txt` (text, 6.4 MB)
- `d07.txt` (text, 4.7 MB)
- `d08.txt` (text, 322 KB)
<!-- files:end -->
