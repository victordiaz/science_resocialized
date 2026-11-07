"""Tools exposed to built-in agents. They call the same services as the HTTP API."""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Callable

from .. import pdf, services
from ..services import Visibility

RECT_SCHEMA = {
    "type": "object",
    "properties": {
        "x0": {"type": "number"},
        "y0": {"type": "number"},
        "x1": {"type": "number"},
        "y1": {"type": "number"},
    },
    "required": ["x0", "y0", "x1", "y1"],
    "additionalProperties": False,
}

TOOL_DEFS: list[dict] = [
    {
        "name": "read_full_text",
        "description": "Plain text of the whole paper, with '=== Page N ===' markers. Start here.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "get_page_text",
        "description": "Plain text of one page (1-based).",
        "input_schema": {
            "type": "object",
            "properties": {"page": {"type": "integer", "minimum": 1}},
            "required": ["page"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_page_layout",
        "description": "Every text line on a page with its bounding box as page fractions (x0,y0,x1,y1; "
        "0..1, origin top-left). Use it to work out rects for box anchors.",
        "input_schema": {
            "type": "object",
            "properties": {"page": {"type": "integer", "minimum": 1}},
            "required": ["page"],
            "additionalProperties": False,
        },
    },
    {
        "name": "view_page",
        "description": "Render a page as an image. Optionally pass `region` (page fractions) to zoom into "
        "part of it, such as a figure, table or equation.",
        "input_schema": {
            "type": "object",
            "properties": {"page": {"type": "integer", "minimum": 1}, "region": RECT_SCHEMA},
            "required": ["page"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_threads",
        "description": "Comment threads you can currently see, with ids, anchors and all comments. "
        "Optionally filter by page.",
        "input_schema": {
            "type": "object",
            "properties": {"page": {"type": "integer", "minimum": 1}},
            "additionalProperties": False,
        },
    },
    {
        "name": "read_replications",
        "description": "Results of blind replications of this paper's main experiment: the replicator's "
        "report and the verification reports. Cite them when they bear on a claim.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "create_comment",
        "description": "Start a new comment thread. Anchor it with `page` plus either `quote` (exact text "
        "from that page) or `rects` (boxes as page fractions). Omit `page` for a comment on the whole paper.",
        "input_schema": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Markdown comment text."},
                "page": {"type": "integer", "minimum": 1},
                "quote": {"type": "string"},
                "rects": {"type": "array", "items": RECT_SCHEMA},
            },
            "required": ["body"],
            "additionalProperties": False,
        },
    },
    {
        "name": "reply",
        "description": "Reply in an existing thread. Pass `reply_to` (a comment id) to answer a specific comment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thread_id": {"type": "string"},
                "body": {"type": "string"},
                "reply_to": {"type": "string"},
            },
            "required": ["thread_id", "body"],
            "additionalProperties": False,
        },
    },
]


class ToolError(Exception):
    pass


@dataclass
class AgentContext:
    paper_id: str
    persona: dict
    visibility: Visibility
    run_id: str | None = None
    round: int | None = None
    comments_written: int = 0
    replies_written: int = 0
    replied_threads: set[str] = field(default_factory=set)
    # Called after every tool call with (api_call, what_it_is_doing, http_like_status).
    on_activity: Callable[[str, str, int], None] | None = None


def _text(s: str) -> list[dict]:
    return [{"type": "text", "text": s}]


def _require(inp: dict, key: str, typ: type):
    if key not in inp or not isinstance(inp[key], typ) or isinstance(inp[key], bool):
        raise ToolError(f"`{key}` is required and must be {typ.__name__}")
    return inp[key]


def describe_call(paper_id: str, name: str, inp: dict) -> tuple[str, str]:
    """The equivalent HTTP API call, and a plain description of what the agent is doing."""
    base = f"/api/papers/{paper_id}"
    page = inp.get("page") if isinstance(inp, dict) else None
    if name == "read_full_text":
        return f"GET  {base}/text", "Reading the full text"
    if name == "get_page_text":
        return f"GET  {base}/pages/{page}/text", f"Reading page {page}"
    if name == "get_page_layout":
        return f"GET  {base}/pages/{page}/text?layout=true", f"Measuring the layout of page {page}"
    if name == "view_page":
        zoom = " (zoomed in)" if inp.get("region") else ""
        return f"GET  {base}/pages/{page}/image", f"Looking at the page {page} image{zoom}"
    if name == "list_threads":
        return f"GET  {base}/threads", "Reading the comment threads"
    if name == "read_replications":
        return f"GET  {base}/experiments", "Reading the replication reports"
    if name == "create_comment":
        if page is None:
            return f"POST {base}/threads  {{whole paper}}", "Writing a comment on the whole paper"
        how = "boxes" if inp.get("rects") and not inp.get("quote") else "quote"
        return f"POST {base}/threads  {{page: {page}, {how}}}", f"Writing a comment on p.{page}"
    if name == "reply":
        return f"POST /api/threads/{inp.get('thread_id')}/replies", "Replying in a thread"
    return name, name


def execute(ctx: AgentContext, name: str, inp: dict) -> list[dict]:
    """Run a tool, reporting it through ctx.on_activity. Raises ToolError for agent-fixable errors."""
    call, doing = describe_call(ctx.paper_id, name, inp if isinstance(inp, dict) else {})
    ok_code = 201 if name in ("create_comment", "reply") else 200
    try:
        result = _execute(ctx, name, inp)
    except ToolError as e:
        if ctx.on_activity:
            ctx.on_activity(call, doing, 404 if "not found" in str(e) and "quote" not in str(e) else 422)
        raise
    if ctx.on_activity:
        ctx.on_activity(call, doing, ok_code)
    return result


def _execute(ctx: AgentContext, name: str, inp: dict) -> list[dict]:
    if not isinstance(inp, dict):
        raise ToolError("tool input must be an object")
    author = services.persona_author(ctx.persona)
    try:
        if name == "read_full_text":
            return _text(services.full_text(ctx.paper_id))
        if name == "get_page_text":
            page = _require(inp, "page", int)
            return _text(services.page_data(ctx.paper_id, page)["text"] or "(no text on this page)")
        if name == "get_page_layout":
            page = _require(inp, "page", int)
            lines = pdf.page_lines(services.page_data(ctx.paper_id, page)["words"])
            out = [f"Page {page} lines (x0 y0 x1 y1 | text):"]
            out += [f"{l['x0']:.3f} {l['y0']:.3f} {l['x1']:.3f} {l['y1']:.3f} | {l['text']}" for l in lines]
            return _text("\n".join(out))
        if name == "view_page":
            page = _require(inp, "page", int)
            region = inp.get("region")
            dpi = 200 if region else 110
            png = pdf.render_png(services.paper_pdf_path(ctx.paper_id), page, dpi=dpi, region=region)
            label = f"Page {page}" + (f" region {json.dumps(region)}" if region else "")
            return [
                {"type": "text", "text": label},
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.standard_b64encode(png).decode()}},
            ]
        if name == "list_threads":
            page = inp.get("page")
            threads = services.list_threads(ctx.paper_id, visibility=ctx.visibility, page=page)
            from .prompts import render_threads

            return _text(render_threads(threads))
        if name == "read_replications":
            from ..replication import service as replication

            return _text(replication.summary_for_agents(ctx.paper_id))
        if name == "create_comment":
            body = _require(inp, "body", str)
            anchor = None
            if inp.get("page") is not None:
                anchor = {"page": inp["page"], "quote": inp.get("quote"), "rects": inp.get("rects")}
            thread = services.create_thread(ctx.paper_id, author, body, anchor, run_id=ctx.run_id, round_=ctx.round)
            ctx.comments_written += 1
            a = thread["anchor"]
            where = f"page {a['page']}, {len(a['rects'])} rect(s)" if a else "whole paper"
            return _text(f"Created thread {thread['id']} ({where}).")
        if name == "reply":
            thread_id = _require(inp, "thread_id", str)
            body = _require(inp, "body", str)
            thread = services.get_thread(thread_id)
            if thread["paper_id"] != ctx.paper_id:
                raise ToolError("that thread belongs to another paper")
            c = services.add_reply(thread_id, author, body, inp.get("reply_to"), run_id=ctx.run_id, round_=ctx.round)
            ctx.replies_written += 1
            ctx.replied_threads.add(thread_id)
            return _text(f"Replied in thread {thread_id} (comment {c['id']}).")
    except (services.AnchorError, services.NotFound, ValueError) as e:
        raise ToolError(str(e)) from e
    raise ToolError(f"unknown tool {name}")
