# Log, study S06

Recognition: [withheld from the bundle; the full line is in the record]

Started 16:57 (local clock).

## Plan (written before any analysis)

- Data: `papers/S06/data/d11.csv`, the derived PD file (3 rows per participant: Weapons-Black, Weapons-White, Flankers). Other files will only be inspected to check that d11 is consistent (e.g. participant count), not used for the primary test.
- Variables: `PD` (control estimate, outcome), `Group` (high internal/low external vs high internal/high external; between), `Task` (Weapons vs Flankers; within), `ID`.
- Exclusions: none, per the card ("every participant in the PD file enters the test"). Rows with missing PD would be dropped only if present, and reported.
- Primary test: `aov(PD ~ Group * Task + Error(ID/Task))` in R on the 3-rows-per-participant file (both Weapons rows kept). Report Group x Task F, df, p from the ID:Task stratum; partial eta^2 = SS_int / (SS_int + SS_resid of that stratum), with a 90%/95% CI from the noncentral F.
- Claim holds if: the Group x Task interaction is significant at alpha = .05 (two-sided F) AND its direction is as claimed: the (HI/LE minus HI/HE) difference in PD is larger on Weapons than on Flankers. Significant in the opposite direction, or p >= .05, counts as not holding.
- Checks (not the basis of the conclusion): 2x2 mixed ANOVA on per-participant Weapons mean vs Flankers (should give the same interaction); simple group effects per task (Welch t); Python replication of the numbers.

## Commands
1. `cd .../env/runs/S06 && cat PROMPT.md; ls` — read brief.
2. `cat papers/S06/card.md papers/S06/data/MANIFEST.json` — read card.
3. (plan above written) `head` of each data file to confirm d11 structure (columns ID, GENDER, HiLoCat, Measure, PD, TrialType, Task).
4. Wrote `analysis.R`; ran `/opt/homebrew/bin/Rscript papers/S06/report/analysis.R > papers/S06/report/analysis.out`.
5. Wrote `analysis.py` (runs analysis.R, then a pingouin cross-check); ran `.venv/bin/python -I papers/S06/report/analysis.py > papers/S06/report/analysis.out`. Python and R agree: F(1,73) = 0.432, p = .513.
6. Wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S06/report/report.md papers/S06/report/report.pdf`; wrote conclusion.json last.

No change of plan. d11 has 225 rows, 75 IDs (46 / 29), no missing PD; Weapons-Black values match the wide file d12 exactly. No exclusions.
Finished 16:58 (about 2 minutes of wall time by the local clock).
