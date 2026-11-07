# S27 log

Recognition: I recognise the general paradigm (needs-based model of reconciliation: victims' need for empowerment, perpetrators' need for acceptance); I do not recall this replication's results and proceed as if I did not know the original.

Start: 17:09 (Sat 7 Nov 2026).

## Plan (written before opening the data)

- Data: `papers/S27/data/d05.sav` (SPSS; the CSV is described as its twin; I will check row count agrees but analyse the .sav).
- DV: `AvgWillingReconcileTime2` (after-message willingness to reconcile, mean of 10 items, higher = more willing). Used as given in the file; I will also check that it reproduces from the item columns if they are identifiable, as a check only.
- Factors: `VictimOrPerpV0P1` (0 victim, 1 perpetrator), `AcceptOrEmpowerA0E1` (0 acceptance, 1 empowerment).
- Exclusions: none by rule. Listwise drop of rows missing the DV or either factor code (card expects 141 left; cells 33/35/39/37).
- Primary test: between-subjects 2x2 ANOVA (Type III sums of squares, sum-to-zero contrasts; with near-equal cells Type II/III give near-identical results), role x message interaction F(1, N-4), with partial eta squared and a 95% CI for it.
- Claim holds if: interaction p < .05 (two-sided) AND the pattern is the predicted crossover direction: victims' mean higher under empowerment than acceptance, and perpetrators' mean higher under acceptance than empowerment (both simple differences in the predicted direction; simple effects need not be individually significant). Claim does not hold if interaction p >= .05 or the significant interaction is in the opposite/non-crossover direction against prediction (e.g. both groups prefer the same message with only a magnitude difference counts as "partially"; I will call it "no" unless the sign pattern is the predicted one). "Cannot tell" reserved for data problems that block the test.
- Checks (not primary): simple effects of message within each role (t tests), main effects, Levene's test, Type II ANOVA, HC3-robust interaction test, Mann-Whitney within role, mixed analysis with Time-1 willingness as covariate (ANCOVA) as robustness.

## Commands
All run from `/Users/vladnicolescu/Developer/science-resocialized-target/env/runs/S27`.

1. `cat PROMPT.md; ls -R papers score` — read brief, listed files.
2. `cat papers/S27/card.md papers/S27/data/MANIFEST.json`
3. (wrote this plan) 
4. `.venv/bin/python -I -c "...pyreadstat.read_sav(d05.sav); print shape, columns, describe of R/M/DV"` — 146 x 93; 144 rows with codes, 141 with DV.
5. Wrote `analysis.py`; `.venv/bin/python -I papers/S27/report/analysis.py > papers/S27/report/analysis.out`.
   - Primary result: interaction F(1,137) = 1.425, p = .235, partial eta^2 = .010, 95% CI [0, .067]. Cell pattern is opposite to the predicted crossover (victims slightly higher after acceptance, perpetrators slightly higher after empowerment).
   - The DV-reconstruction check (reversing Angry2/FeelingstoAmy2/FeelingstoRelationship2) did not reproduce the stored DV (r = .71) — my guess about keying was wrong, not the stored DV.
6. `.venv/bin/python -I -c "...search all 2^10 reversal patterns..."` — stored DV equals the plain mean of the ten Time-2 item columns exactly; those columns are already keyed. Fixed the check in `analysis.py` (no reversal), reran step 5: exact match, alpha = .92. Primary numbers unchanged. This only changed a check, not the plan.
7. Listwise deletion dropped 5 rows (the 2 missing codes are among the 5 missing the DV), leaving 141, cells 37/37/33/34 as the card said.
8. Wrote `report.md`; `.venv/bin/python -I score/md2pdf.py papers/S27/report/report.md papers/S27/report/report.pdf`.
9. Wrote `conclusion.json` last.

No change of plan. Decision per pre-stated rule: interaction p >= .05 and signs opposite to prediction -> claim does not hold.
