"""Domain operations shared by the HTTP API and the built-in agent runner."""
from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal, TypedDict

from . import db, pdf
from .config import settings
from .events import bus

HUMAN_COLOR = "#495057"
DEFAULT_MODEL = "claude-sonnet-5-5"


class NotFound(Exception):
    pass


class AnchorError(ValueError):
    pass


class Author(TypedDict):
    type: Literal["human", "persona"]
    id: str | None
    name: str
    color: str


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def human_author(name: str | None) -> Author:
    return Author(type="human", id=None, name=(name or "").strip() or "Human", color=HUMAN_COLOR)


def persona_author(persona: dict) -> Author:
    return Author(type="persona", id=persona["id"], name=persona["name"], color=persona["color"])


# Hook set by agents.live at startup: called after a human writes a comment.
on_human_comment: Callable[[dict, dict], None] | None = None
# Hook set by app.metadata at startup: called after a paper is uploaded.
on_paper_created: Callable[[str], None] | None = None


# ---------------------------------------------------------------- papers

def _paper_row(row) -> dict:
    d = dict(row)
    d["authors"] = json.loads(d.pop("authors_json", None) or "[]")
    d["keywords"] = json.loads(d.pop("keywords_json", None) or "[]")
    return d


def create_paper(filename: str, data: bytes, title: str | None = None) -> dict:
    paper_id = new_id("pap")
    path = settings.pdf_dir / f"{paper_id}.pdf"
    settings.ensure_dirs()
    path.write_bytes(data)
    try:
        pages = pdf.extract_pages(path)
    except Exception as e:
        path.unlink(missing_ok=True)
        raise ValueError(f"Could not read PDF: {e}") from e
    title_source = "user" if title else "pdf"
    title = title or pdf.pdf_title(path, Path(filename).stem)
    status = "pending" if on_paper_created else "none"
    with db.tx() as conn:
        conn.execute(
            "INSERT INTO papers (id, title, filename, page_count, created_at, title_source, metadata_status) VALUES (?,?,?,?,?,?,?)",
            (paper_id, title, filename, len(pages), now(), title_source, status),
        )
        conn.executemany(
            "INSERT INTO pages (paper_id, number, width, height, text, words_json) VALUES (?,?,?,?,?,?)",
            [(paper_id, p["number"], p["width"], p["height"], p["text"], json.dumps(p["words"])) for p in pages],
        )
    if on_paper_created:
        on_paper_created(paper_id)
    return get_paper(paper_id)


def get_paper(paper_id: str) -> dict:
    with db.tx() as conn:
        row = conn.execute("SELECT * FROM papers WHERE id=?", (paper_id,)).fetchone()
        if not row:
            raise NotFound(f"paper {paper_id} not found")
        pages = conn.execute(
            "SELECT number, width, height FROM pages WHERE paper_id=? ORDER BY number", (paper_id,)
        ).fetchall()
        stats = _paper_stats(conn, [paper_id])[paper_id]
    out = _paper_row(row)
    out.update(stats)
    out["pages"] = [dict(p) for p in pages]
    return out


def _run_summary(r) -> dict:
    return {
        "id": r["id"],
        "persona_count": len(json.loads(r["persona_ids_json"])),
        "rounds": r["rounds"],
        "include_initial": bool(r["include_initial"]),
        "status": r["status"],
        "created_at": r["created_at"],
    }


def _paper_stats(conn, paper_ids: list[str]) -> dict[str, dict]:
    stats = {pid: {"open_count": 0, "resolved_count": 0, "participants": [], "last_run": None} for pid in paper_ids}
    for r in conn.execute("SELECT paper_id, status, COUNT(*) AS n FROM threads GROUP BY paper_id, status"):
        if r["paper_id"] in stats:
            stats[r["paper_id"]][f"{r['status']}_count"] = r["n"]
    for r in conn.execute(
        """SELECT t.paper_id, c.author_type, c.author_id, c.author_name, c.author_color,
                  p.name AS cur_name, p.color AS cur_color, MIN(c.seq) AS first
           FROM comments c JOIN threads t ON t.id=c.thread_id
           LEFT JOIN personas p ON c.author_type='persona' AND p.id=c.author_id AND p.deleted_at IS NULL
           GROUP BY t.paper_id, c.author_type, c.author_id, CASE WHEN c.author_type='human' THEN c.author_name END
           ORDER BY first"""
    ):
        if r["paper_id"] in stats:
            stats[r["paper_id"]]["participants"].append(
                {
                    "type": r["author_type"],
                    "id": r["author_id"],
                    "name": r["cur_name"] or r["author_name"],
                    "color": r["cur_color"] or r["author_color"],
                }
            )
    for r in conn.execute("SELECT * FROM runs ORDER BY created_at DESC"):
        if r["paper_id"] in stats and stats[r["paper_id"]]["last_run"] is None:
            stats[r["paper_id"]]["last_run"] = _run_summary(r)
    for pid in paper_ids:
        stats[pid]["replication"] = _replication_summary(conn, pid)
    return stats


def _replication_summary(conn, paper_id: str) -> dict:
    """One status for the papers list, from the newest experiment and its newest run.

    none | extracting | needs_you | ready | running | verifying | verified | finished | failed
    """
    exp = conn.execute(
        "SELECT id, status FROM experiments WHERE paper_id=? ORDER BY created_at DESC LIMIT 1", (paper_id,)
    ).fetchone()
    if not exp:
        return {"status": "none", "runs": 0}
    runs = conn.execute("SELECT COUNT(*) AS n FROM replications WHERE paper_id=?", (paper_id,)).fetchone()["n"]
    rep = conn.execute(
        "SELECT id, status, report_md FROM replications WHERE experiment_id=? ORDER BY created_at DESC LIMIT 1", (exp["id"],)
    ).fetchone()
    out = {"runs": runs, "experiment_id": exp["id"]}
    if exp["status"] in ("extracting", "checking"):
        return {**out, "status": "extracting"}
    if exp["status"] == "needs_review":
        return {**out, "status": "needs_you"}
    if exp["status"] == "failed" and not rep:
        return {**out, "status": "failed"}
    if not rep:
        return {**out, "status": "ready"}
    if rep["status"] in ("queued", "running"):
        return {**out, "status": "running"}
    if rep["status"] in ("failed", "cancelled"):
        return {**out, "status": "failed" if rep["status"] == "failed" else "ready"}
    vs = [v["status"] for v in conn.execute("SELECT status FROM verifications WHERE replication_id=?", (rep["id"],))]
    verdict = None
    for line in (rep["report_md"] or "").splitlines():
        t = line.lstrip("#").strip().replace("**", "")
        if t.lower().startswith("status:"):
            verdict = t.split(":", 1)[1].strip()
            break
    out["verdict"] = verdict
    if any(v in ("pending", "running") for v in vs):
        return {**out, "status": "verifying"}
    if vs and all(v == "done" for v in vs):
        return {**out, "status": "verified"}
    return {**out, "status": "finished"}


def list_papers() -> list[dict]:
    with db.tx() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM papers ORDER BY created_at DESC").fetchall()]
        stats = _paper_stats(conn, [r["id"] for r in rows])
    rows = [_paper_row(r) for r in rows]
    for r in rows:
        r.update(stats[r["id"]])
        r["thread_count"] = r["open_count"] + r["resolved_count"]
    return rows


PAPER_FIELDS = {"title", "authors", "year", "venue", "abstract", "keywords", "field", "doc_type", "arxiv_id", "doi"}


def update_paper(paper_id: str, *, source: str = "user", **fields) -> dict:
    """Set paper details. A title set by a person (source="user") is never overwritten by extraction."""
    get_paper(paper_id)
    cols: dict[str, Any] = {}
    for k, v in fields.items():
        if k not in PAPER_FIELDS or v is None:
            continue
        if k in ("authors", "keywords"):
            cols[f"{k}_json"] = json.dumps([str(x).strip() for x in v if str(x).strip()])
        elif k == "title":
            if not str(v).strip():
                continue
            cols["title"] = str(v).strip()
            cols["title_source"] = source
        else:
            cols[k] = v
    if cols:
        sets = ", ".join(f"{k}=?" for k in cols)
        with db.tx() as conn:
            conn.execute(f"UPDATE papers SET {sets} WHERE id=?", (*cols.values(), paper_id))
    return get_paper(paper_id)


def set_metadata_status(paper_id: str, status: str, error: str | None = None) -> None:
    with db.tx() as conn:
        conn.execute("UPDATE papers SET metadata_status=?, metadata_error=? WHERE id=?", (status, error, paper_id))


def delete_paper(paper_id: str) -> None:
    get_paper(paper_id)
    with db.tx() as conn:
        conn.execute("DELETE FROM papers WHERE id=?", (paper_id,))
    (settings.pdf_dir / f"{paper_id}.pdf").unlink(missing_ok=True)


def paper_pdf_path(paper_id: str) -> Path:
    get_paper(paper_id)
    return settings.pdf_dir / f"{paper_id}.pdf"


def page_data(paper_id: str, number: int) -> dict:
    with db.tx() as conn:
        row = conn.execute("SELECT * FROM pages WHERE paper_id=? AND number=?", (paper_id, number)).fetchone()
    if not row:
        raise NotFound(f"page {number} not found in paper {paper_id}")
    return {
        "number": row["number"],
        "width": row["width"],
        "height": row["height"],
        "text": row["text"],
        "words": json.loads(row["words_json"]),
    }


def full_text(paper_id: str) -> str:
    with db.tx() as conn:
        rows = conn.execute("SELECT number, text FROM pages WHERE paper_id=? ORDER BY number", (paper_id,)).fetchall()
    if not rows:
        get_paper(paper_id)
    return "\n\n".join(f"=== Page {r['number']} ===\n{r['text'].strip()}" for r in rows)


# ---------------------------------------------------------------- anchors

def resolve_anchor(paper_id: str, anchor: dict | None) -> tuple[int | None, list, str | None, str | None]:
    """Turn an incoming anchor into (page, rects, quote, kind).

    kind: "text" (a quoted passage, possibly with its selection rects), "box" (rects only:
    a region such as a figure; quote is filled from the words inside), or None (page/paper level)."""
    if not anchor or anchor.get("page") in (None, 0):
        return None, [], None, None
    page = int(anchor["page"])
    paper = get_paper(paper_id)
    if page < 1 or page > paper["page_count"]:
        raise AnchorError(f"page {page} out of range 1..{paper['page_count']}")
    words = page_data(paper_id, page)["words"]
    rects_in = anchor.get("rects") or []
    quote = (anchor.get("quote") or "").strip() or None
    if rects_in:
        rects = pdf.clamp_rects(rects_in)
        if not rects:
            raise AnchorError("all rects were empty after clamping to the page (coordinates are fractions 0..1)")
        if quote:
            return page, rects, quote, "text"
        return page, rects, pdf.text_in_rects(words, rects) or None, "box"
    if quote:
        rects = pdf.find_quote(words, quote)
        if rects is None:
            raise AnchorError(
                f"quote not found on page {page}. Copy the text exactly as it appears on that page "
                "(a shorter, distinctive phrase works best), or give rects instead."
            )
        return page, rects, quote, "text"
    return page, [], None, None  # page-level comment


# ---------------------------------------------------------------- threads/comments

# Comments keep the author's name/color as written, but show a persona's current
# name/color while it exists (so edits on the Personas page apply everywhere).
COMMENT_SELECT = """SELECT c.*, p.name AS cur_name, p.color AS cur_color FROM comments c
    LEFT JOIN personas p ON c.author_type='persona' AND p.id=c.author_id AND p.deleted_at IS NULL"""


def _comment_row(r) -> dict:
    keys = r.keys()
    name = (r["cur_name"] if "cur_name" in keys else None) or r["author_name"]
    color = (r["cur_color"] if "cur_color" in keys else None) or r["author_color"]
    return {
        "id": r["id"],
        "seq": r["seq"],
        "thread_id": r["thread_id"],
        "author": {"type": r["author_type"], "id": r["author_id"], "name": name, "color": color},
        "body": r["body"],
        "reply_to": r["reply_to"],
        "run_id": r["run_id"],
        "round": r["round"],
        "created_at": r["created_at"],
    }


def _thread_obj(t, comments: list[dict]) -> dict:
    return {
        "id": t["id"],
        "paper_id": t["paper_id"],
        "anchor": None
        if t["page"] is None
        else {"page": t["page"], "rects": json.loads(t["rects_json"]), "quote": t["quote"], "kind": t["anchor_kind"] or "text"},
        "status": t["status"],
        "created_at": t["created_at"],
        "comments": comments,
    }


def _insert_comment(conn, thread_id: str, author: Author, body: str, reply_to: str | None, run_id, round_) -> str:
    cid = new_id("cmt")
    conn.execute(
        """INSERT INTO comments (id, thread_id, author_type, author_id, author_name, author_color, body, reply_to, run_id, round, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (cid, thread_id, author["type"], author["id"], author["name"], author["color"], body, reply_to, run_id, round_, now()),
    )
    return cid


def create_thread(
    paper_id: str, author: Author, body: str, anchor: dict | None, *, run_id: str | None = None, round_: int | None = None
) -> dict:
    body = (body or "").strip()
    if not body:
        raise ValueError("comment body is empty")
    page, rects, quote, kind = resolve_anchor(paper_id, anchor)
    tid = new_id("thr")
    with db.tx() as conn:
        conn.execute(
            "INSERT INTO threads (id, paper_id, page, rects_json, quote, anchor_kind, created_at) VALUES (?,?,?,?,?,?,?)",
            (tid, paper_id, page, json.dumps(rects), quote, kind, now()),
        )
        _insert_comment(conn, tid, author, body, None, run_id, round_)
    thread = get_thread(tid)
    bus.publish(paper_id, {"type": "thread.created", "thread_id": tid})
    if author["type"] == "human" and on_human_comment:
        on_human_comment(thread, thread["comments"][0])
    return thread


def add_reply(
    thread_id: str, author: Author, body: str, reply_to: str | None = None, *, run_id: str | None = None, round_: int | None = None
) -> dict:
    body = (body or "").strip()
    if not body:
        raise ValueError("reply body is empty")
    thread = get_thread(thread_id)
    if reply_to and reply_to not in {c["id"] for c in thread["comments"]}:
        raise ValueError(f"reply_to {reply_to} is not a comment in thread {thread_id}")
    with db.tx() as conn:
        cid = _insert_comment(conn, thread_id, author, body, reply_to, run_id, round_)
    thread = get_thread(thread_id)
    comment = next(c for c in thread["comments"] if c["id"] == cid)
    bus.publish(thread["paper_id"], {"type": "comment.created", "thread_id": thread_id, "comment_id": cid})
    if author["type"] == "human" and on_human_comment:
        on_human_comment(thread, comment)
    return comment


def get_thread(thread_id: str) -> dict:
    with db.tx() as conn:
        t = conn.execute("SELECT * FROM threads WHERE id=?", (thread_id,)).fetchone()
        if not t:
            raise NotFound(f"thread {thread_id} not found")
        cs = conn.execute(COMMENT_SELECT + " WHERE c.thread_id=? ORDER BY c.seq", (thread_id,)).fetchall()
    return _thread_obj(t, [_comment_row(c) for c in cs])


@dataclass
class Visibility:
    """What an agent may see. Round 0: humans + own comments. Later rounds: snapshot."""
    persona_id: str | None = None
    only_humans_and_self: bool = False
    max_seq: int | None = None

    def allows(self, c: dict) -> bool:
        if self.max_seq is not None and c["seq"] > self.max_seq:
            return False
        if self.only_humans_and_self:
            return c["author"]["type"] == "human" or c["author"]["id"] == self.persona_id
        return True


def list_threads(
    paper_id: str,
    *,
    visibility: Visibility | None = None,
    author_id: str | None = None,
    status: str | None = None,
    page: int | None = None,
) -> list[dict]:
    with db.tx() as conn:
        ts = conn.execute("SELECT * FROM threads WHERE paper_id=? ORDER BY created_at", (paper_id,)).fetchall()
        cs = conn.execute(
            COMMENT_SELECT + " JOIN threads t ON t.id=c.thread_id WHERE t.paper_id=? ORDER BY c.seq",
            (paper_id,),
        ).fetchall()
    by_thread: dict[str, list[dict]] = {}
    for c in cs:
        by_thread.setdefault(c["thread_id"], []).append(_comment_row(c))
    out = []
    for t in ts:
        comments = by_thread.get(t["id"], [])
        if not comments:
            continue
        if visibility is not None:
            if not visibility.allows(comments[0]):
                continue
            comments = [c for c in comments if visibility.allows(c)]
        if status and t["status"] != status:
            continue
        if page is not None and t["page"] != page:
            continue
        if author_id and not any(c["author"]["id"] == author_id for c in comments):
            continue
        out.append(_thread_obj(t, comments))
    out.sort(key=lambda th: (th["anchor"]["page"] if th["anchor"] else 0, th["anchor"]["rects"][0]["y0"] if th["anchor"] and th["anchor"]["rects"] else 0))
    return out


def max_comment_seq(paper_id: str) -> int:
    with db.tx() as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(c.seq), 0) AS m FROM comments c JOIN threads t ON t.id=c.thread_id WHERE t.paper_id=?",
            (paper_id,),
        ).fetchone()
    return int(row["m"])


def set_thread_status(thread_id: str, status: str) -> dict:
    if status not in ("open", "resolved"):
        raise ValueError("status must be 'open' or 'resolved'")
    thread = get_thread(thread_id)
    with db.tx() as conn:
        conn.execute("UPDATE threads SET status=? WHERE id=?", (status, thread_id))
    bus.publish(thread["paper_id"], {"type": "thread.updated", "thread_id": thread_id})
    return get_thread(thread_id)


def delete_thread(thread_id: str) -> None:
    thread = get_thread(thread_id)
    with db.tx() as conn:
        conn.execute("DELETE FROM threads WHERE id=?", (thread_id,))
    bus.publish(thread["paper_id"], {"type": "thread.deleted", "thread_id": thread_id})


# ---------------------------------------------------------------- personas

def _persona_row(r) -> dict:
    d = dict(r)
    d["enabled"] = bool(d["enabled"])
    d.pop("api_key_hash", None)
    return d


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def create_persona(
    name: str,
    *,
    kind: str = "builtin",
    color: str = "#1F5FD6",
    prompt: str = "",
    model: str = DEFAULT_MODEL,
    tagline: str = "",
    enabled: bool = True,
) -> dict:
    """Returns the persona plus its API key (shown only once)."""
    if kind not in ("builtin", "external"):
        raise ValueError("kind must be 'builtin' or 'external'")
    if not name.strip():
        raise ValueError("name is required")
    pid = new_id("per")
    key = "prk_" + secrets.token_urlsafe(24)
    with db.tx() as conn:
        conn.execute(
            """INSERT INTO personas (id, kind, name, color, prompt, model, tagline, enabled, api_key_hash, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (pid, kind, name.strip(), color, prompt, model or DEFAULT_MODEL, tagline.strip(), int(enabled), _hash_key(key), now()),
        )
    p = get_persona(pid)
    p["api_key"] = key
    return p


def get_persona(persona_id: str, *, include_deleted: bool = False) -> dict:
    with db.tx() as conn:
        r = conn.execute("SELECT * FROM personas WHERE id=?", (persona_id,)).fetchone()
    if not r or (r["deleted_at"] and not include_deleted):
        raise NotFound(f"persona {persona_id} not found")
    return _persona_row(r)


def list_personas(*, with_stats: bool = False) -> list[dict]:
    with db.tx() as conn:
        rows = conn.execute("SELECT * FROM personas WHERE deleted_at IS NULL ORDER BY created_at").fetchall()
        usage = {}
        if with_stats:
            usage = {
                r["author_id"]: (r["n"], r["papers"])
                for r in conn.execute(
                    """SELECT c.author_id, COUNT(*) AS n, COUNT(DISTINCT t.paper_id) AS papers
                       FROM comments c JOIN threads t ON t.id=c.thread_id
                       WHERE c.author_type='persona' GROUP BY c.author_id"""
                )
            }
    out = [_persona_row(r) for r in rows]
    if with_stats:
        for p in out:
            p["comment_count"], p["paper_count"] = usage.get(p["id"], (0, 0))
    return out


UPDATABLE = {"name", "color", "prompt", "model", "enabled", "kind", "tagline"}


def update_persona(persona_id: str, **fields: Any) -> dict:
    get_persona(persona_id)
    fields = {k: v for k, v in fields.items() if k in UPDATABLE and v is not None}
    if "kind" in fields and fields["kind"] not in ("builtin", "external"):
        raise ValueError("kind must be 'builtin' or 'external'")
    if "enabled" in fields:
        fields["enabled"] = int(bool(fields["enabled"]))
    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        with db.tx() as conn:
            conn.execute(f"UPDATE personas SET {sets} WHERE id=?", (*fields.values(), persona_id))
    return get_persona(persona_id)


def delete_persona(persona_id: str) -> None:
    """Soft delete: existing comments keep their author name/color."""
    get_persona(persona_id)
    with db.tx() as conn:
        conn.execute("UPDATE personas SET deleted_at=?, enabled=0 WHERE id=?", (now(), persona_id))


def regenerate_key(persona_id: str) -> str:
    get_persona(persona_id)
    key = "prk_" + secrets.token_urlsafe(24)
    with db.tx() as conn:
        conn.execute("UPDATE personas SET api_key_hash=? WHERE id=?", (_hash_key(key), persona_id))
    return key


def persona_by_key(key: str) -> dict | None:
    with db.tx() as conn:
        r = conn.execute(
            "SELECT * FROM personas WHERE api_key_hash=? AND deleted_at IS NULL", (_hash_key(key),)
        ).fetchone()
    return _persona_row(r) if r else None


def copy_seed_pdf(src: Path) -> dict:
    data = src.read_bytes()
    return create_paper(src.name, data)

