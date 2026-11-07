"""HTTP API. Agents authenticate with `Authorization: Bearer <persona api key>`; no header = human."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse

from . import pdf, services
from .agents import runner
from .config import settings
from .events import bus
from .schemas import PaperPatch, PersonaCreate, PersonaPatch, ReplyCreate, RunCreate, ThreadCreate, ThreadPatch

api = APIRouter(prefix="/api")


def current_author(
    authorization: str | None = Header(None),
    x_user_name: str | None = Header(None),
) -> services.Author:
    if authorization:
        scheme, _, key = authorization.partition(" ")
        if scheme.lower() != "bearer" or not key:
            raise HTTPException(401, "use 'Authorization: Bearer <persona api key>'")
        persona = services.persona_by_key(key.strip())
        if not persona:
            raise HTTPException(401, "unknown or revoked persona api key")
        return services.persona_author(persona)
    return services.human_author(x_user_name)


def _wrap(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except services.NotFound as e:
        raise HTTPException(404, str(e))
    except services.AnchorError as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------- status

@api.get("/status")
def status():
    import os

    return {
        "anthropic_configured": bool(settings.anthropic_api_key or os.environ.get("ANTHROPIC_AUTH_TOKEN")),
        "max_agent_steps": settings.max_agent_steps,
    }


@api.get("/whoami")
def whoami(author: services.Author = Depends(current_author)):
    return author


# ---------------------------------------------------------------- papers

@api.get("/papers")
def list_papers():
    return services.list_papers()


@api.post("/papers", status_code=201)
async def upload_paper(file: UploadFile = File(...), title: str | None = Query(None)):
    data = await file.read()
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "file is not a PDF")
    return await asyncio.to_thread(_wrap, services.create_paper, file.filename or "paper.pdf", data, title)


@api.get("/papers/{paper_id}")
def get_paper(paper_id: str):
    return _wrap(services.get_paper, paper_id)


@api.patch("/papers/{paper_id}")
def patch_paper(paper_id: str, body: PaperPatch):
    """Edit a paper's details. A title set here is kept when details are re-extracted."""
    return _wrap(services.update_paper, paper_id, source="user", **body.model_dump(exclude_none=True))


@api.post("/papers/{paper_id}/metadata")
def extract_metadata(paper_id: str):
    """Re-extract title, authors, year, venue, abstract, keywords and ids (runs in the background)."""
    from . import metadata

    _wrap(services.get_paper, paper_id)
    metadata.start(paper_id)
    return services.get_paper(paper_id)


@api.delete("/papers/{paper_id}", status_code=204)
def delete_paper(paper_id: str):
    _wrap(services.delete_paper, paper_id)


@api.get("/papers/{paper_id}/file")
def paper_file(paper_id: str):
    path = _wrap(services.paper_pdf_path, paper_id)
    return FileResponse(path, media_type="application/pdf")


@api.get("/papers/{paper_id}/text", response_class=Response)
def paper_text(paper_id: str):
    return Response(_wrap(services.full_text, paper_id), media_type="text/plain; charset=utf-8")


@api.get("/papers/{paper_id}/pages/{n}/text")
def page_text(paper_id: str, n: int, layout: bool = Query(False, description="Include line boxes")):
    p = _wrap(services.page_data, paper_id, n)
    out = {"number": p["number"], "width": p["width"], "height": p["height"], "text": p["text"], "words": p["words"]}
    if layout:
        out["lines"] = pdf.page_lines(p["words"])
    return out


@api.get("/papers/{paper_id}/pages/{n}/image")
def page_image(
    paper_id: str,
    n: int,
    dpi: int = Query(110, ge=36, le=300),
    x0: float | None = None,
    y0: float | None = None,
    x1: float | None = None,
    y1: float | None = None,
):
    path = _wrap(services.paper_pdf_path, paper_id)
    region = None
    if None not in (x0, y0, x1, y1):
        region = {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
    try:
        png = pdf.render_png(path, n, dpi=dpi, region=region)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return Response(png, media_type="image/png", headers={"Cache-Control": "max-age=3600"})


# ---------------------------------------------------------------- threads

@api.get("/papers/{paper_id}/threads")
def list_threads(paper_id: str, author_id: str | None = None, status: str | None = None, page: int | None = None):
    _wrap(services.get_paper, paper_id)
    return services.list_threads(paper_id, author_id=author_id, status=status, page=page)


@api.post("/papers/{paper_id}/threads", status_code=201)
def create_thread(paper_id: str, body: ThreadCreate, author: services.Author = Depends(current_author)):
    anchor = body.anchor.model_dump() if body.anchor else None
    return _wrap(services.create_thread, paper_id, author, body.body, anchor)


@api.get("/threads/{thread_id}")
def get_thread(thread_id: str):
    return _wrap(services.get_thread, thread_id)


@api.post("/threads/{thread_id}/replies", status_code=201)
def reply(thread_id: str, body: ReplyCreate, author: services.Author = Depends(current_author)):
    return _wrap(services.add_reply, thread_id, author, body.body, body.reply_to)


@api.patch("/threads/{thread_id}")
def patch_thread(thread_id: str, body: ThreadPatch):
    return _wrap(services.set_thread_status, thread_id, body.status)


@api.delete("/threads/{thread_id}", status_code=204)
def delete_thread(thread_id: str):
    _wrap(services.delete_thread, thread_id)


# ---------------------------------------------------------------- personas

@api.get("/personas")
def list_personas():
    return services.list_personas(with_stats=True)


@api.post("/personas", status_code=201)
def create_persona(body: PersonaCreate):
    return _wrap(services.create_persona, **body.model_dump())


@api.get("/personas/{persona_id}")
def get_persona(persona_id: str):
    return _wrap(services.get_persona, persona_id)


@api.patch("/personas/{persona_id}")
def patch_persona(persona_id: str, body: PersonaPatch):
    return _wrap(services.update_persona, persona_id, **body.model_dump())


@api.delete("/personas/{persona_id}", status_code=204)
def delete_persona(persona_id: str):
    _wrap(services.delete_persona, persona_id)


@api.post("/personas/{persona_id}/regenerate-key")
def regenerate_key(persona_id: str):
    return {"api_key": _wrap(services.regenerate_key, persona_id)}


# ---------------------------------------------------------------- runs

@api.post("/papers/{paper_id}/runs", status_code=201)
def start_run(paper_id: str, body: RunCreate):
    return _wrap(runner.start_run, paper_id, body.persona_ids, body.rounds, body.include_initial)


@api.get("/papers/{paper_id}/runs")
def list_runs(paper_id: str):
    return runner.list_runs(paper_id)


@api.get("/runs/{run_id}")
def get_run(run_id: str):
    return _wrap(runner.get_run, run_id)


@api.post("/runs/{run_id}/cancel")
def cancel_run(run_id: str):
    return _wrap(runner.cancel_run, run_id)


# ---------------------------------------------------------------- events (SSE)

@api.get("/papers/{paper_id}/events")
async def events(paper_id: str, request: Request):
    q = bus.subscribe(paper_id)

    async def stream():
        try:
            yield "event: ready\ndata: {}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {json.dumps(ev)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            bus.unsubscribe(paper_id, q)

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
