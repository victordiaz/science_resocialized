**Claim (hypothesis).** When group members can help their own group without harming the other group, they contribute less to the pool that harms the other group. Direction: the contribution rate to the between-group pool B is lower in the two-pool game (which offers both a within-group pool W and pool B) than in the one-pool game (where pool B is the only pool). The key term is the main effect of game type.

**Design.** 2 (game: one-pool vs two-pool) x 2 (communication: none vs 5 minutes of free within-group discussion before deciding) between-subjects. Cohorts of six same-sex participants are randomly assigned to a condition and split into two 3-person groups who play against each other once. Each player has 10 tokens and decides privately how many to keep (each kept token pays the player 2 money units), give to pool W (two-pool game only: each token pays every ingroup member 1 unit), or give to pool B (each token pays every ingroup member 1 unit and subtracts 1 unit from every outgroup member). Pools are labelled neutrally.

**Measures.** `GivePool_B` = tokens (0-10) each participant gives to pool B. Unit of analysis: the 3-person group (`Group_Num`); DV = the group's mean `GivePool_B` (equivalently the group's percentage of its endowment given to pool B). Factors: `Condition_Game` (1 = one-pool game, 2 = two-pool game), `Condition_Communication` (1 = none, 2 = with communication).

**Sample.** 120 participants (university participant pool, paid by outcome; 32 all-female and 8 all-male groups), forming 40 three-person groups, 10 groups per cell.

**Exclusions.** None.

**Test.** 2 x 2 between-groups ANOVA on the group-level pool-B contribution with game, communication and their interaction; key statistic = F for the game main effect, df (1, groups - 4). Effect size partial eta^2 = SS_game / (SS_game + SS_error). Not the key test: the two-pool-game-only t-test of communication on pool-W contributions.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d04.sav` (SPSS, 5 KB): 40 rows 17 columns Group-level aggregate; the SPSS syntax uses its Pool_B_Percent.
- `d05.sav` (SPSS, 9 KB): 120 rows 19 columns The file the key test reads. 10 groups per cell.
<!-- files:end -->
