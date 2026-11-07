# S26 log

Recognition: the design looks like the intergroup prisoner's dilemma "maximizing-difference" (IPD vs IPD-MD) paradigm (Halevy, Bornstein & Sagiv line of work); I carry on as if I did not know any results.

## Plan (written 17:09, before opening the data)

- Data: `d05.sav` (individual level, 120 rows); aggregate to the 3-person group (`Group_Num`). `d04.sav` used only as a cross-check of the aggregation.
- DV: group mean of `GivePool_B` (tokens 0-10), per group (n = 40 groups expected).
- Factors: `Condition_Game` (1 one-pool, 2 two-pool), `Condition_Communication` (1 none, 2 communication).
- Exclusions: none (card says none). Only drop rows with missing `GivePool_B` or condition codes, reported if any. Check that each group has 3 members and a single condition.
- Primary test: 2x2 between-groups ANOVA (Type III sums of squares, sum-to-zero contrasts; balanced design so I-III agree) on the group mean; key statistic F for the game main effect, df (1, 36). Effect size partial eta^2 = SS_game/(SS_game+SS_error) with 95% CI (noncentral-F inversion).
- Claim holds if: the game main effect is significant at alpha = .05 (two-sided F) AND the direction is two-pool mean < one-pool mean. Significant in the opposite direction or p >= .05 -> does not hold.
- Robustness: Welch t-test of game ignoring communication; Mann-Whitney on group means; ANOVA on d04 Pool_B_Percent; individual-level check with group clustering not needed beyond this.

## Commands
1. `cat papers/S26/card.md`, `cat papers/S26/data/MANIFEST.json` (before plan)
2. `.venv/bin/python -I -c "...pyreadstat.read_sav... head, labels"` — inspected structure of d04/d05 (variable names and labels only; no analysis).
3. Wrote `analysis.py`; ran `.venv/bin/python -I papers/S26/report/analysis.py | tee papers/S26/report/analysis.out` (17:10). Hashes ok; 120 rows, 40 groups of 3, no missing, no exclusions. Primary: F(1,36)=26.76, p=8.8e-6, partial eta^2=.426 [.169,.581]; two-pool < one-pool. No change of plan.
   Note: Levene significant (p=.005; one-pool+communication cell SD 3.7 vs 0.8-1.7 elsewhere); Welch t and Mann-Whitney on the game factor agree (both p<1e-4), as do individual-level OLS with group-clustered SEs and the d04 Pool_B_Percent ANOVA.
4. Wrote report.md; rendered `.venv/bin/python -I score/md2pdf.py papers/S26/report/report.md papers/S26/report/report.pdf`.
5. Wrote conclusion.json last.
