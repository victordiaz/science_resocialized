# Paper Review: AI-persona + human annotation of research PDFs

Date: 2026-11-07
Status: draft for approval

## Intent

A web app where research papers (PDF) are reviewed by a panel of AI reviewer
personas and by humans, side by side, as anchored comment threads on the PDF.
Agents act autonomously through an API; humans use a normal PDF-annotator UI.
The point is to get structured, multi-perspective critique of a paper, have the
personas challenge each other, and let a human interrogate any claim and get an
answer immediately.

## Goals

- View a PDF and see all comments anchored to regions (text passages, figures,
  equations, tables) on its pages.
- Threaded comments: anyone (persona or human) can reply to any thread.
- Manage personas in the app: create / edit / delete, each with name, color,
  prompt, and model.
- "Run review" on a paper: one Claude agent per selected persona, in parallel,
  writing comments through the API.
- Optional discussion rounds where personas read each other's comments and reply.
- Live replies: when a human addresses a persona, it answers right away.
- Everything agents do goes through a documented HTTP API, so external agents
  (later: an MCP wrapper) can do the same.
- Ships with one example paper preloaded so the agent flow can be seen at once.

## Non-goals (v1)

- MCP server (later, as a thin wrapper over the HTTP API).
- User accounts / login / multi-tenant permissions.
- Editing the PDF itself or exporting annotations back into the PDF file.
- Building the external agent pipeline; this app is where agents write, and it
  has its own built-in runner.

## Anti-goals

- Agents talking to each other in unbounded loops or spending money without the
  human starting it.
- Agents having to understand raw PDF internals (coordinate systems, content
  streams). They get images, words-with-positions, and one simple anchor format.
- Anchors that drift or misalign between what the agent saw and what the human
  sees.

## Constraints

- Runs locally on the user's machine for now; must be a normal web app
  (backend server + browser frontend) deployable elsewhere later. No
  localhost-only assumptions baked into the frontend (API base URL configurable).
- Anthropic API key supplied via local config / env var, never sent to the
  frontend.

## Decided: how it works

### Core concepts

- **Paper**: an uploaded PDF, with a title, page count, and per-page size.
- **Persona**: name, color, system prompt, model (default `claude-sonnet-5-5`, editable),
  enabled flag. Personas are authors of comments.
- **Human author**: v1 has no login. The human is a single local user with a
  display name set in settings (field kept so multiple humans can exist later).
- **Thread**: a root comment with an anchor, plus replies. Status: open / resolved.
- **Comment**: author (persona or human), body (markdown), timestamps, optional
  parent (for replies). Root comments carry the anchor.

### Anchor format (the single way to point at the PDF)

```
anchor = {
  page: int,                  # 1-based
  rects: [{x0, y0, x1, y1}],  # fractions of page width/height, 0..1, top-left origin
  quote: string | null        # text found inside the rects, if any
}
```

- Same normalized coordinate space for page images, word positions, and anchors.
  A rect drawn on a rendered page image converts trivially at any resolution.
- Paper-level comments (no region) are allowed: `anchor = null` / page-only.
- Agents can create anchors two ways:
  1. **By box**: give `page` + `rects` directly (e.g. after looking at the
     page image and boxing a figure).
  2. **By text**: give `page` + `quote` (or word index range); the server finds
     the words and computes `rects` from word positions. Error if not found.
- Humans create anchors by selecting text (→ rects from selection + quote) or
  dragging a rectangle (→ rect, quote filled from words inside it).

### PDF processing

- On upload, the backend (PyMuPDF) extracts per page: size, and words with
  normalized bboxes (in reading order, with block/line indices). Stored so agent
  reads are cheap.
- Page images rendered on demand at a requested DPI (cached).
- Frontend renders the PDF with PDF.js (text layer enabled for selection) and
  draws anchors as an overlay using normalized coords.

### Agent-facing HTTP API (also used by the built-in runner)

Authentication: each persona has an API key; requests from the built-in runner
use it too. Human UI calls are unauthenticated in v1 (local). Rough surface:

- `GET  /papers`, `POST /papers` (upload), `GET /papers/{id}` (meta, pages)
- `GET  /papers/{id}/pages/{n}/image?dpi=` → PNG
- `GET  /papers/{id}/pages/{n}/text` → words with bboxes, plus plain text
- `GET  /papers/{id}/text` → full plain text with page markers (cheap first read)
- `GET  /papers/{id}/threads` (filters: author, page, status)
- `POST /papers/{id}/threads` (anchor + body) — create root comment
- `POST /threads/{id}/replies` (body)
- `PATCH /threads/{id}` (status)
- Personas CRUD, review runs (start / status / cancel)

An OpenAPI spec is generated (FastAPI) and is the contract for external agents.

### Built-in agent runner

- Each persona run = a Claude tool-use loop with tools mirroring the API:
  `read_full_text`, `get_page_text`, `view_page` (returns image),
  `list_threads`, `create_comment` (by box or by quote), `reply`.
- System prompt = a fixed base prompt (how to use tools, anchor rules, be
  specific, cite location) + the persona's prompt.
- Runs execute in parallel per persona, in the backend process (background
  tasks). Each run has a per-persona step/turn limit to bound cost.
- Progress (per persona: status, steps, comments written) and new comments
  stream to the UI live (server-sent events or websocket).

### Two interaction rules

1. **Review runs — agents talk to each other only when you start it.**
   "Run review" on a paper: pick personas, pick discussion rounds (0..N,
   default 1).
   - Round 0: each persona reviews independently. Personas in this round do
     not see each other's in-progress comments (to keep them independent).
   - Rounds 1..N: each persona reads all threads and replies where it agrees,
     disagrees, or adds something; may also respond to human comments.
   - A discussion-only run (no round 0) can be started later, e.g. after
     humans have added comments.
   - Runs are cancellable and always end after the chosen rounds.
2. **Live replies — agents answer you whenever you talk to them.**
   - Human replies in a thread whose root author is a persona → that persona
     answers in the thread.
   - Human @mentions a persona in any comment → that persona answers.
   - Agent comments never trigger other agents live. Agent-to-agent only
     happens inside review runs.

### UI

- **Library**: list of papers, upload.
- **Paper view**: PDF on the left with anchor overlays colored by author;
  thread sidebar on the right (sorted by page position), filter by persona /
  human / status; click thread ↔ scroll to anchor. Highlight text or drag a
  box to comment. Reply box with @mention autocomplete. "Run review" panel with
  live per-persona progress.
- **Personas**: list, create/edit/delete (name, color, prompt, model, enabled).
- **Settings**: human display name; API key status (set via config, not UI).

### Visual design (2026-11-07)

The UI follows the "Review Room" design canvas
(https://claude.ai/artifact/GgouWAs9U4Z8qYWuf2B1J8): four screens, Paper workspace,
Papers library, Personas, Run review. Warm neutral background `#F3F2EE`, ink
`#1B1C1F`, accent `#1F5FD6`; Inter for UI, Space Grotesk for headings, Source Serif 4
for quoted paper text, JetBrains Mono for model tags and prompts. Persona palette:
blue `#1F5FD6`, teal `#0B7285`, orange `#B4410B`, purple `#6741D9`, raspberry
`#A61E4D`, green `#2B8A3E`; humans `#495057`.

- Workspace: page-thumbnail rail with open-thread counts; toolbar with Highlight
  text / Draw box, page pager and zoom; numbered markers on the PDF; thread panel
  scoped to the current page (toggle to all pages), Open/Resolved tabs, author chips.
- Run review is its own page: reviewers, discussion rounds 0-3, per-round stage
  bars, one lane per persona with what it is doing now, and a live log of the API
  calls the agents make (recorded in `run_events`).
- Comments show a persona's current name and color; deleted personas keep the
  name and color the comment was written with.

### Stack (builder's call, stated to the user)

- Backend: Python, FastAPI, SQLite, PyMuPDF, official Anthropic Python SDK.
- Frontend: React + Vite + TypeScript, PDF.js.
- Single repo, backend serves the built frontend in production mode.

### Seed data

- One example paper downloaded from arXiv: "Attention Is All You Need"
  (arXiv:1706.03762) — has figures, equations, and tables to exercise anchors.
- Four starter personas, all on `claude-sonnet-5-5`: Methods Skeptic, Domain
  Expert, Clarity Editor, Figure Inspector (reviews figures/tables visually).

## Calls made after builder review (author's calls, user may override)

- **External agents are personas.** Persona has `kind: builtin | external`.
  Built-in personas have prompt + model and are run by the app; external
  personas only have name/color/API key (key shown once in the UI on creation,
  regenerable). In v1 keys identify authorship, not security. Live replies to
  an external persona are not answered automatically (v1); the thread simply
  shows as awaiting their reply. Webhooks/MCP notifications are later work.
- **Visibility in runs.**
  - Round 0: a persona sees human comments and its own earlier comments on the
    paper (so a re-run doesn't duplicate itself), but no other persona's
    comments, from this run or earlier ones.
  - Rounds 1..N: personas run in parallel against a snapshot of all threads as
    they stood when the round started; replies written during a round become
    visible next round. Runs record round start times to filter on.
- **Threads are flat**: root comment + ordered list of replies (no nesting).
  Each reply may carry an optional `reply_to` comment id, set when you click
  "reply" on a specific comment. Live-reply target = author of the
  `reply_to` comment if it's a built-in persona, else the root author; any
  @mentions add further targets.

## Left to the builder

- Exact DB schema, endpoint naming, SSE vs websocket.
- Base agent prompt wording and step limits (sane defaults, configurable).
- Image DPI defaults, caching strategy.
- UI styling and layout details.

---

# Part 2: Blind replication (2026-11-07)

## Intent

Besides reviewing a paper, test its main result by replication: extract the main
experiment, give it **blind** (no results, no paper) to a coding agent that actually
replicates it, then have agents verify the replication against the paper. The
verification reports are readable by other agents (the reviewer personas) and humans.

## Decisions

From the user:
- The replicator is Claude Code run headless (`claude -p`) in its own folder, and
  actually builds and runs the experiment. Resources are available; start with small papers.
- Blindness: the replicator gets the experiment without outcomes and is told not to
  use the internet to look up the paper or its results.
- Verification output is a free-form written report ("artifact"); no fixed format.
- Runs on this machine for now, but the execution side must be modular so it can
  move to another computer.

Builder's calls:
- **Pipeline, fully automatic**: extract → leak check → replicate → verify. It stops
  for a human only when the leak check finds the spec gives away results (UI: edit the
  spec, or start anyway).
- **Data**: `experiments` (spec shown to the replicator, hidden outcome, leak check),
  `replications` (one blind run of an experiment), `verifications` (one report each).
  An experiment can be replicated several times (e.g. after editing its spec), and a
  replication verified several times.
- **Worker boundary**: the app never starts Claude Code itself. It queues replication
  jobs; a standalone worker script (`worker/replicate_worker.py`, stdlib only, no app
  imports) claims jobs over HTTP with a worker token, runs Claude Code in
  `<workdir>/<replication id>/`, streams progress events back, and uploads the report
  and source/output files when done. The app starts one local worker by default; another
  machine runs the same script pointed at the app URL.
- **Claude Code flags**: `-p --output-format stream-json --verbose`,
  `--tools Bash,Read,Edit,Write,Glob,Grep` (no web tools), `--permission-mode
  bypassPermissions` (unattended; it runs code on the worker machine), `--bare`,
  `--max-budget-usd` and a wall-clock limit, `--append-system-prompt` with the blind rules.
  The replicator writes `REPORT.md` (what it did, results) in its folder.
- **Agents in the app** (Claude API, like reviewers): Extractor (paper tools +
  `submit_experiment`), Leak checker (one call), Verifiers (chosen personas; paper tools +
  experiment + replication files incl. images + `submit_report`). Reviewer personas get a
  `read_replications` tool so reviews can cite verification reports.
- **UI**: a Replicate page per paper: start (verifier picks, budget), the extracted
  experiment (spec, hidden outcome collapsed, leak check), each replication (status,
  live log, report, files), and verification reports.
