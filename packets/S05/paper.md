# S05 — Is temporal selection of a second cued letter suppressed, delayed and diffused with different time courses?

## Question
In a rapid letter stream with two cued letters, does the report of the second cued letter change in efficacy (how often a report comes from around its position), latency (where reports are centred) and precision (their spread), with time courses across the 1-10 item interval that differ between measures? Predicted: a significant measure (3) x target (2) x SOA (10) interaction.

## Data and sample
One file (`d04.csv`): 720 per-participant summary values = 12 participants x 3 measures x 2 targets x 10 SOAs. No missing values; every cell has 12 values. Practice trials were already discarded; **no exclusions**, n = 12 participants, 720 values analysed. Column mapping per the card: column `efficacy` = measure, `latency` = target, `precision` = SOA.

## Test (named in advance)
Full-factorial fixed-effects ANOVA, all factors categorical, every value treated as independent (participant not in the model; equivalent to Matlab `anovan(..., 'model','full')`), Type III sums of squares (balanced design). Term of interest: measure x target x SOA. The claim holds if p < .05.

## Result
**Three-way interaction: F(18, 660) = 12.98, p = 3.3 x 10^-33, partial eta-squared = .26, 95% CI [.19, .30].**

Cell means (averaged over participants):

| measure | target | SOA 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| efficacy | T1 | .124 | .126 | .128 | .124 | .124 | .125 | .125 | .127 | .127 | .124 |
| efficacy | T2 | .098 | .097 | .084 | .078 | .076 | .084 | .096 | .099 | .110 | .113 |
| latency | T1 | .24 | .21 | .10 | .08 | .10 | -.02 | .08 | .06 | .08 | .02 |
| latency | T2 | -.22 | -.62 | -.82 | -.14 | .44 | 1.13 | .92 | .66 | .68 | .52 |
| precision | T1 | 1.42 | .91 | 1.30 | 1.27 | 1.18 | 1.11 | 1.24 | 1.07 | 1.12 | 1.06 |
| precision | T2 | 1.75 | 1.98 | 3.25 | 4.25 | 2.17 | 1.27 | 1.40 | 1.45 | 1.18 | 1.38 |

For T1 all three measures are nearly flat across SOA. For T2, efficacy dips at SOA 3-5 and recovers by 9-10; variance (diffusion) peaks at SOA 3-4; latency is shifted *earlier* than the target at SOA 1-3 and *later* at SOA 5-10, peaking at SOA 6.

## Checks (not primary)
- Measures are on different scales (probability, positions, positions squared), so part of an interaction across measures could be scale alone. With values z-scored within measure, the three-way term is still F(18, 660) = 10.18, p = 1.6 x 10^-25.
- Repeated-measures ANOVA with participant as a random factor (R `aov`, Error strata): three-way F(18, 198) = 16.87, p < 2 x 10^-16 (z-scored: F = 14.75).
- Target x SOA within each measure (fixed-effects): efficacy F(9, 220) = 1.98, p = .043; latency F(9, 220) = 12.57, p < 10^-15; precision F(9, 220) = 8.96, p < 10^-10. The efficacy effect is small in absolute terms (a dip of ~.05 against ~.12).

## Caveats
Treating 720 values from 12 people as independent inflates the degrees of freedom; the card specifies that test, and the participant-aware ANOVA gives the same answer. The early-SOA latency shift for T2 is negative (reports before the target), not "delayed"; the delay appears from SOA 5 on. Efficacy values are per-position probabilities (~1/8), so its interaction is the weakest of the three.

## Conclusion
**The claim holds on this data: the measure x target x SOA interaction is significant and large (F(18, 660) = 12.98, p < .001, partial eta-squared = .26), and survives rescaling and a participant-level ANOVA.**

Files: `analysis.py` (all numbers), `analysis.out`, `log.md`.
