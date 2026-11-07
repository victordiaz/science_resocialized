"""Blind replication pipeline: storage, the in-app agents, and the worker job queue.

Two steps, each started by a person:
  1. start_extraction -> extractor agent -> leak checker (stops: spec ready, or needs review)
  2. queue_replication -> (worker claims, runs Claude Code, streams events, completes with files)
     -> start_verifications (one verifier agent per chosen persona), automatically.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import logging
import mimetypes
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from .. import db, services
from ..agents import runner, tools
from ..agents.tools import AgentContext, ToolError
from ..config import settings
from ..events import bus
from ..services import NotFound, Visibility
from . import prompts

log = logging.getLogger("paper_review.replication")

# Background threads run synchronously when False (tests).
background = True

HEARTBEAT_STALE = timedelta(minutes=10)
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 25 * 1024 * 1024
READ_LIMIT = 60_000  # characters of a text file shown to a verifier per read

READ_TOOLS = [t for t in tools.TOOL_DEFS if t["name"] in ("read_full_text", "get_page_text", "view_page")]


def _spawn(fn, *args) -> None:
    if background:
        threading.Thread(target=fn, args=args, daemon=True).start()
    else:
        fn(*args)


def _publish(paper_id: str, **extra) -> None:
    bus.publish(paper_id, {"type": "replication.updated", **extra})


def _pseudo_persona(name: str) -> dict:
    return {"id": f"system:{name}", "name": name, "color": "#495057", "model": settings.pipeline_model, "prompt": ""}


# ================================================================ storage

def _exp_row(r) -> dict:
    d = dict(r)
    d["verifier_ids"] = json.loads(d.pop("verifier_ids_json"))
    d["leak_found"] = None if d["leak_found"] is None else bool(d["leak_found"])
    return d


def _rep_row(r) -> dict:
    d = dict(r)
    d["verifier_ids"] = json.loads(d.pop("verifier_ids_json"))
    d["attachment_ids"] = json.loads(d.pop("attachment_ids_json", None) or "[]")
    d["cancel_requested"] = bool(d["cancel_requested"])
    return d


def get_experiment(exp_id: str) -> dict:
    with db.tx() as conn:
        r = conn.execute("SELECT * FROM experiments WHERE id=?", (exp_id,)).fetchone()
    if not r:
        raise NotFound(f"experiment {exp_id} not found")
    return _exp_row(r)


def _update_experiment(exp_id: str, **fields) -> dict:
    fields["updated_at"] = services.now()
    sets = ", ".join(f"{k}=?" for k in fields)
    with db.tx() as conn:
        conn.execute(f"UPDATE experiments SET {sets} WHERE id=?", (*fields.values(), exp_id))
    exp = get_experiment(exp_id)
    _publish(exp["paper_id"], experiment_id=exp_id)
    return exp


def get_replication(rep_id: str, *, events_after: int | None = None) -> dict:
    with db.tx() as conn:
        r = conn.execute("SELECT * FROM replications WHERE id=?", (rep_id,)).fetchone()
        if not r:
            raise NotFound(f"replication {rep_id} not found")
        rep = _rep_row(r)
        vs = conn.execute(
            """SELECT v.*, p.name AS persona_name, p.color AS persona_color FROM verifications v
               LEFT JOIN personas p ON p.id=v.persona_id WHERE v.replication_id=? ORDER BY v.created_at""",
            (rep_id,),
        ).fetchall()
        rep["verifications"] = [dict(v) for v in vs]
        if events_after is not None:
            evs = conn.execute(
                "SELECT seq, kind, text, at FROM replication_events WHERE replication_id=? AND seq>? ORDER BY seq LIMIT 500",
                (rep_id, events_after),
            ).fetchall()
            rep["events"] = [dict(e) for e in evs]
    rep["files"] = list_files(rep_id)
    rep["attachments"] = [a for a in (_attachment_or_none(i) for i in rep["attachment_ids"]) if a]
    return rep


def _update_replication(rep_id: str, **fields) -> dict:
    sets = ", ".join(f"{k}=?" for k in fields)
    with db.tx() as conn:
        conn.execute(f"UPDATE replications SET {sets} WHERE id=?", (*fields.values(), rep_id))
    rep = get_replication(rep_id)
    _publish(rep["paper_id"], replication_id=rep_id)
    return rep


def list_for_paper(paper_id: str) -> list[dict]:
    """Experiments, newest first, each with its replications (and their verifications)."""
    services.get_paper(paper_id)
    fail_stale_replications()
    with db.tx() as conn:
        exps = [_exp_row(r) for r in conn.execute(
            "SELECT * FROM experiments WHERE paper_id=? ORDER BY created_at DESC", (paper_id,)
        ).fetchall()]
        rep_ids = {e["id"]: [r["id"] for r in conn.execute(
            "SELECT id FROM replications WHERE experiment_id=? ORDER BY created_at DESC", (e["id"],)
        ).fetchall()] for e in exps}
    for e in exps:
        e["replications"] = [get_replication(rid) for rid in rep_ids[e["id"]]]
        e["attachments"] = list_attachments(e["id"])
    return exps


# ================================================================ pipeline entry points

def start_extraction(paper_id: str) -> dict:
    """Step 1: extract the main experiment and check the spec for leaks. Does not replicate."""
    services.get_paper(paper_id)
    verifier_ids: list[str] = []
    budget_usd = None
    exp_id = services.new_id("exp")
    now = services.now()
    with db.tx() as conn:
        conn.execute(
            """INSERT INTO experiments (id, paper_id, status, verifier_ids_json, budget_usd, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?)""",
            (exp_id, paper_id, "extracting", json.dumps(verifier_ids), budget_usd or settings.replication_budget_usd, now, now),
        )
    _publish(paper_id, experiment_id=exp_id)
    _spawn(_extract_and_check, exp_id)
    return get_experiment(exp_id)


def _check_verifiers(ids: list[str]) -> list[str]:
    out = []
    for pid in ids:
        p = services.get_persona(pid)
        if p["kind"] != "builtin":
            raise ValueError(f"{p['name']} is an external persona; verifiers must run in the app")
        out.append(pid)
    return out


def update_spec(exp_id: str, spec_md: str | None = None, title: str | None = None, outcome_md: str | None = None) -> dict:
    exp = get_experiment(exp_id)
    if exp["status"] in ("extracting", "checking"):
        raise ValueError("the experiment is still being extracted")
    fields: dict[str, Any] = {}
    if spec_md is not None:
        fields["spec_md"] = spec_md
    if title is not None:
        fields["title"] = title
    if outcome_md is not None:
        fields["outcome_md"] = outcome_md
    if spec_md is not None:
        # A person edited the spec: it's theirs now; the old leak check no longer applies.
        fields.update(status="ready", leak_found=None, leak_check_md="Edited by a person after extraction; not re-checked.")
    return _update_experiment(exp_id, **fields)


def recheck_leaks(exp_id: str) -> dict:
    exp = get_experiment(exp_id)
    _update_experiment(exp_id, status="checking")
    _spawn(_leak_check, exp["id"])
    return get_experiment(exp_id)


# ================================================================ extraction + leak check

def _extract_and_check(exp_id: str) -> None:
    exp = get_experiment(exp_id)
    try:
        paper = services.get_paper(exp["paper_id"])
        result: dict = {}

        def executor(ctx, name, inp):
            if name == "submit_experiment":
                for key in ("title", "spec_markdown", "outcome_markdown"):
                    if not isinstance(inp.get(key), str) or not inp[key].strip():
                        raise ToolError(f"`{key}` is required")
                result.update(inp)
                return [{"type": "text", "text": "Saved. You're done; end with a one-line note."}]
            return tools.execute(ctx, name, inp)

        ctx = AgentContext(paper_id=paper["id"], persona=_pseudo_persona("Experiment Extractor"), visibility=Visibility())
        runner.agent_loop(
            runner.client_factory(),
            ctx,
            prompts.EXTRACTOR_TASK.format(title=paper["title"], pages=paper["page_count"]),
            max_steps=settings.max_agent_steps,
            system=prompts.EXTRACTOR_SYSTEM,
            tools=READ_TOOLS + [SUBMIT_EXPERIMENT],
            executor=executor,
        )
        if not result:
            raise RuntimeError("the extractor finished without submitting an experiment")
        _update_experiment(
            exp_id, status="checking", title=result["title"].strip(),
            spec_md=result["spec_markdown"].strip(), outcome_md=result["outcome_markdown"].strip(),
        )
    except Exception as e:
        log.exception("extraction %s failed", exp_id)
        _update_experiment(exp_id, status="failed", error=f"Extraction failed: {runner._err_text(e)}")
        return
    _leak_check(exp_id)


def _leak_check(exp_id: str) -> None:
    exp = get_experiment(exp_id)
    try:
        verdict: dict = {}

        def executor(ctx, name, inp):
            if name == "submit_leak_check":
                if not isinstance(inp.get("leaks_found"), bool) or not isinstance(inp.get("notes"), str):
                    raise ToolError("`leaks_found` (boolean) and `notes` (string) are required")
                verdict.update(inp)
                return [{"type": "text", "text": "Recorded."}]
            raise ToolError(f"unknown tool {name}")

        ctx = AgentContext(paper_id=exp["paper_id"], persona=_pseudo_persona("Leak Checker"), visibility=Visibility())
        runner.agent_loop(
            runner.client_factory(),
            ctx,
            prompts.LEAK_TASK.format(spec=exp["spec_md"], outcome=exp["outcome_md"]),
            max_steps=4,
            system=prompts.LEAK_SYSTEM,
            tools=[SUBMIT_LEAK_CHECK],
            executor=executor,
        )
        if not verdict:
            raise RuntimeError("the leak checker did not submit a verdict")
    except Exception as e:
        log.exception("leak check %s failed", exp_id)
        _update_experiment(exp_id, status="needs_review", leak_check_md=f"The leak check could not run: {runner._err_text(e)}")
        return
    leak = verdict["leaks_found"]
    _update_experiment(exp_id, status="needs_review" if leak else "ready", leak_found=int(leak), leak_check_md=verdict["notes"].strip())


SUBMIT_EXPERIMENT = {
    "name": "submit_experiment",
    "description": "Save the blind replication spec and the hidden outcome. Call once, at the end.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Short neutral title of the experiment (no paper title)."},
            "spec_markdown": {"type": "string", "description": "The SPEC shown to the replicator. No results."},
            "outcome_markdown": {"type": "string", "description": "The paper's reported outcome, hidden from the replicator."},
        },
        "required": ["title", "spec_markdown", "outcome_markdown"],
        "additionalProperties": False,
    },
}

SUBMIT_LEAK_CHECK = {
    "name": "submit_leak_check",
    "description": "Record whether the SPEC leaks the outcome or identifies the paper.",
    "input_schema": {
        "type": "object",
        "properties": {
            "leaks_found": {"type": "boolean"},
            "notes": {"type": "string", "description": "Markdown: each leak, quoted, with a suggested fix; or why it is clean."},
        },
        "required": ["leaks_found", "notes"],
        "additionalProperties": False,
    },
}


# ================================================================ replication queue (worker side)

def queue_replication(exp_id: str, verifier_ids: list[str] | None = None, budget_usd: float | None = None, timeout_min: int | None = None) -> dict:
    """Step 2: replicate the experiment blind; the chosen verifiers run when it finishes."""
    exp = get_experiment(exp_id)
    if exp["status"] in ("extracting", "checking", "failed") or not exp["spec_md"].strip():
        raise ValueError("this experiment has no finished spec to replicate")
    ids = _check_verifiers(verifier_ids) if verifier_ids is not None else exp["verifier_ids"]
    rep_id = services.new_id("rep")
    with db.tx() as conn:
        conn.execute(
            """INSERT INTO replications (id, experiment_id, paper_id, status, spec_md, verifier_ids_json, attachment_ids_json,
                                         budget_usd, timeout_min, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (rep_id, exp_id, exp["paper_id"], "queued", exp["spec_md"], json.dumps(ids),
             json.dumps([a["id"] for a in list_attachments(exp_id)]),
             budget_usd or exp["budget_usd"], timeout_min or settings.replication_timeout_min, services.now()),
        )
    if exp["status"] == "needs_review":
        _update_experiment(exp_id, status="ready")
    _publish(exp["paper_id"], replication_id=rep_id)
    return get_replication(rep_id)


def claim_job(worker: str) -> dict | None:
    """Give the oldest queued replication to a worker. Returns the job or None."""
    fail_stale_replications()
    with db.tx() as conn:
        r = conn.execute("SELECT id FROM replications WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
        if not r:
            return None
        now = services.now()
        cur = conn.execute(
            "UPDATE replications SET status='running', worker=?, started_at=?, heartbeat_at=? WHERE id=? AND status='queued'",
            (worker, now, now, r["id"]),
        )
        if cur.rowcount == 0:  # another worker took it
            return None
    rep = get_replication(r["id"])
    _publish(rep["paper_id"], replication_id=rep["id"])
    add_events(rep["id"], [{"kind": "info", "text": f"Claimed by worker {worker}"}])
    return {
        "replication_id": rep["id"],
        "task_md": prompts.REPLICATOR_TASK_FILE.format(spec=rep["spec_md"], files=prompts.files_section(rep["attachments"])),
        "attachments": [
            {"id": a["id"], "filename": a["filename"], "size": a["size"], "sha256": a["sha256"],
             "url": f"/api/worker/attachments/{a['id']}"}
            for a in rep["attachments"]
        ],
        "prompt": prompts.REPLICATOR_TASK.format(minutes=rep["timeout_min"], budget=rep["budget_usd"]),
        "system_append": prompts.REPLICATOR_APPEND,
        "budget_usd": rep["budget_usd"],
        "timeout_min": rep["timeout_min"],
    }


def add_events(rep_id: str, events: list[dict], workdir: str | None = None) -> dict:
    """Store progress events from the worker. Returns {"cancel": bool}."""
    rep = get_replication(rep_id)
    now = services.now()
    rows = [(rep_id, str(e.get("kind", "text"))[:16], str(e.get("text", ""))[:4000], now) for e in events if e.get("text")]
    with db.tx() as conn:
        if rows:
            conn.executemany("INSERT INTO replication_events (replication_id, kind, text, at) VALUES (?,?,?,?)", rows)
        conn.execute(
            "UPDATE replications SET heartbeat_at=?, workdir=COALESCE(?, workdir) WHERE id=?", (now, workdir, rep_id)
        )
    if rows:
        bus.publish(rep["paper_id"], {"type": "replication.events", "replication_id": rep_id})
    return {"cancel": rep["cancel_requested"] or rep["status"] == "cancelled"}


def _safe_relpath(path: str) -> PurePosixPath:
    p = PurePosixPath(path.replace("\\", "/"))
    if p.is_absolute() or not p.parts or any(part in ("..", "") for part in p.parts):
        raise ValueError(f"bad file path {path!r}")
    return p


def complete_job(rep_id: str, status: str, report_md: str | None, cost_usd: float | None, error: str | None, files: list[dict]) -> dict:
    rep = get_replication(rep_id)
    if status not in ("done", "failed", "cancelled"):
        raise ValueError("status must be done, failed or cancelled")
    if rep["cancel_requested"] and status == "done":
        status = "cancelled"
    out_dir = settings.replication_dir / rep_id
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    saved = 0
    for f in files:
        rel = _safe_relpath(str(f.get("path", "")))
        data = base64.b64decode(f.get("content_b64", ""))
        if len(data) > MAX_FILE_BYTES or total + len(data) > MAX_TOTAL_BYTES:
            continue
        total += len(data)
        dest = out_dir.joinpath(*rel.parts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        saved += 1
    if report_md is None and (out_dir / "REPORT.md").exists():
        report_md = (out_dir / "REPORT.md").read_text(errors="replace")
    add_events(rep_id, [{"kind": "info", "text": f"Finished: {status}. {saved} files uploaded."}])
    rep = _update_replication(
        rep_id, status=status, report_md=report_md, cost_usd=cost_usd, error=error, finished_at=services.now()
    )
    if status == "done" and rep["verifier_ids"]:
        start_verifications(rep_id, rep["verifier_ids"])
    return get_replication(rep_id)


def cancel_replication(rep_id: str) -> dict:
    rep = get_replication(rep_id)
    if rep["status"] == "queued":
        return _update_replication(rep_id, status="cancelled", finished_at=services.now())
    if rep["status"] == "running":
        return _update_replication(rep_id, cancel_requested=1)
    return rep


def fail_stale_replications() -> None:
    """A running job whose worker went quiet is marked failed (it can be re-run)."""
    cutoff = (datetime.now(timezone.utc) - HEARTBEAT_STALE).isoformat()
    with db.tx() as conn:
        stale = conn.execute(
            "SELECT id, paper_id FROM replications WHERE status='running' AND heartbeat_at < ?", (cutoff,)
        ).fetchall()
        for r in stale:
            conn.execute(
                "UPDATE replications SET status='failed', error='The worker stopped responding.', finished_at=? WHERE id=?",
                (services.now(), r["id"]),
            )
    for r in stale:
        _publish(r["paper_id"], replication_id=r["id"])


# ================================================================ files

def _rep_dir(rep_id: str) -> Path:
    return settings.replication_dir / rep_id


def list_files(rep_id: str) -> list[dict]:
    root = _rep_dir(rep_id)
    if not root.exists():
        return []
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out.append({"path": p.relative_to(root).as_posix(), "size": p.stat().st_size})
    return out


def file_path(rep_id: str, path: str) -> Path:
    get_replication(rep_id)
    rel = _safe_relpath(path)
    full = _rep_dir(rep_id).joinpath(*rel.parts)
    if not full.is_file():
        raise NotFound(f"no file {path} in replication {rep_id}")
    return full


# ================================================================ verification

def start_verifications(rep_id: str, persona_ids: list[str]) -> list[dict]:
    rep = get_replication(rep_id)
    if rep["status"] not in ("done", "failed"):
        raise ValueError("a replication can be verified once it has finished")
    persona_ids = _check_verifiers(persona_ids)
    ids = []
    with db.tx() as conn:
        for pid in persona_ids:
            vid = services.new_id("ver")
            conn.execute(
                "INSERT INTO verifications (id, replication_id, paper_id, persona_id, status, created_at) VALUES (?,?,?,?,?,?)",
                (vid, rep_id, rep["paper_id"], pid, "pending", services.now()),
            )
            ids.append(vid)
    _publish(rep["paper_id"], replication_id=rep_id)
    for vid in ids:
        _spawn(_run_verification, vid)
    return get_replication(rep_id)["verifications"]


def _update_verification(vid: str, paper_id: str, **fields) -> None:
    sets = ", ".join(f"{k}=?" for k in fields)
    with db.tx() as conn:
        conn.execute(f"UPDATE verifications SET {sets} WHERE id=?", (*fields.values(), vid))
    _publish(paper_id, verification_id=vid)


def _run_verification(vid: str) -> None:
    with db.tx() as conn:
        v = dict(conn.execute("SELECT * FROM verifications WHERE id=?", (vid,)).fetchone())
    rep = get_replication(v["replication_id"])
    exp = get_experiment(rep["experiment_id"])
    paper = services.get_paper(rep["paper_id"])
    _update_verification(vid, rep["paper_id"], status="running")
    try:
        persona = services.get_persona(v["persona_id"], include_deleted=True)
        submitted: dict = {}

        def executor(ctx, name, inp):
            if name == "submit_report":
                if not isinstance(inp.get("report_markdown"), str) or not inp["report_markdown"].strip():
                    raise ToolError("`report_markdown` is required")
                submitted["report"] = inp["report_markdown"].strip()
                return [{"type": "text", "text": "Report saved."}]
            if name == "list_replication_files":
                files = [f"{f['path']} ({f['size']} bytes)" for f in list_files(rep["id"])]
                files += [f"inputs/{a['filename']} ({a['size']} bytes, provided by a person{': ' + a['note'] if a['note'] else ''})" for a in rep["attachments"]]
                return [{"type": "text", "text": "\n".join(files) or "(no files)"}]
            if name == "read_replication_file":
                path = str(inp.get("path", ""))
                if path.startswith("inputs/"):
                    att = next((a for a in rep["attachments"] if a["filename"] == path[len("inputs/"):]), None)
                    if not att:
                        raise ToolError(f"no provided file {path}")
                    return _read_path_for_agent(attachment_path(att), path)
                return _read_file_for_agent(rep["id"], path)
            return tools.execute(ctx, name, inp)

        files = list_files(rep["id"])
        msg = prompts.VERIFIER_TASK.format(
            rep_id=rep["id"], title=paper["title"], spec=rep["spec_md"], outcome=exp["outcome_md"],
            status=rep["status"] + (f" ({rep['error']})" if rep["error"] else ""),
            provided=prompts.files_section(rep["attachments"]) or "No files were provided.",
            cost=f", replication cost ${rep['cost_usd']:.2f}" if rep["cost_usd"] else "",
            files=f"{len(files)} files (use list_replication_files)" if files else "none uploaded",
        )
        system = prompts.VERIFIER_SYSTEM.format(name=persona["name"], persona_prompt=persona.get("prompt") or "")
        ctx = AgentContext(paper_id=paper["id"], persona=persona, visibility=Visibility())
        runner.agent_loop(
            runner.client_factory(), ctx, msg, max_steps=settings.max_agent_steps,
            system=system, tools=READ_TOOLS + VERIFIER_TOOLS, executor=executor,
        )
        if not submitted:
            raise RuntimeError("the verifier finished without submitting a report")
        _update_verification(vid, rep["paper_id"], status="done", report_md=submitted["report"], finished_at=services.now())
    except Exception as e:
        log.exception("verification %s failed", vid)
        _update_verification(vid, rep["paper_id"], status="failed", error=runner._err_text(e), finished_at=services.now())


def _read_file_for_agent(rep_id: str, path: str) -> list[dict]:
    try:
        full = file_path(rep_id, path)
    except (NotFound, ValueError) as e:
        raise ToolError(str(e)) from e
    return _read_path_for_agent(full, path)


def _read_path_for_agent(full: Path, path: str) -> list[dict]:
    mime = mimetypes.guess_type(full.name)[0] or ""
    if mime in ("image/png", "image/jpeg", "image/gif", "image/webp"):
        if full.stat().st_size > 4 * 1024 * 1024:
            raise ToolError("image is too large to view")
        return [
            {"type": "text", "text": f"{path}:"},
            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": base64.standard_b64encode(full.read_bytes()).decode()}},
        ]
    with open(full, "rb") as fh:
        raw = fh.read(READ_LIMIT * 4)
    size = full.stat().st_size
    if b"\x00" in raw[:4096] or full.suffix.lower() in (".zip", ".gz", ".tar", ".7z", ".npz", ".pt", ".pkl", ".parquet"):
        raise ToolError(f"{path} is a binary file ({size} bytes); it can't be read as text here")
    text = raw.decode(errors="replace")
    if size > len(raw):
        text += f"\n\n[file is {size} bytes; only the start is shown]"
    if len(text) > READ_LIMIT:
        text = text[:READ_LIMIT] + f"\n\n[truncated: showing {READ_LIMIT} of {len(text)} characters]"
    return [{"type": "text", "text": text}]


VERIFIER_TOOLS = [
    {
        "name": "list_replication_files",
        "description": "List the files the replicator produced (report, code, outputs).",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "read_replication_file",
        "description": "Read one replication file by path. Images (plots) are returned as images.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "submit_report",
        "description": "Save your verification report (markdown, any structure). Call once, at the end.",
        "input_schema": {
            "type": "object",
            "properties": {"report_markdown": {"type": "string"}},
            "required": ["report_markdown"],
            "additionalProperties": False,
        },
    },
]


# ================================================================ for reviewers

def summary_for_agents(paper_id: str) -> str:
    """Text digest of replications and verification reports, for reviewer personas."""
    exps = list_for_paper(paper_id)
    if not exps:
        return "No blind replications have been run for this paper."
    out = []
    for e in exps:
        out.append(f"# Experiment: {e['title'] or '(untitled)'} [{e['status']}]")
        if not e["replications"]:
            out.append("No replication runs yet.")
        for r in e["replications"]:
            out.append(f"\n## Replication {r['id']} [{r['status']}]")
            if r["report_md"]:
                rep = r["report_md"]
                out.append("Replicator's REPORT.md:\n" + (rep[:6000] + "\n[truncated]" if len(rep) > 6000 else rep))
            for v in r["verifications"]:
                if v["status"] == "done":
                    out.append(f"\n### Verification by {v['persona_name']}\n{v['report_md']}")
    return "\n".join(out)


def mark_interrupted() -> None:
    """In-app agents can't survive a restart. Worker-side runs are left alone (heartbeats decide)."""
    now = services.now()
    with db.tx() as conn:
        conn.execute(
            "UPDATE experiments SET status='failed', error='The server restarted during extraction.', updated_at=? WHERE status IN ('extracting','checking')",
            (now,),
        )
        conn.execute(
            "UPDATE verifications SET status='failed', error='The server restarted.', finished_at=? WHERE status IN ('pending','running')",
            (now,),
        )


# ================================================================ attachments (files for the replicator)

_UNSAFE = re.compile(r"[^\w.\- ()+]")


def _clean_name(name: str) -> str:
    base = Path(name.replace("\\", "/")).name.strip() or "file"
    base = _UNSAFE.sub("_", base)[:180].lstrip(".") or "file"
    return base


def _att_row(r) -> dict:
    return dict(r)


def _attachment_or_none(att_id: str) -> dict | None:
    with db.tx() as conn:
        r = conn.execute("SELECT * FROM attachments WHERE id=?", (att_id,)).fetchone()
    return _att_row(r) if r else None


def get_attachment(att_id: str) -> dict:
    a = _attachment_or_none(att_id)
    if not a:
        raise NotFound(f"attachment {att_id} not found")
    return a


def list_attachments(exp_id: str) -> list[dict]:
    with db.tx() as conn:
        rows = conn.execute("SELECT * FROM attachments WHERE experiment_id=? ORDER BY created_at", (exp_id,)).fetchall()
    return [_att_row(r) for r in rows]


def attachment_path(att: dict) -> Path:
    return settings.attachment_dir / att["experiment_id"] / att["id"] / att["filename"]


def save_attachment(exp_id: str, filename: str, stream, content_type: str | None = None, note: str = "") -> dict:
    """Stream an uploaded file to disk (chunked, with a size limit and checksum)."""
    exp = get_experiment(exp_id)
    taken = {a["filename"] for a in list_attachments(exp_id)}
    name = _clean_name(filename)
    stem, dot, ext = name.partition(".")
    n = 2
    while name in taken:
        name = f"{stem} ({n}){dot}{ext}"
        n += 1
    att_id = services.new_id("att")
    dest = settings.attachment_dir / exp_id / att_id / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    limit = settings.attachment_max_mb * 1024 * 1024
    h, size = hashlib.sha256(), 0
    try:
        with open(dest, "wb") as out:
            while chunk := stream.read(1024 * 1024):
                size += len(chunk)
                if size > limit:
                    raise ValueError(f"{name} is larger than {settings.attachment_max_mb} MB")
                h.update(chunk)
                out.write(chunk)
    except BaseException:
        dest.unlink(missing_ok=True)
        dest.parent.rmdir()
        raise
    with db.tx() as conn:
        conn.execute(
            "INSERT INTO attachments (id, experiment_id, filename, size, sha256, content_type, note, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (att_id, exp_id, name, size, h.hexdigest(), content_type, note.strip(), services.now()),
        )
    _publish(exp["paper_id"], experiment_id=exp_id)
    return get_attachment(att_id)


def update_attachment(att_id: str, note: str) -> dict:
    att = get_attachment(att_id)
    with db.tx() as conn:
        conn.execute("UPDATE attachments SET note=? WHERE id=?", (note.strip(), att_id))
    _publish(get_experiment(att["experiment_id"])["paper_id"], experiment_id=att["experiment_id"])
    return get_attachment(att_id)


def delete_attachment(att_id: str) -> None:
    """Removes the file. Replications that already ran keep their record of it, without the file."""
    att = get_attachment(att_id)
    path = attachment_path(att)
    path.unlink(missing_ok=True)
    try:
        path.parent.rmdir()
    except OSError:
        pass
    with db.tx() as conn:
        conn.execute("DELETE FROM attachments WHERE id=?", (att_id,))
    _publish(get_experiment(att["experiment_id"])["paper_id"], experiment_id=att["experiment_id"])
