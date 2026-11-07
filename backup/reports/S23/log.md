# Log, S23

Recognition: yes, I recognise the paradigm (repeated estimates by one person averaged, with a delay between them); I proceed as if I did not, and rely only on the computation below.

## Plan (written before any analysis)

- Data: session 1 = `d04.txt`, session 2 = `d05.txt`, merged (inner join) on `student_number_simple`. `d06.txt` not used.
- Variables: `q1`..`q8` in each session; truths 6.3, 43.3, 32.3, 13.4, 53.6, 54.8, 26.4, 22.4.
- Per participant: MSE1 = mean_k (g1_k - t_k)^2; MSEavg = mean_k ((g1_k + g2_k)/2 - t_k)^2.
- Exclusions (as on the card): any `defocus_q*` == 1 in either session; any of the 16 answers missing; session-2 `peaking` != "Nee". Counts reported step by step. Duplicated IDs within a session, if any, will be reported; I will drop IDs duplicated within a session (cannot match unambiguously).
- Primary test: paired t-test MSE1 vs MSEavg, two-sided p reported (one-sided also given, since the direction is predicted), df = n - 1, d_z = t/sqrt(n) with 95% CI (noncentral-t-free approximation: CI of mean difference / SD of differences).
- Claim holds if mean(MSE1 - MSEavg) > 0 with two-sided p < .05.
- Robustness (not deciding): Wilcoxon signed-rank on the same differences; analysis without exclusions; MSE2 vs MSEavg descriptive.

## Commands
1. `cd .../runs/S23; cat PROMPT.md; ls -R papers/S23; cat papers/S23/card.md`
2. `head -3 papers/S23/data/d04.txt; head -3 papers/S23/data/d05.txt; cat papers/S23/data/MANIFEST.json` (headers only)
3. Wrote `analysis.py`; `.venv/bin/python -I papers/S23/report/analysis.py | tee papers/S23/report/analysis.out`
   - Found duplicated IDs: 5 IDs (incl. one blank) repeated in session 1 and 3 in session 2. Per plan, dropped duplicated IDs: 160 unique matched, 138 after exclusions (20 defocus, 1 missing, 1 peaking).
4. Noticed the card's sample (174 matched, 140 after; 125 women, 15 men) corresponds to keeping duplicate-ID rows. Added this as a robustness block (no change to the primary test) and reran: `.venv/bin/python -I papers/S23/report/analysis.py > papers/S23/report/analysis.out`. It reproduces n = 140 and 125/15 exactly; result unchanged in direction and significance.
5. Wrote `report.md`; `.venv/bin/python -I score/md2pdf.py papers/S23/report/report.md papers/S23/report/report.pdf`
6. Wrote `conclusion.json` last.

No change to the primary test after seeing the data.
