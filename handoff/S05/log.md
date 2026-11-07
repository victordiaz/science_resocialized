# Log — S05

Recognition: [withheld from the bundle; the full line is in the record]

Start: 2026-11-07 16:57 CET.

## Plan (written before any analysis)

- Data: `papers/S05/data/d04.csv`, 720 rows (header seen only: `temporal selection, efficacy, latency, precision, subject`).
- Variables: dependent value = `temporal selection`; factors per the card's column mapping: `efficacy` column = measure (3 levels), `latency` column = target (2 levels), `precision` column = SOA (10 levels); `subject` = participant (1..12), not used in the primary model.
- Exclusions: none (practice trials already discarded per the card; the file is the per-participant summary). Rows with missing values, if any, would be dropped and reported.
- Primary test: full-factorial fixed-effects ANOVA (all factors categorical), measure x target x SOA, every value treated as an independent observation, Type III sums of squares with sum-to-zero contrasts (balanced design, so Type I/II/III agree), as Matlab `anovan(...,'model','full')`. Term of interest: three-way interaction, F(18, 660), with partial eta squared and a 95% CI for partial eta squared (from the noncentral F).
- Holds if: the three-way interaction is significant at alpha = .05 (p < .05). Does not hold if p >= .05.
- Checks (not primary): balance check, cell means; repeated-measures ANOVA with participant (R aov with Error(subject/(measure*target*SOA))) for the same term; per-measure target x SOA interactions to describe the pattern. Note the measures are on different scales (probability, positions, positions^2), so the 3-way interaction is partly a scale artefact risk; I will also report a check on within-measure z-scored values.

## Commands
1. `cat PROMPT.md; ls -R papers/S05; cat papers/S05/card.md papers/S05/data/MANIFEST.json; wc -l, head -5 papers/S05/data/d04.csv` (header only seen before the plan).
2. Wrote `papers/S05/report/analysis.py` (plan above, unchanged).
3. `.venv/bin/python -I papers/S05/report/analysis.py > papers/S05/report/analysis.out 2>&1` → 720 rows, 0 missing, balanced (12 per cell). Three-way F(18, 660) = 12.98, p = 3.3e-33, partial eta^2 = .26.
4. `sed` removed one dead no-op line from analysis.py; reran the same command; output identical.
5. Wrote report.md; rendered with `.venv/bin/python -I score/md2pdf.py papers/S05/report/report.md papers/S05/report/report.pdf`.
6. Wrote conclusion.json.

No change of plan. No figure (matplotlib not in the listed environment); a cell-means table is given instead.
End: 2026-11-07 16:58 CET (about 2 minutes). md2pdf also wrote report.html alongside the PDF.
