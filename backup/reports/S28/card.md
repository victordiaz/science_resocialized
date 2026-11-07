**Claim.** How people look at a map beforehand changes how an earlier word puzzle colours their judgement of a person. After a word puzzle full of aggression words, rather than a neutral one, an ambiguous target is rated as more aggressive by participants who first attended to a map's overall shape (and by those in the control condition), and as less aggressive by participants who first attended to the map's details. Tested as the map condition × puzzle condition interaction.

**Design.** 3 (map condition: overall shape vs details vs control) × 2 (word puzzle: aggression vs neutral), fully between-participants, run in a group session in a lecture hall with each task in a separate folder.

**Conditions.** Map condition (`mapCondition`, values `Global`, `Local`, `Control` in the data): participants view a projected state map for 3 minutes, attending to its overall shape (`Global`), its details (`Local`), or both (`Control`), then answer map questions. Word puzzle (`puzzleCondition`): a 2-minute word-search puzzle of 12 words; in the aggression version, 6 of those words are aggression-related (violence, hatred, brutal, murder, attack, malicious), and in the neutral version all 12 are neutral.

**Measure.** Participants read a paragraph about "John", who behaves ambiguously aggressively, and rate him on 10 bipolar 1–9 scales. The dependent variable `aggressivenessScore` is the mean of the two critical scales: item 5 (assertive–hostile) and item 8 (determined–belligerent).

**Sample.** 74 undergraduates tested; 71 analysed.

**Exclusion rules.** Exclude participants who correctly guessed the purpose of the study (`discard == 1`, 3 participants) and participants who did not complete the dependent measures. Note that PID 18 appears twice and belongs to two different people; keep both rows.

**Test.** Between-participants ANOVA `aggressivenessScore ~ mapCondition * puzzleCondition`. The key term is the interaction, F(2, 65); it has the same sum of squares under type II and type III. Effect size: partial η² = SS_interaction / (SS_interaction + SS_residual).

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d09.csv` (CSV, 21 KB)
<!-- files:end -->
