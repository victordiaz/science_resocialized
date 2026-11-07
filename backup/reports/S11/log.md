# Log, study S11

Recognition: I believe I recognise this design (an eye-tracking study of bystanders looking at a Black discussant during a remark about affirmative action); I do not rely on any memory of its results and proceed as if I did not know it.

Start: see first command timestamp below.

## Plan (written before looking at the data)

- Data: `papers/S11/data/d02.txt`, 120 rows x 3 columns, long format, four blocks of 30 rows ordered by Discussant; subject = row position within block (1..30). Expected columns: condition (Condi: 4 = headphones on, 2 = headphones off), discussant, look time (ms).
- Variables: between factor Condition (2 levels), within factor Discussant (1-4), DV look time in ms.
- Exclusions: none beyond those the card says were already applied. I will check that each subject has the same Condi value across the four blocks (consistency of the position = subject assumption) and that there are 15 per condition; missing values, if any, cause listwise exclusion of that subject (needed for a repeated-measures ANOVA). No outlier exclusions.
- Primary test (as the card specifies): mixed-design ANOVA, Condition x Discussant interaction on look time; F with Greenhouse-Geisser-corrected df and p; partial eta squared = SS_int / (SS_int + SS_error(within)), with a 90% CI (noncentral F inversion on uncorrected df, the conventional interval for partial eta^2).
- Claim holds if: the interaction is significant at alpha = .05 (GG-corrected) AND the pattern is in the predicted direction, i.e. the condition difference is concentrated on discussant 3, with look time at discussant 3 higher in headphones off... no: higher when he CAN hear the remark = headphones on (Condi = 4) than headphones off (Condi = 2). Interaction not significant -> claim does not hold on this data. Significant interaction but pattern not driven by discussant 3 in the predicted direction -> does not hold.
- Checks (secondary, not the basis of the conclusion): simple effect of condition at each discussant (Welch t), Mauchly/epsilon, cross-check of ANOVA in R (aov with Error term), and a look at d04.zip contents (listed only; the card says it is raw part-1 files; I will not reprocess it unless d02 is unusable).

## Commands
- `date` (16:59:35 CET): start.
- `cat papers/S11/data/MANIFEST.json; .venv/bin/python -I -c "...zipfile namelist..."` : d04.zip holds 42 entries, raw pp*.txt files (pp01..pp45 with gaps), not used (d02 is usable).
- `cat -v papers/S11/data/d02.txt` : header Looktime, Discussant, Condi; 120 rows, CRLF line endings; four blocks of 30. Looked at raw values only to confirm the layout; no analysis yet.
- Wrote `papers/S11/report/analysis.py` (manual mixed ANOVA + GG epsilon + Mauchly + noncentral-F CI for partial eta^2; pingouin cross-check; secondary per-discussant Welch t; robustness without discussant 2 and on log(1+ms); figure).
- `.venv/bin/python -I papers/S11/report/analysis.py 2>&1 | tee papers/S11/report/analysis.out`
  - Checks passed: no missing values, Condi constant within each row position across the four blocks, 15 per condition. No exclusions.
  - Sphericity violated (Mauchly W = .12, p < .001), GG epsilon = .49.
  - PRIMARY: Condition x Discussant F(1.48, 41.46) = 1.40, p(GG) = .254, partial eta^2 = .048, 90% CI [0, .11] (uncorrected df). Manual and pingouin agree.
  - Direction at D3 is as predicted (on 1003 ms vs off 367 ms) but not significant (Welch p = .107); D4 shows a similar on > off difference.
  - Robustness (not pre-registered as primary, added after seeing the skewed, zero-heavy distributions): on log(1+ms) the interaction is significant (F(3,84) = 3.20, p(GG) = .035, np2 = .10), driven by the large-scale speaker region compressing differences; excluding D2 the interaction is F(2,56)=2.03, p(GG)=.155. These do not change the conclusion, which rests on the pre-specified test.
- Plan unchanged; conclusion: claim does not hold on this data (primary interaction not significant).
- Wrote `papers/S11/report/report.md`; `.venv/bin/python -I score/md2pdf.py papers/S11/report/report.md papers/S11/report/report.pdf` (renderer also left report.html).
- `date` 17:00:46 CET; wrote conclusion.json last. About 2 minutes of wall time.
