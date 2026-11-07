# Log — S14

Recognition: [withheld from the bundle; the full line is in the record]

Start: 17:01 (local).

## Plan (written before any analysis)

- Data: `papers/S14/data/d04.sav` (primary). `d05.xlsx` will only be inspected for what it is; it is not used for the primary test unless d04 is unusable.
- Variables: `NUMBER` (id), `TASK` (FREE / SERIAL, between), `R_QUIET`, `R_DISSIMILAR`, `R_SIMILAR` (proportion correct, within).
- Exclusions: none beyond the protocol (card says the file holds only the 118 analysed participants). I will only drop rows with missing values on the four analysis variables, and report it if any.
- Primary test: 3 (sound, within) × 2 (instruction, between) mixed ANOVA, sphericity assumed; key term = sound × instruction interaction, F(2, 232), partial eta squared with 90% CI (noncentral-F inversion) plus 95% CI.
- Claim holds if: the interaction is significant at alpha = .05 AND its pattern is the predicted one, i.e. the similar-minus-dissimilar difference (dissimilar − similar recall, "extra disruption") is larger in FREE than in SERIAL. A significant interaction in the opposite direction or driven only by quiet vs speech counts as not holding. Non-significant interaction = does not hold (I will also report a contrast-level check to say whether the data are simply uninformative).
- Secondary/robustness (not the conclusion): paired t-tests similar vs dissimilar within each group; Welch t-test on the (dissimilar − similar) difference score between groups (this is the 1-df version of the predicted interaction); main effect of sound; GG-corrected p as a check.

## Commands
- `cd .../env/runs/S14` ; `cat PROMPT.md` ; `cat papers/S14/card.md papers/S14/data/MANIFEST.json`
- `.venv/bin/python -I -c "...read d04.sav and d05.xlsx, print head/dtypes/labels..."` — d04: 118×16; d05.xlsx Sheet1 is the same 16 columns (119 rows incl. header), Sheet2/3 empty. Looks like a duplicate of d04; analysis.py checks that it is identical. Plan unchanged.
- wrote `analysis.py`; `.venv/bin/python -I papers/S14/report/analysis.py | tee analysis.out` — first run failed on a column name (`p-unc` → `p_unc` in this pingouin version), fixed with sed; second run failed on a `%` in the figure title, fixed; third run clean.
- Cross-check in R (temporary CSV export of d04, deleted afterwards): `Rscript -e 'summary(aov(r ~ TASK*s + Error(NUMBER/s)))'` → TASK:s F(2, 232) = 1.628, p = .199, identical to pingouin.
- Result: interaction F(2, 232) = 1.63, p = .199, partial η² = .014. Direction is the predicted one (free 0.035 vs serial 0.013 extra disruption), but by the rule set above (significant interaction required) the claim does not hold. No change of plan.
- `.venv/bin/python -I score/md2pdf.py papers/S14/report/report.md papers/S14/report/report.pdf`
- End 17:04; ~3 minutes of analysis time. conclusion.json written last.
