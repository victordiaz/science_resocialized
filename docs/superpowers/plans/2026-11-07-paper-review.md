# Paper Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Local web app where AI reviewer personas and humans annotate research PDFs with anchored, threaded comments; agents run from the app and through an HTTP API.

**Architecture:** FastAPI backend owns PDFs (PyMuPDF), SQLite storage, a service layer used by both HTTP routes and the built-in Claude agent runner, and an in-process event bus streamed to the UI over SSE. React + PDF.js frontend renders pages with a text layer and a normalized-coordinate overlay for anchors.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, PyMuPDF, anthropic SDK, sqlite3, pytest; React 18, Vite, TypeScript, pdfjs-dist.

**Spec:** `docs/superpowers/specs/2026-11-07-paper-review-design.md`

## Global Constraints

- Anchor = `{page: int (1-based), rects: [{x0,y0,x1,y1}] in 0..1 top-left origin, quote: str|null}`; `anchor: null` = paper-level.
- Default persona model `claude-sonnet-5-5`; server-side refusal fallback (`fallbacks: "default"`, beta `server-side-fallback-2026-07-01`) on Opus/Sonnet/Fable models.
- Anthropic key only from env `ANTHROPIC_API_KEY` (or `backend/.env`); never returned by any endpoint.
- Frontend API base from `VITE_API_BASE` (default same origin, `/api`).
- Agent comments never trigger other agents live.
- Round 0 visibility: human comments + own comments only. Rounds ≥1: snapshot at round start.
- Threads flat; reply has optional `reply_to`. Live target = `reply_to` author if builtin persona else root author if builtin persona, plus @mentioned builtin personas.
- No git repo exists; commit steps are skipped (user didn't ask to init git).

## Review Focus

1. Quote not found on page (hyphenation, ligatures, extra whitespace) → API returns 422 with a message the agent can act on; matching normalizes whitespace/case/ligatures/hyphen-breaks. Test: `test_find_quote_normalizes`, `test_create_thread_quote_not_found_422`.
2. Rects outside 0..1 or inverted → clamped and normalized, not stored raw. Test: `test_anchor_rects_clamped`.
3. Missing API key when starting a run → run fails fast with clear status message, not a crash. Test: `test_run_without_key_fails_cleanly`.
4. Deleting a persona that authored comments → comments keep author name/color (persona soft-deleted). Test: `test_delete_persona_keeps_comments`.
5. Human @mention of unknown/external persona → no agent triggered, no error. Test: `test_live_reply_targets`.

---

### Task 1: Backend core — config, DB, PDF processing

**Files:** Create `backend/pyproject.toml`, `backend/app/{__init__,config,db,pdf}.py`; Test `backend/tests/test_pdf.py`, `backend/tests/conftest.py`.

**Interfaces — Produces:**
- `config.settings` with `data_dir: Path`, `db_path: Path`, `anthropic_api_key: str|None`, `max_agent_steps: int = 40`.
- `db.connect() -> sqlite3.Connection` (row_factory=Row, WAL, FKs on), `db.init_db()`.
- `pdf.extract_pages(path) -> list[PageInfo]` where PageInfo = `{"number", "width", "height", "words": [{"text","x0","y0","x1","y1","block","line"}]}` normalized.
- `pdf.render_png(path, page:int, dpi:int) -> bytes`.
- `pdf.find_quote(words, quote) -> list[Rect] | None` (merges words per line into one rect per line).
- `pdf.clamp_rects(rects) -> list[Rect]`.
- `pdf.text_in_rects(words, rects) -> str`.

Tests: `test_extract_pages_normalized` (generated PDF via fitz with known text; all coords in 0..1), `test_find_quote_normalizes` (multi-space/case/“ﬁ” ligature), `test_find_quote_multiline_returns_rect_per_line`, `test_anchor_rects_clamped`, `test_text_in_rects`.

### Task 2: Service layer + HTTP API

**Files:** Create `backend/app/{schemas,services,events,main}.py`, `backend/app/routes/{papers,threads,personas,runs}.py`; Test `backend/tests/test_api.py`.

**Interfaces — Produces (services):**
- `create_paper(filename, data: bytes, title=None) -> dict`, `get_paper`, `list_papers`, `page_words(paper_id, n)`.
- `create_thread(paper_id, author: Author, body, anchor_in) -> dict` where `anchor_in` may have `rects` or `quote`; raises `AnchorError` (→422).
- `add_reply(thread_id, author, body, reply_to=None) -> dict` → emits event, calls `live.on_human_comment` if author is human.
- `list_threads(paper_id, *, visible_to: VisibilityFilter|None=None, author_id=None, status=None)`.
- `set_thread_status(thread_id, status)`.
- Persona CRUD: `create_persona(...)` returns api_key once; `delete_persona` soft-deletes.
- `Author = {"type": "human"|"persona", "id": str|None, "name": str, "color": str}`.
- `events.bus.publish(paper_id, event: dict)`, `events.bus.subscribe(paper_id) -> queue`.

**Routes (prefix `/api`)** as in spec; agents authenticate with header `Authorization: Bearer <persona api key>`; no header = human.
SSE: `GET /api/papers/{id}/events`.

Tests: upload+meta, page text, page image PNG, create thread by rects & by quote, quote-not-found 422, reply with persona bearer key sets author, thread status patch, `test_delete_persona_keeps_comments`.

### Task 3: Agent runner — review runs + live replies

**Files:** Create `backend/app/agents/{__init__,prompts,tools,runner,live}.py`; Test `backend/tests/test_runner.py`.

**Interfaces — Produces:**
- `tools.TOOL_DEFS: list[dict]`, `tools.execute(ctx: AgentContext, name, input) -> list[content blocks]`.
- `AgentContext(paper_id, persona, run_id|None, round:int|None, visibility)`.
- `runner.start_run(paper_id, persona_ids, rounds:int, include_initial: bool) -> run dict` (background thread; each round parallel via ThreadPoolExecutor; cancellable via `cancel_run(run_id)`).
- `runner.agent_loop(client, ctx, system, user_msg) -> None` with max steps.
- `live.on_human_comment(thread, comment)` → resolves targets, spawns `respond_in_thread` per target.
- `runner.get_client()` → anthropic client; injectable for tests.

Tests use a fake client returning scripted tool_use responses: `test_round0_visibility`, `test_round_snapshot`, `test_run_without_key_fails_cleanly`, `test_live_reply_targets`, `test_cancel_run`.

### Task 4: Seed data

**Files:** Create `backend/app/seed.py`, `backend/seed/attention.pdf` (downloaded from arXiv 1706.03762).
Produces `seed.seed_if_empty()` called at startup: four builtin personas (Methods Skeptic, Statistician, Domain Expert, Clarity Editor) + example paper.

### Task 5: Frontend

**Files:** `frontend/{package.json,vite.config.ts,tsconfig.json,index.html}`, `frontend/src/{main.tsx,App.tsx,api.ts,types.ts,styles.css}`, `frontend/src/pages/{Library,PaperView,Personas}.tsx`, `frontend/src/components/{PdfPage,ThreadList,ThreadCard,Composer,ReviewPanel}.tsx`.
Vite dev proxies `/api` → `http://localhost:8000`. Behaviours from spec "UI" section; human name in localStorage.

### Task 6: README with run instructions.
