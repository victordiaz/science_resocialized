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
