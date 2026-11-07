# env: the lab bench (target side)

The researcher side of the experiment on one page. A researcher agent takes one anonymized finding (the card and the raw
data, nothing else), redoes the analysis, and writes a report that becomes a PDF; the PDF is handed to the reviewers'
machine. The page shows the choosing, the hand-off and the progress, and it never reads the sealed record.

## Start it

    .venv/bin/python -I env/server.py            # http://127.0.0.1:8765/

The `claude` CLI must be logged in for the runner to start an agent (`claude auth status`; if not, `claude auth login`
once in a terminal). The page shows the CLI's state top right and retries every two minutes.

## Use it

- The thirty cards are the studies under `papers/S##/`, each read from `card.md` (the hypothesis, design, sample, the
  data files given) and `data/MANIFEST.json` (formats, file count, size). Each shows its state: data ready, assigned, researcher
  running, report written, pdf rendered, handed off, failed.
- Drag a card onto a desk, or press "Hand to a researcher": the server starts `env/run_researcher.py <id>` and the desk
  shows the run live: elapsed time, turns and tool calls, tokens, cost, the last tool call, the tail of `runner.log`,
  `log.md`, `analysis.out` or `report.md`, the files appearing in `report/`, and the finished PDF in place.
- "Hand off" packs the bundle (`env/handoff.py`) into `handoff/<id>/` with hashes; see `handoff/README.md` for the
  contract with the reviewers' machine.
- "Details" opens the full card and the run's record. The published outcome and the reproduction are not on this
  machine at all: they live in the operator repository, which shares no history with this one.
- "Send over the wall" (on a handed-off desk) moves the bundle to the transport target set in the header pill:
  `user@host:/path` (rsync over ssh; a Tailscale host name works once both machines are on the tailnet), `/local/path`
  (a folder copy), or `tailscale:<machine>` (`tailscale file cp` of a zip). The receipt is `handoff/<id>/sent.json`.
  On the other side, `handoff/receive.py <inbox> --verdicts` verifies every bundle's hashes and every receipt written back.
- "+" and "−" change the number of desks; several researchers run at once, one per desk.

A page reload loses nothing: the desks are in `env/state.json`, each run in `papers/S##/report/status.json`.

## Files

| File | What |
|---|---|
| `server.py` | the local web server: the page, `/api/state`, `/api/run`, `/api/stop`, `/api/handoff`, `/api/tail`, `/report/<study>/<file>`. Every finding path goes through `common.safe_finding_file`, which refuses sealed file names. |
| `bench.html` | the page; no build step; fonts from Google Fonts as in `diagram/flow.html`, nothing else external |
| `run_researcher.py` | runs one researcher agent for one study in a sealed sandbox at `env/runs/<study>/` (see below); writes `report/status.json`, `report/runner.log`, `report/runner.jsonl`, `report/work.json`, `report/PROMPT.md`; syncs the agent's `report/` into `papers/<study>/report/`; renders `report.pdf` with `score/md2pdf.py`; records tokens and cost from the CLI's stream |
| `handoff.py` | packs `handoff/<study>/` and updates `handoff/MANIFEST.json`; `--verify` recomputes the hashes; `--zip`; `--send <target>` (rsync to a path or host, or `tailscale file cp`), writing `sent.json` |
| `common.py` | paths, the card parser, the state of a finding from disk, `safe_finding_file` |
| `state.json` | the bench's state: desks, runs and the transport target (git-ignored) |
| `runs/` | the sandboxes (git-ignored) |

## The seal, as the runner enforces it

The agent never sees `papers/<study>/` itself. The runner builds `env/runs/<study>/` shaped like the repo:
`briefs/research-brief.md`, `score/md2pdf.py`, `.venv` (a symlink), `papers/<study>/card.md`, `papers/<study>/data/`
(as it is: neutral names and the manifest; the replication's report, scripts and codebooks were withheld on the operator
side before export) and an empty `report/`. What was given is recorded in `papers/<study>/report/work.json`. The run
refuses to start if anything named `truth.json`, `files.json`, `survey.json` or `reproduction.json` is reachable from
the sandbox (none exists in this repository; the guard stays) or any symlink leads back into the repo. The CLI runs
with `--setting-sources ""` (no user settings, plugins or hooks), `--strict-mcp-config`, no web tools, no network for
Bash, and Claude Code's filesystem sandbox denying reads of `.git/`, `handoff/`, `env/runs/`, the operator repository on
the same laptop, and the user's Claude transcripts. `--dry-run` builds and checks the sandbox and prints the command;
`--attach` builds it and waits for an outside agent to write the report there (used when the CLI is logged out; the
status then says backend `attached` and carries no token counts).

The researcher's prompt is `briefs/research-brief.md` with a preface saying where it is; the exact text is kept in
`papers/<study>/report/PROMPT.md`.
