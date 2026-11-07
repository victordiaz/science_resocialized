# The hand-off: from the researcher's machine to the reviewers' machine

This folder is the wall between the two halves of the experiment. On this side a researcher agent worked from a
finding's card and raw data and wrote a report. On the other side a panel of reviewers marks that report. Nothing in a
bundle names the paper, the authors, the journal or the result; the sealed record (kept in the operator repository)
is not in this repository at all, and nothing derived from it crosses.

## What a bundle contains: `handoff/<study>/`

| File | What | Who wrote it |
|---|---|---|
| `report.pdf` | the researcher's report: question, sample after exclusions, test, statistic, p, effect size, one figure at most, the conclusion in one sentence | the researcher agent, rendered by `score/md2pdf.py` |
| `report.md` | the same text as Markdown | the researcher agent |
| `log.md` | the researcher's plan before the data, the recognition line if any, every command it ran, any change of plan | the researcher agent |
| `card.md` | the claim as a hypothesis, the design, the measures, the sample, the exclusions, the named test; no title, authors, year or result | the reproduction agent |
| `manifest.json` | ids, SHA-256 and size of every file, the time, the researcher's model, backend, tokens, cost and minutes, the conclusion it stated (`holds`) | `env/handoff.py` |
| `data/` | the raw data as the researcher saw it: `papers/<study>/data/` under its neutral names (`d01.sav`, `d02.csv`) with `MANIFEST.json`; the replication report, audit script, syntax and codebooks were withheld before export | `env/run_researcher.py` (the sandbox copy) |

`data/` is git-ignored here (135 MB over thirty findings) and must travel by folder copy; its hashes are in
`manifest.json` under `data_files`, so the reviewers' side can verify what it received. `handoff/MANIFEST.json` lists
every bundle written, with the time, the PDF's hash, the model and the cost.

Verify a bundle on either side with:

    .venv/bin/python -I env/handoff.py S01 --verify

or, without this repo, by recomputing `shasum -a 256` of each file against `manifest.json`.

## What the reviewers' side must write back: `verdicts/<study>/<structure>/<reviewer>/round1.json` and `round2.json`

`structure` is one of `solo`, `rules`, `people`, with a suffix for a planted condition (`rules_pushed`,
`rules_majority`, `rules_colleague`, `rules_advocate`, `rules_track`, `rules_escalation`). `reviewer` is `R1` to `R5`
for agents, `P1` to `P5` for people. The schema is the receipt in `briefs/review-brief.md`:

```json
{"reviewer": "R3", "round": 1, "study": "S01",
 "odds_holds": 0.0,
 "reasons": [{"claim": "the exclusion of 4 participants is not explained", "where": "report p.1, log line 12", "mark": "not on the page"}],
 "recomputed": {"attempted": true, "what": "the primary test from the data", "result": "t(27)=..., p=...", "agrees_with_report": "yes | no | partly"},
 "recognised_study": false,
 "round2_change": null,
 "minutes": 0}
```

`round2.json` has `round: 2` and `round2_change` set to one line saying why the odds moved or stayed. A structure that
has no second round writes `round1.json` only. Beside the receipts, the reviewers' side writes
`verdicts/<study>/<structure>/board.md` (the anonymised board shown in round 2) and, for the people's arm,
`verdicts/<study>/people/minutes.json` with the minutes each person spent. The scorer (`score/score.py`) reads
`verdicts/` from this folder once every receipt is on disk, and only then opens the sealed record.

Nothing the reviewers write back may name the paper. A reviewer who recognises the study says so in the receipt
(`recognised_study: true`) and that is all; the scorer reports every number on all findings and on the unrecognised
subset.

## How a bundle travels

The bundle is a folder; any transport that preserves bytes works, and the hashes check it on arrival. Three are
supported today, in order of what is in place:

1. **Folder copy.** Copy `handoff/<study>/` (with `data/`) to the reviewers' machine by a USB stick, AirDrop or a
   shared folder; copy `verdicts/` back the same way.
2. **Git.** `handoff/` is committed to this repository without `data/`; the reviewers' machine pulls it and fetches
   the data by folder copy once. Verdicts come back as a commit under `handoff/verdicts/`.
3. **A tailnet (planned channel).** With both machines on the same Tailscale network (the bench's header pill holds the target and the desk's "Send over the wall" button runs it):
   `env/handoff.py S01 --send user@reviewers:/path/to/handoff/` rsyncs the bundle over the tailnet, and
   `env/handoff.py S01 --send tailscale:reviewers` sends `handoff/S01.zip` with `tailscale file cp`. Verdicts
   come back the same way into `handoff/verdicts/`. Neither has been exercised yet on the day; the rsync path is the
   one to try first. A Membrane node could wrap the same bundle and receipt later; the bundle format does not change.

On arrival, `receive.py` (copied with every send; standard library only) checks the bundles and, with `--verdicts`, the
receipts written back:

    python3 receive.py /path/to/inbox --verdicts

It exits 1 if a hash differs, a sealed file is present, or a receipt lacks a field of the schema. The local round trip
(send to a folder, receive, write a receipt, receive again) was exercised on 7 November; the tailnet path was not, as
Tailscale was stopped on the laptop.

Whatever the transport, the rule is the same: the reviewers' machine never holds the sealed record, the survey
receipts, the reproductions or the public table; none of those is in this repository either. It holds bundles and writes verdicts.
