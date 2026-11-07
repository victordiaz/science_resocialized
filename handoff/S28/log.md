# S28 log

Recognition: [withheld from the bundle; the full line is in the record]

Start: 17:09 (Nov 7 2026).

## Plan (written before any analysis; only the card and the CSV header/first 4 rows seen)

- Data: `papers/S28/data/d09.csv` (74 rows).
- Variables: DV `aggressivenessScore` (mean of Q5 and Q8, 1-9); factors `mapCondition` (Global/Local/Control) and `puzzleCondition` (aggression vs neutral).
- Exclusions (from the card): drop `discard == 1` (correct guess of hypothesis; expected 3); drop rows with missing `aggressivenessScore` (did not complete the DV). Keep both PID 18 rows. Expected N = 71. I will also verify that aggressivenessScore equals (Q5+Q8)/2 and report any mismatch, but use the given column.
- Primary test: between-participants ANOVA `aggressivenessScore ~ C(mapCondition) * C(puzzleCondition)`, type III SS with sum-to-zero contrasts (type II reported too); key term the interaction F(2, 65). Effect size partial eta² = SS_int/(SS_int+SS_res), with a 95% CI from inverting the noncentral F.
- Claim holds if: interaction p < .05 AND the pattern matches the direction: aggression-minus-neutral difference positive in Global (and Control) and negative in Local. Interaction significant with a different pattern = does not hold as stated; p >= .05 = does not hold (no evidence for the interaction on this data; I will say whether the CI is wide enough to make it "cannot tell").
- Secondary/robustness (not the basis of the conclusion): cell means/SDs; simple effects of puzzle within each map condition (t-tests); planned contrast Local vs (Global+Control) on the prime effect; ANOVA keeping discard==1 participants; nonparametric check (rank ANOVA).

## Commands
- `.venv/bin/python -I -c "...value_counts..."` — checked shape (74×36), cell counts, discard==1 (3), missing DV (0), PID 18 twice.
- Wrote `analysis.py`; ran `.venv/bin/python -I papers/S28/report/analysis.py > papers/S28/report/analysis.out`.
- Fixed pandas print width and removed a dead line; reran same command. No change of plan; N = 71 as expected, DV column equals (Q5+Q8)/2 in all rows.
- Result: interaction F(2,65)=0.865, p=.426, partial eta²=.026 [0, .114]. Claim does not hold. Unplanned observation: pattern is not as claimed (aggression puzzle gave lower ratings in Control and Local, ~0 in Global); main effect of map condition significant (Global rated more aggressive).
- Wrote `report.md`; rendered with `.venv/bin/python -I score/md2pdf.py papers/S28/report/report.md papers/S28/report/report.pdf` (renderer also left report.html).
- Wrote `conclusion.json` last. End 17:11; about 2 minutes of wall time.
