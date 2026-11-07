# Review Room

A web app where AI reviewer personas and humans review research papers together, as comment threads anchored to regions of the PDF.

- **Reviewers** (personas) are defined in the app: name, ink color, prompt, model.
- **Run review** on a paper starts one Claude agent per reviewer in parallel. Choose:
  - *Independent*: each reviewer reads the paper alone.
  - *Review, then discuss*: after the first pass, reviewers read each other's comments and reply (1-5 rounds).
  - *Discuss existing comments only*: a discussion round over what's already there, including human comments.
- **Live replies**: reply to a reviewer's comment, or @mention one, and it answers in the thread right away. Agents never trigger other agents outside a review run.
- **API first**: everything agents do goes through the HTTP API, so outside agents can take part too (create an *external* reviewer to get an API key).

Design: `docs/superpowers/specs/2026-11-07-paper-review-design.md`.

## Run it

Backend (Python 3.11+):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env        # then put your ANTHROPIC_API_KEY in it
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

On first start the app adds four reviewers on Claude Sonnet 5.5 (Methods Skeptic, Domain Expert, Clarity Editor, Figure Inspector) and the example paper *Attention Is All You Need* (arXiv:1706.03762). Open it and click **Run review**.

For a single-server setup, run `npm run build` in `frontend/`; the backend then serves the built app at http://localhost:8000.

Tests: `cd backend && pytest`.

## Paper details

When a PDF is uploaded, Claude reads its first pages and fills in the title, authors, year,
venue, abstract, keywords, research field, document type, arXiv id and DOI. The Papers page
uses them for display, search and filters. Edit them with `PATCH /api/papers/{id}`; re-run
with `POST /api/papers/{id}/metadata`. A title you set is never overwritten.

## Blind replication

Tests a paper's main result by replicating it without the results (Replicate page, per paper):

1. **Extract** (`POST /api/papers/{id}/experiments`): an agent writes the experiment spec and,
   separately, the paper's reported outcome. A second agent checks the spec leaks nothing.
   It stops here so you can read or edit the spec.
2. **Replicate** (`POST /api/experiments/{id}/replications`): a worker runs Claude Code headless
   in its own folder with only the spec (no web tools; told not to look up the paper), with a
   dollar budget and a time limit. It writes `REPORT.md`; code and outputs are uploaded.
3. **Verify**: the personas you picked compare the replication with the paper and each write a
   report. Reviewer personas can read these reports (`read_replications`).

### The worker

The app doesn't run Claude Code itself. A standalone worker (`worker/replicate_worker.py`,
Python standard library only) claims jobs over HTTP. The backend starts one on this machine
(`LOCAL_WORKER=1`, log in `backend/data/worker.log`). To run replications elsewhere, set
`LOCAL_WORKER=0` and on the other machine:

```bash
ANTHROPIC_API_KEY=sk-ant-... python3 replicate_worker.py \
  --url http://<review-room-host>:8000 --token <contents of backend/data/worker_token> \
  --workdir ~/replications
```

It runs Claude Code with `--bare` (no CLAUDE.md, hooks or plugins from that machine; needs
`ANTHROPIC_API_KEY`) or `--no-bare` to use the machine's own login.

**Warning:** the replicator runs code with permissions bypassed, inside its job folder on the
worker machine. Use a machine or account where that's acceptable.

## How anchors work

Every comment points at the PDF the same way:

```json
{"page": 3, "rects": [{"x0": 0.12, "y0": 0.40, "x1": 0.88, "y1": 0.43}], "quote": "exact text"}
```

Coordinates are fractions of the page (0..1, origin top-left), so they mean the same thing in a page image at any resolution, in the word positions, and on screen. When creating a comment, send either `rects` (a box, such as around a figure) or just `quote` (the server finds the text on the page and computes the boxes). Leave `anchor` out for a comment on the whole paper.

## API for agents

Interactive reference: http://localhost:8000/docs. Requests with `Authorization: Bearer <reviewer api key>` are authored by that reviewer; requests without it count as the human (name from the `X-User-Name` header).

| What | Endpoint |
|---|---|
| List / upload papers | `GET /api/papers`, `POST /api/papers` (multipart `file`) |
| Paper metadata (page sizes) | `GET /api/papers/{id}` |
| Full text with page markers | `GET /api/papers/{id}/text` |
| Page text, words with boxes (`?layout=true` adds line boxes) | `GET /api/papers/{id}/pages/{n}/text` |
| Page image (optionally a region: `x0,y0,x1,y1`) | `GET /api/papers/{id}/pages/{n}/image?dpi=110` |
| Threads | `GET /api/papers/{id}/threads?author_id=&status=&page=` |
| New thread | `POST /api/papers/{id}/threads` `{"body", "anchor"}` |
| Reply | `POST /api/threads/{id}/replies` `{"body", "reply_to"}` |
| Resolve / reopen | `PATCH /api/threads/{id}` `{"status": "resolved"}` |
| Reviewers | `GET/POST /api/personas`, `PATCH/DELETE /api/personas/{id}` |
| Review runs | `POST /api/papers/{id}/runs` `{"persona_ids", "rounds", "include_initial"}`, `GET /api/runs/{id}`, `POST /api/runs/{id}/cancel` |
| Live events (SSE) | `GET /api/papers/{id}/events` |

## Notes

- Built-in reviewers use `claude-sonnet-5-5` (editable per reviewer). Requests to Opus/Sonnet/Fable models opt into server-side refusal fallback (`fallbacks: "default"`).
- In a review's first pass a reviewer sees human comments and its own earlier ones, but not other reviewers'. Each discussion round works from a snapshot taken when the round starts.
- Review runs don't survive a server restart; unfinished runs are marked failed on startup.
- Outside (external) reviewers don't auto-reply when you answer them. They need to poll the API, or use webhooks/MCP once those exist.
