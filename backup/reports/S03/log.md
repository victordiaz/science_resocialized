# S03 log

Recognition: I do not recognise this specific study (a manipulation of listing reasons about advice and its effect on mixed feelings toward a sex-offender list); proceeding from the data only.

Start: 16:55 (2026-11-07).

## Plan (written before any analysis; only file heads have been viewed to learn the format)

- **File:** `data/d05.txt`, the analysis file the card describes (89 rows, 32 columns, 3 summary lines above the header, `Include` column). `d06.tsv` (97 data rows, no Include column, has `SexOffender` and precomputed `NotTorn_R`, `Indecisive_RC`, `Ambiv`) is used only as a cross-check.
- **Variables:** `Condition` (0 neutral, 1 favour-only, 2 for-and-against). Items: `StrongMixed` (-3..3), `NotTorn` reversed as -NotTorn, `Indecisive` recoded as Indecisive-4. Index = mean of the available recoded items (person mean of items answered). "." treated as missing.
- **Exclusions:** keep `Include == 1` only (= did not report experience with sexual offenders / the list). No other exclusions. Participants with all three items missing would drop out (expected none). Expect n = 70.
- **Primary test:** one-way between-subjects ANOVA of the index on Condition (3 levels), F(2, n-3), alpha = .05; eta^2 = SS_cond/(SS_cond+SS_err) with a 95% CI (noncentral-F inversion).
- **Claim holds if:** the omnibus F is significant at p < .05 AND the condition-1 mean is lower than the condition-2 mean (the predicted direction). If p >= .05: does not hold on this data. If significant but condition 1 >= condition 2: does not hold (wrong direction).
- **Secondary (not decisive):** Welch t-test cond 1 vs 2 with Cohen's d; Welch ANOVA; Kruskal-Wallis; same ANOVA on d06 with SexOffender=="No" as a consistency check; item-level descriptives.

## Commands
1. `cat PROMPT.md; ls -R papers` (brief, file listing)
2. `cat papers/S03/card.md papers/S03/data/MANIFEST.json; wc -l data/*; head d05.txt; head -5 d06.tsv` (format only)
3. Wrote this plan.
4. Wrote `analysis.py`; `.venv/bin/python -I papers/S03/report/analysis.py > papers/S03/report/analysis.out 2>&1`
5. Added `pd.set_option` for wider printing (the t-test p-value was truncated); re-ran the same command. No change to the analysis.
6. Wrote `report.md`; `.venv/bin/python -I score/md2pdf.py papers/S03/report/report.md papers/S03/report/report.pdf`
7. Wrote `conclusion.json`.

No change of plan. Notes: Include==0 coincides exactly with SexOffender=="Yes" (19 rows), as the card says. One included participant answered 2 of 3 items and got the mean of those two. d06 (97 rows, 12 with missing SexOffender) gives the same picture: F(2,65)=1.91, p=.156.
