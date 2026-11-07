"""FastAPI app entrypoint: `uvicorn app.main:app --reload` from backend/."""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import db, metadata, seed
from .agents import live, runner
from .config import settings
from .replication import service as replication
from .replication.routes import api as replication_api
from .routes import api

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("paper_review")

WORKER_SCRIPT = settings.frontend_dist.parent.parent / "worker" / "replicate_worker.py"


def start_local_worker() -> subprocess.Popen | None:
    """Run the replication worker on this machine, as its own process (same script a remote machine runs)."""
    if not WORKER_SCRIPT.exists():
        log.warning("replication worker script not found at %s", WORKER_SCRIPT)
        return None
    env = dict(os.environ)
    if settings.anthropic_api_key:
        env["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    logfile = open(settings.data_dir / "worker.log", "ab")
    proc = subprocess.Popen(
        [
            sys.executable, str(WORKER_SCRIPT),
            "--url", settings.public_url,
            "--token", settings.get_worker_token(),
            "--workdir", str(settings.data_dir / "replication_work"),
            "--name", "local",
        ],
        env=env, stdout=logfile, stderr=subprocess.STDOUT,
    )
    log.info("started local replication worker (pid %s), log: %s", proc.pid, settings.data_dir / "worker.log")
    return proc


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db()
    runner.mark_interrupted_runs()
    replication.mark_interrupted()
    live.install()
    metadata.install()
    if settings.seed:
        seed.seed_if_empty()
    metadata.resume_unfinished()
    worker = start_local_worker() if settings.local_worker else None
    yield
    if worker and worker.poll() is None:
        worker.terminate()


app = FastAPI(
    title="Science Resocialized API",
    description="Anchored, threaded review comments on research PDFs for AI personas and humans. "
    "Agents authenticate with `Authorization: Bearer <persona api key>`.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(api)
app.include_router(replication_api)

# Serve the built frontend if present (production mode).
if settings.frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=settings.frontend_dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        # Files from frontend/public (favicons, brand assets) are copied into dist as-is.
        root = settings.frontend_dist.resolve()
        f = (root / path).resolve()
        if path and f.is_file() and f.is_relative_to(root):
            return FileResponse(f)
        return FileResponse(root / "index.html")
