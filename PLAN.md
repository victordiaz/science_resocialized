# Science Resocialized: the first experiment

*Plan written Saturday 7 November 2026 at the Claude Impact Lab (Foresight Institute, CIC Berlin). Version 1 at 13:10 asked judges to predict replication outcomes; version 2 at 13:45 moved to reproduction from data after the recall problem was judged unfixable by masking; version 3 at 14:20 is the design as it will run: a researcher agent works from masked data, a panel reviews its report. Open source; donated to Foresight. The interactive flow is `diagram/flow.html`.*

## 1. The question

A claim is cheap to make now and checking it is the bottleneck. Published psychology findings were each run again by an independent lab, and the replication's raw data, analysis script and outcome are public. Here, a researcher agent receives that data with the result masked, reaches its own conclusion, and writes a report. A panel of reviewer agents marks the report and gives a verdict: does the conclusion hold? The panel's structure is the variable: who commits first, who sees whom, who may revise, which primitives they run on (track record, escalation, a devil's advocate), and whether a bad actor or an incentive is pushing them. Only the scorer opens the sealed record.

The question in one line: **which social structure for review lands on the truth most often, at what cost, and how much does a bad actor move it?**

## 2. The data

**Source.** The Reproducibility Project: Psychology (Open Science Collaboration, 2015). The table `RPPdataConverted.csv` from https://github.com/CenterForOpenScience/rpp, folder `data_allformats`, read and copied on 2026-11-07; its SHA-256 is in `data/raw/rpp/SHA256SUMS`. The table has 168 rows, 99 of which carry an outcome in `Replicate.R` (38 yes, 61 no). Each replication is an OSF component with three children: Data, Materials and Analysis Audit; the last holds a standard R script that recomputes the key statistic. The census of all 99 is `data/census/osf-files.json` (mechanical; 96 have a Data child with files and an audit script).

**The survey.** Eight Opus agents, twelve findings each, open every data file and the audit script and write one receipt per finding (`data/survey/<Local.ID>.json`): usable, unclear or unusable, with row counts, the variables the key test needs and whether each is present, a recomputation where one was possible, and what was opened. The brief is `briefs/survey-brief.md`. Only **usable** findings go on.

**The reproduction.** One Opus agent per usable finding recomputes the key statistic twice, by running the audit script and independently in Python, and writes a receipt with the table's number, the script's and its own (`data/findings/<Local.ID>/reproduction.json`; brief `briefs/reproduce-brief.md`). This is the ground truth beside the published outcome. A finding whose three numbers disagree is kept and marked; the disagreement is itself a result.

**One folder per finding**, `data/findings/<Local.ID>`:

| File | What | Who sees it |
|---|---|---|
| `card.md` | the claim as a question, the design, the sample; no title, authors, journal, year, institution, and no result | the researcher, then the panel |
| `download/` | the replication's raw data as fetched from OSF (git-ignored; the receipts carry the hashes) | the researcher, then the panel |
| `report/report.pdf` | the researcher agent's report: conclusion, method, numbers, one figure | the panel |
| `report/log.md` | every command the researcher ran | the record |
| `panel/<structure>/` | each reviewer's odds and reasons, before and after the board | the record |
| `truth.json` | the published outcome, the replication's statistic, our verified reproduction, and which reviewer was planted | sealed until scoring |

The seal is a rule of the scripts, not secrecy: the data is public. No researcher or reviewer prompt includes `truth.json` or any file that names the paper; the scoring script reads `truth.json` only after every verdict is on disk.

**Two larger pools for a second round**: the Altmejd et al. (2019) set of 131 direct replications across four projects (OSF `4fn73`), and FORRT's Replication Database (over 1,600 replication results).

## 3. Recall, and why the seal is enough here

The RPP findings are famous. A model has read the paper that lists their outcomes; so has anyone who follows the replication literature. In the first version of this plan that was fatal: masking a card cannot hide a finding whose procedure is its fingerprint.

In this design the researcher's job is to compute, not to remember. A researcher that writes "this effect is known not to replicate" without the numbers has written a bad report, and the panel is told that a conclusion not carried by the analysis in front of them does not hold. The reviewers' job is to check the report against the data, not against the literature. Recall still helps a reviewer who knows the published statistic, so two things are recorded: a recall probe before the panel runs (the solo model is shown each card and asked whether it recognises the study and what the replication found; `results/contamination.json`), and every score reported on all findings and on the unrecognised subset.

## 4. The researcher

One Opus agent per finding, fresh context. It receives `card.md` and `download/`, the Python environment and R, and a page limit. It decides how to test the claim, runs the analysis, states its conclusion with the numbers, and exports `report.pdf` (Markdown to PDF by script; one figure at most). It writes `log.md` as it goes. It is not told what the original lab found or what the replication found. Its brief is `briefs/research-brief.md`.

A researcher may be wrong on its own, which is the natural source of reports that do not hold. If too few are wrong to score a panel, a planted wrong report is added with the error recorded in `truth.json`, and the two kinds are scored apart.

## 5. The panel

Reviewer agents read the report, may reopen the data and rerun the analysis, and give odds that the conclusion holds, as a number between 0 and 1, with reasons. The structures compared:

| Structure | Who | Rules |
|---|---|---|
| **Solo** | one reviewer | reads, judges, no board |
| **Agents under rules** | five reviewers, one model, separate contexts | each commits before seeing the others; the board shows the four others' odds and reasons without names; one revision, with a line saying why |
| **People with agents** | three to five people, each with an agent | the same rule, on a shared page built on the day; minutes counted |

**Primitives, switched on one at a time where the day allows:** a track record (a reviewer's weight on the board set by its past agreement with the record, starting equal); escalation (a finding where the panel is unanimous or evenly split goes to a person); a devil's advocate (one reviewer per finding told to argue against the first-round majority as strongly as the evidence allows, and to give its honest odds anyway).

**Bad actors and incentives, planted and recorded in `truth.json`:** a reviewer told to push a chosen verdict regardless of the report; a reviewer rewarded for agreeing with the majority; a reviewer told the researcher is a colleague. Each structure runs clean and with one planted condition, so the cost of a bad actor is a number per structure.

**Aggregate.** The structure's odds for a finding are the mean of the revised odds; the median and the log-odds pool are recorded beside it. The mean is named in advance as the answer.

**Cost.** Every call is logged with input and output tokens and the price at the time of the run; the people's arm logs minutes.

## 6. Scoring

One script, `score/score.py`, run once. It reads every structure's odds from the finding folders, opens `truth.json` for each, and writes `results/table.md` and `results/table.json`:

| Structure | Condition | n | Accuracy | Brier | Accuracy (unrecognised) | Cost |
|---|---|---|---|---|---|---|
| Base rate | | n | | | | 0 |
| Solo | clean / planted | | | | | |
| Agents under rules | clean / planted | | | | | |
| People with agents | clean / planted | | | | | |

"Holds" is true when the researcher's conclusion agrees with the published outcome and with the verified reproduction. Accuracy is the odds rounded against that; the Brier score is the squared distance from it. A 95% interval on accuracy from the binomial goes beside every figure: on thirty items one accuracy figure is uncertain by about 17 points either way. The base rate is said first.

## 7. Order of work

0. Repository, raw data with hash, the census of the 99 OSF components. *Done by 13:55.*
1. The survey, eight Opus agents, receipts per finding. *Running from 14:05.*
2. The reproduction, one agent per usable finding; the cards written from the receipts.
3. The researcher runs; reports to PDF; `truth.json` sealed.
4. The recall probe; the solo panel.
5. Agents under rules, clean, then with one planted condition.
6. The board; the people's session in the afternoon.
7. `score.py`, the table, the README in the order: question, method, table, limits.

Each step ends with files on disk that the next step reads; no step passes anything by hand.

## 8. Limits, said first

- A pilot. At most thirty findings, one afternoon; the count is whatever the survey and the reproductions allow.
- Recall. The dataset is famous; the seal keeps the result out of the process, the probe measures what leaks in, and the unrecognised subset is scored apart.
- The researcher and the reviewers are one model family on one day. The finding is about the structure, not the model.
- A planted condition changes one thing against the clean run of the same structure, and nothing else.
- The people's arm is not blind to the agents' runs; the board shows people only people, after commit.

## 9. The bigger picture this is a brick of

A network of such rooms, each a node; each claim carrying odds that move as evidence comes in; the weight of a checker's word set by a track record kept under a name the system holds apart from the person; escalation of split or unanimous claims to people; watchers that reopen sources and flag everything downstream when something upstream moves. Today's table is the smallest piece of that which can be checked against a record. `arms/arm3_people/PROPOSAL.md` says what the next piece would be.
