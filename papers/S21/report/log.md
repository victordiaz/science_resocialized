# Log S21

Recognition: I partly recognise the paradigm (stimulus quality x word frequency in lexical decision with pseudohomophone nonwords, ex-Gaussian analysis, Yap/Balota/Besner line of work) but do not recall this replication's result; carrying on as if I did not.

Start: 17:07 (2026-11-07).

## Plan (written before any analysis)

Data: `d07.csv`, trial-level (columns seen in header only: Subject, ldtfreq, Procedure, word_NW, Target.ACC, Target.RT, border, z). I will first inspect the coding of the columns (value counts only, no condition means) to map: ldtfreq -> frequency (high/low), Procedure -> quality (CleanProc vs degraded), word_NW -> word vs nonword.

Variables: per participant x quality (clear/degraded) x frequency (high/low), mu of an ex-Gaussian fitted to correct word-trial RTs.

Exclusions (as the card specifies; no participants excluded):
1. Errors (Target.ACC != 1) removed.
2. RT < 200 ms or > 3000 ms removed.
3. Then, per participant, separately for word and nonword trials, RTs beyond 2.5 SD of that participant's mean (computed on the remaining correct trials) removed.
If the file already appears trimmed (e.g. the `border`/`z` columns), I will still apply the trimming from the raw RTs myself and report how many trials each step removes.

Fit: QMPE v2.18 is not available. I will fit the ex-Gaussian by quantile maximum likelihood myself (QMPE-style: likelihood of counts of RTs falling between empirical quantiles of the data, using the ex-Gaussian CDF, quantiles at deciles... specifically the QMPE default-like set of ~ (n/ ~) quantile bounds; I will use deciles 0.1..0.9, i.e. 10 bins), optimised with Nelder-Mead from moment-based start values. Robustness: ordinary continuous maximum likelihood (scipy exponnorm) per cell.

Primary test: 2 x 2 repeated-measures ANOVA on mu; key statistic F(1, n-1) for quality x frequency interaction (equivalent to one-sample t on the interaction contrast (LFdeg - HFdeg) - (LFclear - HFclear), F = t^2). Effect size partial eta^2 = SS_int / (SS_int + SS_err), with 95% CI (via noncentral F inversion) plus the mean interaction contrast with 95% CI.

Claim holds if: interaction p < .05 two-sided AND the contrast is positive (frequency effect on mu larger in degraded than clear). Holds = no if p >= .05 or opposite direction significant; "cannot tell" only if the data cannot be mapped/fitted.

Checks: same ANOVA on continuous-ML mu; on mean RTs (secondary); main effects.

## Commands
- `cd .../env/runs/S21` (first python call failed: wrong relative path to .venv; no output).
- `.venv/bin/python -I -c` value counts of columns (no condition means). Findings: 71 subjects, 22,481 rows, all Target.ACC = 1 and RT in [203, 2998] -> the file already contains only correct trials within 200-3000 ms, so steps 1-2 of the exclusions were applied upstream; I cannot report how many trials they removed. word_NW: 1 = word (ldtfreq 1 or 2), 2 = nonword (ldtfreq 3). `border` = 0 on 142 rows, `z` looks like a within-subject z-score.
- Checked whether `z` equals per-subject, per-word/nonword z of RT and whether border==0 equals |z|>2.5.
  Result: `z` column is NOT the per-subject x word/nonword z (max diff 2.4); |z column| never exceeds 2.5. Meaning of `border`/`z` unclear; I do not use them.
- Frequency coding (decided before looking at cell means): 100 HF and 100 LF items, so the ldtfreq level with more correct trials (1: 6,362 vs 2: 5,454) is the more accurate = high-frequency level. Checked afterwards that ldtfreq 1 is also faster overall (836 vs 939 ms): consistent.
- Wrote `analysis.py` (QMLE with decile bin bounds, Nelder-Mead; continuous ML robustness; 2x2 RM ANOVA via contrasts, F = t^2; partial eta^2 CI by noncentral-F inversion).
- First run `.venv/bin/python -I papers/S21/report/analysis.py` showed my 2.5-SD z within the file reaches 4.7 (598 trials beyond 2.5 SD), i.e. the file is NOT already SD-trimmed. That first run had (by my error) not yet applied the planned trim; I fixed the script to apply it, as the plan says (no change of plan). Untrimmed version kept as robustness (`--no-trim`, output in `analysis_notrim.out`). Untrimmed primary: F(1,70) = 9.83, p = .0025 — same conclusion.
- `.venv/bin/python -I papers/S21/report/analysis.py > analysis.out` and `... --no-trim > analysis_notrim.out`.
  Primary (trimmed, QMLE mu): interaction contrast = 86.9 ms [35.6, 138.2], F(1,70) = 11.41, p = .0012, partial eta^2 = .140 [.024, .289]. Frequency effect on mu: clear 17.7 ms, degraded 104.6 ms. Continuous-ML mu: F(1,70) = 13.17, p = .0005. Mean RT (secondary): interaction -13.3 ms, F(1,70) = 1.26, p = .26 (not significant, opposite sign).
- Limitation: exclusion steps 1-2 (errors, <200/>3000 ms) were applied upstream; counts removed are not recoverable from the file. QMPE v2.18 not available; own QMLE implementation used.
- Rendered report: `.venv/bin/python -I score/md2pdf.py papers/S21/report/report.md papers/S21/report/report.pdf`.
