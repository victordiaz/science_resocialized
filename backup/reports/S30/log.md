# Log, S30

Recognition: the claim looks like the perceptual-sensitivity work on men's misperception of women's sexual interest (Farris, Treat, Viken & McFall style); I do not recall the replication's result and proceed as if I did not recognise it.

Start: 17:11 (wall clock).

## Plan (written before any analysis)

- Data: `papers/S30/data/d02.sav`.
- Variables: `Gender` (between; coding to be checked from value labels), `Sens_Friend`, `Sens_SI` (precomputed ln α per category). Derived: diff = Sens_Friend − Sens_SI.
- Exclusions: none planned (the card says none). Only rows missing Gender or either Sens score would be dropped, reported with counts. I will also check that the precomputed scores can be recomputed from the count columns, as a data-integrity check (not to replace them).
- Primary test: 2 (category within) × 2 (Gender between) mixed ANOVA; key term Gender × category interaction, F(1, N−2), partial η² with 95% CI. Computed as a one-way between-gender ANOVA on diff (identical F), with Welch t and a bootstrap CI on the mean difference as robustness.
- Claim holds if: the interaction is significant at α = .05 two-sided AND the direction matches the claim, i.e. men's deficit relative to women is larger for sexual interest than for friendly (women's Sens_SI advantage > women's Sens_Friend advantage, equivalently diff larger in men than in women). A significant interaction in the opposite direction counts as "no". Non-significant: "no" (the predicted interaction is not found); I will say "cannot tell" only if the data are unusable.
- Secondary/robustness: gender main effects per category; Pres_time added as a factor (Gender × Pres_time on diff); Mann–Whitney on diff.

## Commands
- `.venv/bin/python -I -c "...read_sav, print head/dtypes/labels/describe"` — Gender 1=Male, 2=Female; Pres_time 1=500ms, 2=3000ms. Count columns are hit/FA/miss/correct-rejection totals per category, not the full 4×4 confusion matrix, so ln α cannot be recomputed exactly from them; the integrity check is dropped (change of plan, reason: information not in the file). I use the precomputed scores as the card instructs.
- Wrote `papers/S30/report/analysis.py`; ran `.venv/bin/python -I papers/S30/report/analysis.py > papers/S30/report/analysis.out 2>&1` (17:11). Primary: interaction F(1,142)=1.19, p=.276, partial η²=.008 [.000,.061]; direction as predicted but not significant → claim does not hold by the pre-stated rule.
- `grep -n -i "img\|image" score/md2pdf.py` — check renderer resolves relative images.
- Wrote report.md; `.venv/bin/python -I score/md2pdf.py papers/S30/report/report.md papers/S30/report/report.pdf`.
- Appended a power computation to analysis.py (to back the limitation sentence with a computed number) and reran the same command; re-rendered PDF.
- Wrote conclusion.json last. End ≈17:13; ~3 minutes.
