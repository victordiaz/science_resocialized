"""Live replies: a persona answers when a human talks to it. Agents never trigger agents."""
from __future__ import annotations

import logging
import re
import threading

from .. import services
from ..config import settings
from ..events import bus
from ..services import Visibility
from . import prompts, runner
from .tools import AgentContext

log = logging.getLogger("paper_review.live")

# Set False in tests to run synchronously.
background = True


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def resolve_targets(thread: dict, comment: dict) -> list[dict]:
    """Built-in, enabled personas that should answer this human comment."""
    personas = {p["id"]: p for p in services.list_personas() if p["kind"] == "builtin" and p["enabled"]}
    targets: dict[str, dict] = {}
    comments = {c["id"]: c for c in thread["comments"]}
    is_root = thread["comments"][0]["id"] == comment["id"]
    if not is_root:
        direct = comments.get(comment.get("reply_to") or "")
        if direct and direct["author"]["type"] == "persona" and direct["author"]["id"] in personas:
            targets[direct["author"]["id"]] = personas[direct["author"]["id"]]
        else:
            root_author = thread["comments"][0]["author"]
            if root_author["type"] == "persona" and root_author["id"] in personas and not direct:
                targets[root_author["id"]] = personas[root_author["id"]]
    body = comment["body"].lower()
    for p in personas.values():
        if f"@{p['name'].lower()}" in body or f"@{slug(p['name'])}" in body:
            targets[p["id"]] = p
    return list(targets.values())


def on_human_comment(thread: dict, comment: dict) -> None:
    for persona in resolve_targets(thread, comment):
        if background:
            threading.Thread(target=respond, args=(thread["id"], comment["id"], persona), daemon=True).start()
        else:
            respond(thread["id"], comment["id"], persona)


def respond(thread_id: str, comment_id: str, persona: dict) -> None:
    thread = services.get_thread(thread_id)
    paper_id = thread["paper_id"]
    event = {"thread_id": thread_id, "persona_id": persona["id"], "persona_name": persona["name"], "persona_color": persona["color"]}
    bus.publish(paper_id, {"type": "live.started", **event})
    try:
        paper = services.get_paper(paper_id)
        comment = next(c for c in thread["comments"] if c["id"] == comment_id)
        ctx = AgentContext(paper_id=paper_id, persona=persona, visibility=Visibility())
        msg = prompts.live_reply_task(
            paper["title"], prompts.render_threads([thread], header="The thread:"), thread_id, comment_id, comment["author"]["name"]
        )
        client = runner.client_factory()
        final = runner.agent_loop(client, ctx, msg, max_steps=settings.live_reply_steps)
        if thread_id not in ctx.replied_threads and final:
            services.add_reply(thread_id, services.persona_author(persona), final, comment_id)
        bus.publish(paper_id, {"type": "live.finished", **event})
    except Exception as e:
        log.exception("live reply by %s failed", persona["name"])
        bus.publish(paper_id, {"type": "live.finished", **event, "error": runner._err_text(e)})


def install() -> None:
    services.on_human_comment = on_human_comment
