# Log — S08

Recognition: the design resembles counterfactual-thinking / "upward counterfactual" studies of performance after failure; I do not recall this specific study or its outcome, and I proceed only from the data.

Start: (see `date` output in first command), 2026-11-07.

## Plan (written before looking at the data values)

- **Variables.** `Cond` (1 = more-practice statements, 2 = control), `Attempted`, `Correct` on the second exam. DV = `Correct / Attempted` per participant, computed by me (the file's `percent` column is used only as a cross-check).
- **Exclusions.** None, per the card. The only forced exclusion: a participant with `Attempted` = 0 or missing `Attempted`/`Correct`/`Cond` has an undefined DV and is dropped (reported with count). I will also check Correct <= Attempted; any violation is reported, not silently fixed.
- **Primary test.** Independent-samples Student t-test (equal variances), one-tailed, H1: mean(control, Cond 2) > mean(more-practice, Cond 1); df = N − 2.
- **Claim holds if** one-tailed p < .05 with control mean > more-practice mean. Holds "no" if p ≥ .05 (including the effect in the opposite direction). Effect size: Cohen's d (control − practice) with 95% CI (noncentral-t), plus the mean difference with 95% CI.
- **Checks (not primary).** Welch t; Mann–Whitney U; same comparison on Attempted and Correct counts; cross-check with `percent` column.

## Commands
1. `cd .../env/runs/S08; cat PROMPT.md; cat papers/S08/card.md; ls papers/S08/data` — read brief and card.
2. `head -5 papers/S08/data/d02.csv; cat MANIFEST.json` — header check only (after plan was written).
3. Wrote `analysis.py`; ran `.venv/bin/python -I papers/S08/report/analysis.py | tee papers/S08/report/analysis.out`.
4. `.venv/bin/python -I -c "..."` — inspected the 7 duplicated Subject ids (ids 1 and 55). Rows differ in date, time and scores (no full-row duplicates), so they are distinct sessions sharing a reused/default id. Kept all 61, consistent with the card (N = 61, no exclusions). No change of plan.
5. Wrote `report.md`; rendered with `.venv/bin/python -I score/md2pdf.py papers/S08/report/report.md papers/S08/report/report.pdf`.
6. Wrote `conclusion.json` last.

Result: t(59) = 2.325, one-tailed p = .0118; d = 0.60 [0.08, 1.11]. Claim holds by the pre-set criterion.
