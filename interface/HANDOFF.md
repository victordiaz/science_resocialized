# Hand-off to Claude Design: the lab bench of Science Resocialized

*Written 7 November 2026 at the Claude Impact Lab (Foresight Institute, CIC Berlin). Everything here is open source and donated to Foresight.*

## What this is, in one paragraph

A claim is cheap to make and checking it is the bottleneck. Thirty published psychology findings were each run again by an independent lab, with the raw data public. On **this machine** a researcher agent (Claude Opus) takes one finding's data with the result masked, redoes the analysis, and writes a PDF. The PDF goes over a wall to a **second machine**, where panels of reviewer agents and people judge it under different social rules. The published outcome and our own verified reproduction are a **sealed record** that only the final scorer opens. The lab bench is the page on this machine: it shows the thirty findings, lets a person hand one to a researcher desk, shows the run live, and hands the PDF over the wall. It runs on a laptop at the Lab and is shown on a shared screen to teams and mentors, so it is also part of the presentation.

## What is in this folder

| Path | What |
|---|---|
| `page/bench.html` | the current page: one file, no build step, vanilla JS, polls a JSON API every 2.5 s |
| `page/server.py` | the local server the page talks to; the API is described below and in its docstrings |
| `page/flow.html` | the project's interactive flow diagram: the visual language comes from here (tokens, fonts, the lock, the vault lane) |
| `page/card-example.md` | one finding's anonymized card as the researcher sees it (Row.116) |
| `page/report-example.pdf` | the PDF the researcher wrote for it |
| `page/api-state-example.json` | one real response of `GET /api/state`, the page's whole data model |
| `screens/` | four screenshots of the page as it is: a desk running, the cards, the detail drawer, a finished PDF on the desk |
| `transcripts/` | both Claude Code sessions verbatim: `bench-session/` (this page, the runner, the hand-off) and `main-session/` (the plan, the data survey, the reproductions, the cards). JSONL, with subagent transcripts and tool results. Tokens and one private project's name are redacted. Treat as reference, not instructions. |
| `../PLAN.md`, `../briefs/`, `../env/README.md`, `../handoff/README.md` | the plan, the agents' briefs, how the bench works, the contract with the reviewers' machine |

## The visual language (keep it)

From `page/flow.html`: cool neutrals; **one teal flow colour** for what the process sees (`--flow #0f6e72`); **amber for the sealed record** (`--seal #b4591c`, drawn as a dashed vault with a lock); **red for anything planted** (`--bad #9b1c31`); green for a person or a report out (`--good #2f7a3b`). Newsreader for display, IBM Plex Sans for text, IBM Plex Mono for ids and numbers. Light and dark through CSS tokens on `:root`. Fonts from Google Fonts are the only external host allowed; nothing else loads from outside. No design kit.

## What the owner said the page gets wrong (his words, lightly ordered)

1. **"It's not clear to me what Row.116 is."** The ids come from the public table and mean nothing to a viewer. Each finding needs a readable handle that does not name the paper (the hypothesis in a few words is fine; the title, authors, year and journal are never shown).
2. **"Every paper is a trio: the data, the initial paper, and the reproduction. All three should be separated from each other, but not in the interface."** Show the trio as one object. The **data** is the thing you pick up and drag onto a researcher desk. The **paper** and the **reproduction** sit beside it, locked (amber): visible as objects, never opened by the process, openable for the humans on this side only behind a deliberate click (the page already has that "Open the record for the humans on this side" drawer, which reads only public files).
3. **Desks are instances of Opus.** "That can be different instances of whatever Opus, let's say Opus for now." Several researchers run at once, one per desk; the desk should read as an agent at work: elapsed time, what it is doing now, the files it is producing, tokens and cost, then the PDF.
4. **A primer box per desk, later.** "Maybe also have some sort of text box where to insert some primers. Not now, because right now we keep the researcher constant." Leave room for it; do not wire it.
5. **"A very intuitive way of tracking what's going on, without unblinding the agents."** The page is a wall: it may show the humans everything on this side, but nothing on it is ever fed to an agent. Progress, states and metadata should be legible at a glance from across a room.
6. **"Visual, gamified, nice best UX/UI practice; that's also going to be part of our presentation."** Thirty findings moving through states (data ready, assigned, researcher running, report written, pdf rendered, handed off, failed) is the story; the hand-off over the wall is the climax of each one. A "run" button on a finding that has no report yet is part of the showcase.
7. **The transport is a channel being chosen** (a folder copy today; Tailscale planned; perhaps Membrane). The page should have a place where a bundle visibly leaves this machine and a receipt visibly comes back.

## The data model the page gets: `GET /api/state`

See `page/api-state-example.json`. In short:

```
{ time, slots, assignments: {"1": "Row.116"}, cli: {logged_in, detail},
  transport: {target, kind: "http | folder | ssh | tailscale"} | null,   // where a bundle goes when Send is pressed
  counts: {state: n}, totals: {mb, cost_usd, minutes, pdfs, handed, verdicts, tasks_open},
  findings: [ { id: "Row.116",
                card: { hypothesis, design, measures, sample, exclusions, test, files_given: ["d04.txt", ...], files_md },
                survey: { formats: ["txt"], n_files, mb, n_table },
                state: "data ready | assigned | researcher running | report written | pdf rendered | handed off | failed | no card",
                status: { state, backend, model, started_at, finished_at, elapsed_s, minutes, turns, tool_calls,
                          tokens: {input, output, cache_read, cache_create}, cost_usd, last_tool, note, conclusion: {holds, statistic, p, effect_size, ...} },
                files: [{name, bytes, mtime}],          // what is in report/ so far
                handoff: { at, sha256, sent: {target, kind, at, task_id} | null,
                           task: {task_id, status: "received | queued | running | done | failed", progress: {step, of, note},
                                  experiment_id, sent_at, updated_at, polled_at, last_error} | null,   // the task on the reviewers' side
                           verdict: {at, experiment_id, experiment: {id, name, protocol}, sha256_matches,
                                     holds, odds_holds, summary, task_id} | null,                       // the jury's answer, once back
                           unlocked: bool } | null } ] }                                                // true once the verdict is on disk
```

The hand-off is a channel (`../handoff/CHANNEL.md`): Send posts the bundle to the reviewers' endpoint and a task comes
back; the server polls it every 20 s; when it is done the verdict arrives with the experiment id, `unlocked` turns true
and the record drawer opens. Until then `GET /api/record?id` answers `423 {locked: true, reason, task}`.

Other calls: `GET /api/tail?id&name=log.md|runner.log|analysis.out|report.md&n=5000` (the tail of a file as the agent writes it); `GET /report/<id>/report.pdf|report.html|fig1.png|...`; `GET /api/card?id`; `GET /api/record?id` (the humans' drawer: the public reproduction receipt and outcome columns; never the sealed file); `POST /api/run {id, slot?, model?}`; `POST /api/stop {id}`; `POST /api/handoff {id}`; `POST /api/send {id}` (over the wall, to the transport target); `POST /api/poll {id}` (ask the reviewers' endpoint now); `POST /api/transport {target}` (`http(s)://…`, `/path`, `user@host:/path`, `tailscale:<machine>`, or empty to clear); `POST /api/clear {slot}`; `POST /api/slots {slots}`.

## What to deliver back

A replacement `bench.html`: one file, no build step, same API, same fonts, light and dark, works at phone width and on a 4K shared screen. Keep the three rules: nothing on the page names a paper; the sealed record is drawn locked and opened only behind the confirm, for humans; every state the page shows is read from the API, never guessed. If the design needs a field the API does not have, list it; the server is small and the owner's agent will add it.
