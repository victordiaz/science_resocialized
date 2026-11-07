# Log — S04

Recognition: I recognise the general paradigm (visual statistical learning of triplets with 2AFC familiarity tests) but not this specific study or its outcome; proceeding from the data only.

Start: 17:12 (wall clock).

## Plan (written before opening any data file)

- **Data**: 15 MATLAB files d04–d18, assumed one per participant. Read with scipy.io.loadmat.
- **Variables**: per trial, `triplet_type` and `correct` (as named on the card). Keep only trials with `triplet_type == "real"`; discard "pseudo".
- **Per-participant score**: mean of `correct` over the real trials (expected 16 per participant).
- **Exclusions**: none, per card (no dropouts, all participants kept including those who noticed triplets). If a file is unreadable or has a trial count other than 16 real trials, I will report it and keep whatever valid real trials it has.
- **Primary test**: two-sided one-sample t-test of the 15 per-participant proportions against 0.5; effect size d = t/sqrt(n) (= (mean-0.5)/SD), with a 95% CI for d (noncentral t) and for the mean.
- **Claim holds** if mean proportion > 0.5 and p < .05 (two-sided). Does not hold if p >= .05 (or significant below chance). With n=15 a null is weakly informative; I will report the CI and a Wilcoxon signed-rank and a pooled binomial / GLMM-style check as robustness only.

## Commands
- `python -c` loadmat d04.mat: struct `data` with fields correct, response, order_within_trial (base-foil/foil-base), triplet_type (real/pseudo), trial_order, params, Ntrials=32. Matches plan; no change.
- Wrote `analysis.py`; ran `.venv/bin/python -I papers/S04/report/analysis.py | tee papers/S04/report/analysis.out`. All 15 files have 32 trials, 16 real; `correct` agrees with response/order coding on every trial. No exclusions. No change of plan.
- Primary result: mean 0.700, t(14) = 3.71, p = .0023, d = 0.96 [0.33, 1.56]. Claim holds by the pre-set criterion.
- Wrote `report.md`; rendered with `.venv/bin/python -I score/md2pdf.py papers/S04/report/report.md papers/S04/report/report.pdf`.
- Wrote `conclusion.json` last.
