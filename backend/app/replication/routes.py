"""HTTP API for blind replication, plus the worker protocol (X-Worker-Token)."""
from __future__ import annotations

import asyncio
import hmac

from fastapi import APIRouter, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .. import services
from ..config import settings
from . import service

api = APIRouter(prefix="/api")


def _wrap(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except services.NotFound as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------- app side

class ExperimentPatch(BaseModel):
    title: str | None = None
    spec_md: str | None = None
    outcome_md: str | None = None


class ReplicationStart(BaseModel):
    verifier_ids: list[str] | None = None
    budget_usd: float | None = Field(None, gt=0, le=500)
    timeout_min: int | None = Field(None, ge=5, le=24 * 60)


class VerifyStart(BaseModel):
    verifier_ids: list[str]


@api.post("/papers/{paper_id}/experiments", status_code=201)
def start_extraction(paper_id: str):
    """Step 1: extract the main experiment (spec + hidden outcome) and check the spec for leaks."""
    return _wrap(service.start_extraction, paper_id)


@api.get("/papers/{paper_id}/experiments")
def list_experiments(paper_id: str):
    return _wrap(service.list_for_paper, paper_id)


@api.get("/experiments/{exp_id}")
def get_experiment(exp_id: str):
    return _wrap(service.get_experiment, exp_id)


@api.patch("/experiments/{exp_id}")
def patch_experiment(exp_id: str, body: ExperimentPatch):
    return _wrap(service.update_spec, exp_id, body.spec_md, body.title, body.outcome_md)


@api.post("/experiments/{exp_id}/leak-check")
def leak_check(exp_id: str):
    return _wrap(service.recheck_leaks, exp_id)


@api.post("/experiments/{exp_id}/replications", status_code=201)
def queue_replication(exp_id: str, body: ReplicationStart):
    """Step 2: replicate the experiment blind; the chosen verifiers run when it finishes."""
    return _wrap(service.queue_replication, exp_id, body.verifier_ids, body.budget_usd, body.timeout_min)


@api.get("/replications/{rep_id}")
def get_replication(rep_id: str, events_after: int | None = Query(None, description="Include progress events after this seq")):
    return _wrap(service.get_replication, rep_id, events_after=events_after)


@api.post("/replications/{rep_id}/cancel")
def cancel_replication(rep_id: str):
    return _wrap(service.cancel_replication, rep_id)


@api.post("/replications/{rep_id}/verifications", status_code=201)
def verify(rep_id: str, body: VerifyStart):
    return _wrap(service.start_verifications, rep_id, body.verifier_ids)


@api.get("/replications/{rep_id}/files/{path:path}")
def replication_file(rep_id: str, path: str):
    full = _wrap(service.file_path, rep_id, path)
    return FileResponse(full)


# ---------------------------------------------------------------- attachments

class AttachmentPatch(BaseModel):
    note: str


@api.post("/experiments/{exp_id}/attachments", status_code=201)
def upload_attachments(exp_id: str, files: list[UploadFile] = File(...), note: str = Form("")):
    """Attach files (any type: datasets, archives, code) for the replicator. They appear in ./inputs/."""
    _wrap(service.get_experiment, exp_id)
    out = []
    for f in files:
        out.append(_wrap(service.save_attachment, exp_id, f.filename or "file", f.file, f.content_type, note))
    return out


@api.get("/experiments/{exp_id}/attachments")
def list_attachments(exp_id: str):
    _wrap(service.get_experiment, exp_id)
    return service.list_attachments(exp_id)


@api.patch("/attachments/{att_id}")
def patch_attachment(att_id: str, body: AttachmentPatch):
    return _wrap(service.update_attachment, att_id, body.note)


@api.delete("/attachments/{att_id}", status_code=204)
def delete_attachment(att_id: str):
    _wrap(service.delete_attachment, att_id)


def _attachment_file(att_id: str) -> FileResponse:
    att = _wrap(service.get_attachment, att_id)
    path = service.attachment_path(att)
    if not path.is_file():
        raise HTTPException(404, "the file is missing on the server")
    return FileResponse(path, filename=att["filename"], media_type=att["content_type"] or "application/octet-stream")


@api.get("/attachments/{att_id}/download")
def download_attachment(att_id: str):
    return _attachment_file(att_id)


# ---------------------------------------------------------------- worker side

def _require_worker(token: str | None) -> None:
    if not token or not hmac.compare_digest(token, settings.get_worker_token()):
        raise HTTPException(401, "missing or wrong X-Worker-Token")


class ClaimBody(BaseModel):
    worker: str = "worker"


class EventsBody(BaseModel):
    events: list[dict] = Field(default_factory=list)
    workdir: str | None = None


class CompleteBody(BaseModel):
    status: str
    report_md: str | None = None
    cost_usd: float | None = None
    error: str | None = None
    files: list[dict] = Field(default_factory=list, description="[{path, content_b64}]")


@api.post("/worker/claim")
def worker_claim(body: ClaimBody, x_worker_token: str | None = Header(None)):
    _require_worker(x_worker_token)
    return {"job": service.claim_job(body.worker[:80])}


@api.get("/worker/attachments/{att_id}")
def worker_attachment(att_id: str, x_worker_token: str | None = Header(None)):
    _require_worker(x_worker_token)
    return _attachment_file(att_id)


@api.post("/worker/replications/{rep_id}/events")
def worker_events(rep_id: str, body: EventsBody, x_worker_token: str | None = Header(None)):
    _require_worker(x_worker_token)
    return _wrap(service.add_events, rep_id, body.events, body.workdir)


@api.post("/worker/replications/{rep_id}/complete")
async def worker_complete(rep_id: str, body: CompleteBody, x_worker_token: str | None = Header(None)):
    _require_worker(x_worker_token)
    return await asyncio.to_thread(_wrap, service.complete_job, rep_id, body.status, body.report_md, body.cost_usd, body.error, body.files)
