"""Built-in agent runner: Claude tool-use loops for review runs (rounds) and live replies."""
from __future__ import annotations

import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

import anthropic

from .. import db, services
from ..config import settings
from ..events import bus
from ..services import Visibility
from . import prompts
from .tools import TOOL_DEFS, AgentContext, ToolError, execute

log = logging.getLogger("paper_review.runner")

# Models that accept server-side refusal fallback (`fallbacks: "default"`).
FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5", "claude-fable-5-1", "claude-fable-5"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def _default_client_factory():
    return anthropic.Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else anthropic.Anthropic()


# Replaceable in tests.
client_factory: Callable[[], Any] = _default_client_factory

_cancel_events: dict[str, threading.Event] = {}


class Cancelled(Exception):
    pass


# ---------------------------------------------------------------- model loop

def call_model(client, persona: dict, system: str, messages: list, tools: list | None = None) -> Any:
    model = persona.get("model") or services.DEFAULT_MODEL
    kwargs = dict(
        model=model,
        max_tokens=16000,
        system=system,
        tools=TOOL_DEFS if tools is None else tools,
        messages=messages,
        cache_control={"type": "ephemeral"},
        output_config={"effort": settings.agent_effort},
    )
    if model in FALLBACK_MODELS:
        return client.beta.messages.create(**kwargs, betas=[FALLBACK_BETA], fallbacks="default")
    return client.messages.create(**kwargs)


def agent_loop(
    client,
    ctx: AgentContext,
    user_msg: str,
    *,
    max_steps: int,
    cancel: threading.Event | None = None,
    on_step: Callable[[int], None] | None = None,
    system: str | None = None,
    tools: list | None = None,
    executor: Callable[[Any, str, dict], list] | None = None,
) -> str:
    """Run one agent until it stops calling tools. Returns its final text. Append-only history.

    Defaults to a reviewer persona (review prompt, review tools); other agents pass their
    own system prompt, tool definitions and executor."""
    if system is None:
        system = prompts.BASE_SYSTEM + "\n\n# Persona: " + ctx.persona["name"] + "\n" + (ctx.persona.get("prompt") or "")
    run_tool = executor or execute
    messages: list = [{"role": "user", "content": user_msg}]
    final_text = ""
    for step in range(1, max_steps + 1):
        if cancel is not None and cancel.is_set():
            raise Cancelled()
        response = call_model(client, ctx.persona, system, messages, tools)
        if on_step:
            on_step(step)
        if response.stop_reason == "refusal":
            raise RuntimeError("the model declined this request (safety classifier)")
        texts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
        if texts:
            final_text = "\n".join(texts).strip()
        tool_uses = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason == "pause_turn":
            continue
        if not tool_uses:
            return final_text
        results = []
        for tu in tool_uses:
            try:
                content = run_tool(ctx, tu.name, tu.input)
                results.append({"type": "tool_result", "tool_use_id": tu.id, "content": content})
            except ToolError as e:
                results.append({"type": "tool_result", "tool_use_id": tu.id, "content": f"Error: {e}", "is_error": True})
        if step == max_steps - 1:
            results.append({"type": "text", "text": "You have one step left. Finish now with your final message."})
        messages.append({"role": "user", "content": results})
    return final_text


# ---------------------------------------------------------------- runs

def _run_obj(conn, run_row, *, events: bool = True) -> dict:
    tasks = conn.execute(
        """SELECT rt.*, p.name AS persona_name, p.color AS persona_color
           FROM run_tasks rt LEFT JOIN personas p ON p.id = rt.persona_id
           WHERE rt.run_id=? ORDER BY rt.round, p.name""",
        (run_row["id"],),
    ).fetchall()
    d = dict(run_row)
    d["persona_ids"] = json.loads(d.pop("persona_ids_json"))
    d["include_initial"] = bool(d["include_initial"])
    d["tasks"] = [dict(t) for t in tasks]
    d["number"] = conn.execute(
        "SELECT COUNT(*) AS n FROM runs WHERE paper_id=? AND created_at<=?", (d["paper_id"], d["created_at"])
    ).fetchone()["n"]
    if events:
        rows = conn.execute(
            """SELECT e.*, p.name AS persona_name, p.color AS persona_color FROM run_events e
               LEFT JOIN personas p ON p.id=e.persona_id WHERE e.run_id=? ORDER BY e.seq DESC LIMIT 60""",
            (d["id"],),
        ).fetchall()
        d["events"] = [dict(r) for r in rows]
    return d


def get_run(run_id: str) -> dict:
    with db.tx() as conn:
        r = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if not r:
            raise services.NotFound(f"run {run_id} not found")
        return _run_obj(conn, r)


def list_runs(paper_id: str) -> list[dict]:
    with db.tx() as conn:
        rows = conn.execute("SELECT * FROM runs WHERE paper_id=? ORDER BY created_at DESC LIMIT 20", (paper_id,)).fetchall()
        return [_run_obj(conn, r, events=(i == 0)) for i, r in enumerate(rows)]


def _update_run(run_id: str, paper_id: str, **fields) -> None:
    sets = ", ".join(f"{k}=?" for k in fields)
    with db.tx() as conn:
        conn.execute(f"UPDATE runs SET {sets} WHERE id=?", (*fields.values(), run_id))
    bus.publish(paper_id, {"type": "run.updated", "run_id": run_id})


def _update_task(task_id: str, run_id: str, paper_id: str, **fields) -> None:
    sets = ", ".join(f"{k}=?" for k in fields)
    with db.tx() as conn:
        conn.execute(f"UPDATE run_tasks SET {sets} WHERE id=?", (*fields.values(), task_id))
    bus.publish(paper_id, {"type": "run.updated", "run_id": run_id})


def start_run(paper_id: str, persona_ids: list[str], rounds: int, include_initial: bool = True, *, background: bool = True) -> dict:
    paper = services.get_paper(paper_id)
    personas = [services.get_persona(pid) for pid in persona_ids]
    personas = [p for p in personas if p["kind"] == "builtin"]
    if not personas:
        raise ValueError("pick at least one built-in persona")
    rounds = int(rounds)
    if rounds < 0 or rounds > 5:
        raise ValueError("discussion rounds must be between 0 and 5")
    if not include_initial and rounds == 0:
        raise ValueError("a discussion-only run needs at least one discussion round")
    round_numbers = ([0] if include_initial else []) + list(range(1, rounds + 1))
    run_id = services.new_id("run")
    with db.tx() as conn:
        conn.execute(
            """INSERT INTO runs (id, paper_id, persona_ids_json, rounds, include_initial, status, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (run_id, paper_id, json.dumps([p["id"] for p in personas]), rounds, int(include_initial), "queued", services.now()),
        )
        for rn in round_numbers:
            for p in personas:
                conn.execute(
                    "INSERT INTO run_tasks (id, run_id, persona_id, round, status) VALUES (?,?,?,?,?)",
                    (services.new_id("tsk"), run_id, p["id"], rn, "pending"),
                )
    cancel = threading.Event()
    _cancel_events[run_id] = cancel
    args = (run_id, paper, personas, round_numbers, rounds, cancel)
    if background:
        threading.Thread(target=_execute_run, args=args, daemon=True, name=f"run-{run_id}").start()
    else:
        _execute_run(*args)
    return get_run(run_id)


def cancel_run(run_id: str) -> dict:
    run = get_run(run_id)
    ev = _cancel_events.get(run_id)
    if ev is not None and run["status"] in ("queued", "running"):
        ev.set()
    elif run["status"] in ("queued", "running"):  # orphaned (e.g. after restart)
        _update_run(run_id, run["paper_id"], status="cancelled", finished_at=services.now())
    return get_run(run_id)


def _execute_run(run_id: str, paper: dict, personas: list[dict], round_numbers: list[int], rounds: int, cancel: threading.Event) -> None:
    paper_id = paper["id"]
    _update_run(run_id, paper_id, status="running")
    try:
        client = client_factory()
    except Exception as e:  # e.g. no credentials
        _fail_pending(run_id, paper_id, f"Could not create Anthropic client: {e}")
        _update_run(run_id, paper_id, status="failed", error=f"Could not create Anthropic client: {e}", finished_at=services.now())
        return
    try:
        for rn in round_numbers:
            if cancel.is_set():
                break
            _update_run(run_id, paper_id, current_round=rn)
            snapshot = services.max_comment_seq(paper_id)
            with db.tx() as conn:
                tasks = {r["persona_id"]: r["id"] for r in conn.execute(
                    "SELECT id, persona_id FROM run_tasks WHERE run_id=? AND round=?", (run_id, rn)
                ).fetchall()}
            with ThreadPoolExecutor(max_workers=len(personas)) as pool:
                futures = [
                    pool.submit(_run_task, client, run_id, tasks[p["id"]], paper, p, rn, rounds, snapshot, cancel)
                    for p in personas
                ]
                for f in futures:
                    f.result()
        if cancel.is_set():
            _fail_pending(run_id, paper_id, None, status="cancelled")
            _update_run(run_id, paper_id, status="cancelled", finished_at=services.now())
            return
        with db.tx() as conn:
            failed = conn.execute(
                "SELECT COUNT(*) AS n FROM run_tasks WHERE run_id=? AND status='failed'", (run_id,)
            ).fetchone()["n"]
            total = conn.execute("SELECT COUNT(*) AS n FROM run_tasks WHERE run_id=?", (run_id,)).fetchone()["n"]
        status = "failed" if failed == total else "completed"
        err = f"{failed} of {total} agent tasks failed" if failed else None
        _update_run(run_id, paper_id, status=status, error=err, finished_at=services.now())
    except Exception as e:
        log.exception("run %s crashed", run_id)
        _update_run(run_id, paper_id, status="failed", error=str(e), finished_at=services.now())
    finally:
        _cancel_events.pop(run_id, None)


def _fail_pending(run_id: str, paper_id: str, error: str | None, status: str = "failed") -> None:
    with db.tx() as conn:
        conn.execute(
            "UPDATE run_tasks SET status=?, error=?, finished_at=? WHERE run_id=? AND status IN ('pending','running')",
            (status, error, services.now(), run_id),
        )
    bus.publish(paper_id, {"type": "run.updated", "run_id": run_id})


def _run_task(client, run_id: str, task_id: str, paper: dict, persona: dict, rn: int, rounds: int, snapshot: int, cancel: threading.Event) -> None:
    paper_id = paper["id"]
    if cancel.is_set():
        _update_task(task_id, run_id, paper_id, status="cancelled", finished_at=services.now())
        return
    if rn == 0:
        vis = Visibility(persona_id=persona["id"], only_humans_and_self=True)
    else:
        vis = Visibility(persona_id=persona["id"], max_seq=snapshot)
    def on_activity(call: str, doing: str, code: int) -> None:
        with db.tx() as conn:
            conn.execute(
                "INSERT INTO run_events (run_id, persona_id, round, call, code, at) VALUES (?,?,?,?,?,?)",
                (run_id, persona["id"], rn, call, code, services.now()),
            )
        _update_task(task_id, run_id, paper_id, activity=doing, comment_count=ctx.comments_written, reply_count=ctx.replies_written)

    ctx = AgentContext(paper_id=paper_id, persona=persona, visibility=vis, run_id=run_id, round=rn, on_activity=on_activity)
    _update_task(task_id, run_id, paper_id, status="running", started_at=services.now(), activity="Reading the paper" if rn == 0 else "Reading the other reviewers' comments")
    try:
        visible = services.list_threads(paper_id, visibility=vis)
        if rn == 0:
            existing = prompts.render_threads(
                visible, header="Comments already on this paper that you can see (yours from earlier, and humans'). Don't duplicate them:"
            ) if visible else ""
            msg = prompts.review_task(paper["title"], paper["page_count"], existing)
        else:
            msg = prompts.discussion_task(paper["title"], rn, rounds, prompts.render_threads(visible))

        def on_step(step: int) -> None:
            _update_task(task_id, run_id, paper_id, steps=step)

        agent_loop(client, ctx, msg, max_steps=settings.max_agent_steps, cancel=cancel, on_step=on_step)
        counts = dict(comment_count=ctx.comments_written, reply_count=ctx.replies_written)
        _update_task(task_id, run_id, paper_id, status="done", activity="Finished this round", finished_at=services.now(), **counts)
    except Cancelled:
        counts = dict(comment_count=ctx.comments_written, reply_count=ctx.replies_written)
        _update_task(task_id, run_id, paper_id, status="cancelled", activity="Stopped", finished_at=services.now(), **counts)
    except Exception as e:
        log.exception("task %s failed", task_id)
        counts = dict(comment_count=ctx.comments_written, reply_count=ctx.replies_written)
        _update_task(task_id, run_id, paper_id, status="failed", error=_err_text(e), activity="Failed", finished_at=services.now(), **counts)


def _err_text(e: Exception) -> str:
    if isinstance(e, anthropic.AuthenticationError):
        return "Anthropic authentication failed: set ANTHROPIC_API_KEY in backend/.env"
    if isinstance(e, anthropic.NotFoundError):
        return f"Model not found: {e}"
    if isinstance(e, anthropic.RateLimitError):
        return "Rate limited by the Anthropic API; try again later"
    if isinstance(e, anthropic.APIConnectionError):
        return "Could not reach the Anthropic API"
    if isinstance(e, anthropic.APIStatusError):
        return f"Anthropic API error {e.status_code}: {e.message}"
    return str(e) or e.__class__.__name__


def mark_interrupted_runs() -> None:
    """Runs can't survive a restart; mark leftovers so the UI doesn't show them as live."""
    with db.tx() as conn:
        conn.execute(
            "UPDATE runs SET status='failed', error='server restarted', finished_at=? WHERE status IN ('queued','running')",
            (services.now(),),
        )
        conn.execute(
            "UPDATE run_tasks SET status='failed', error='server restarted' WHERE status IN ('pending','running')"
        )
