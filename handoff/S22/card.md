**Claim (hypothesis).** When people are told to think of a six-item list as two groups of three, a temporal gap appears between the groups in what they reproduce, even in a task whose instruction is to reproduce the list's timing faithfully. The predicted effect: in the timing task, the latency of the 4th response (the first item of the second group) sits further above the trend of the surrounding latencies under grouping instructions than under standard (ungrouped) instructions.

**Design.** Fully within-participants: task (order recall vs timing recall, cued after each list) × instruction (ungrouped, first half; grouped, second half; fixed order for everyone) × output position (1–6). The key test uses the timing task only.

**Conditions and procedure.** Each trial plays six spoken digits (sampled without replacement from 1–9) over headphones with irregular pauses (pauses on a list sum to 3,000 ms). After the list a cue appears: NUMBERS (type the digits in order) or RHYTHM (ignore the digits, tap one key at the remembered onset of each item). Halfway through, participants are told to think of each list as two groups of three, with an example. 80 trials per participant: 20 per task × instruction cell.

**Measure.** For each timing-task trial, the six output latencies in seconds (`Out sec 1` … `Out sec 6`; `Rhythm?` = 1 marks timing trials; `Grouped?` = 0/1 marks instruction; `Subject` is the participant). For each participant and instruction condition: average each latency over the 20 trials; fit a second-order polynomial (latency on position) to the mean latencies at positions 2, 3, 5 and 6; the measure is the mean 4th latency minus the polynomial's prediction at position 4. File: `d03.csv` (one row per trial).

**Sample and exclusions.** Adults from a university participant pool, native or fluent English speakers, paid; planned N = 40. Protocol exclusions: participants who could not complete the session (software crash), participants who report knowing the hypothesis, and participants whose order-task accuracy is low enough to show non-cooperation. The posted file holds only the retained 40 participants; no further exclusions.

**The test.** Paired-samples t-test, two-sided, of the 4th-latency deviation, grouped vs ungrouped, df = 39; effect size Cohen's d computed as the mean difference over the root mean of the two conditions' variances (d_av). Not the key test: the 2 (instruction) × 6 (position) repeated-measures ANOVA interaction on raw latencies, a less specific second test of the same claim that the protocol also planned.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d03.csv` (CSV, 707 KB): 3200 rows 40 columns trial-level; xlsx twin (2.5 MB) not downloaded
<!-- files:end -->
