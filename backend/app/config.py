"""Runtime settings, read from environment (and backend/.env if present)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")


@dataclass
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("PAPER_REVIEW_DATA", BACKEND_DIR / "data")))
    anthropic_api_key: str | None = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY") or None)
    max_agent_steps: int = field(default_factory=lambda: int(os.environ.get("MAX_AGENT_STEPS", "40")))
    live_reply_steps: int = field(default_factory=lambda: int(os.environ.get("LIVE_REPLY_STEPS", "12")))
    agent_effort: str = field(default_factory=lambda: os.environ.get("AGENT_EFFORT", "high"))
    seed: bool = field(default_factory=lambda: os.environ.get("PAPER_REVIEW_SEED", "1") == "1")
    frontend_dist: Path = field(default_factory=lambda: BACKEND_DIR.parent / "frontend" / "dist")
    # Blind replication
    worker_token: str | None = field(default_factory=lambda: os.environ.get("WORKER_TOKEN") or None)
    local_worker: bool = field(default_factory=lambda: os.environ.get("LOCAL_WORKER", "1") == "1")
    replication_budget_usd: float = field(default_factory=lambda: float(os.environ.get("REPLICATION_BUDGET_USD", "10")))
    replication_timeout_min: int = field(default_factory=lambda: int(os.environ.get("REPLICATION_TIMEOUT_MIN", "120")))
    pipeline_model: str = field(default_factory=lambda: os.environ.get("PIPELINE_MODEL", "claude-sonnet-5-5"))
    attachment_max_mb: int = field(default_factory=lambda: int(os.environ.get("ATTACHMENT_MAX_MB", "2048")))
    public_url: str = field(default_factory=lambda: os.environ.get("PUBLIC_URL", "http://127.0.0.1:8000"))

    @property
    def db_path(self) -> Path:
        return self.data_dir / "paper_review.db"

    @property
    def pdf_dir(self) -> Path:
        return self.data_dir / "pdfs"

    @property
    def replication_dir(self) -> Path:
        """Uploaded replication outputs (report, code, results), per replication id."""
        return self.data_dir / "replications"

    @property
    def attachment_dir(self) -> Path:
        """Files people attach to experiments for the replicator."""
        return self.data_dir / "attachments"

    def get_worker_token(self) -> str:
        """WORKER_TOKEN from the environment, else one generated and kept in the data dir."""
        if self.worker_token:
            return self.worker_token
        import secrets

        self.ensure_dirs()
        path = self.data_dir / "worker_token"
        if not path.exists():
            path.write_text(secrets.token_urlsafe(32))
            path.chmod(0o600)
        self.worker_token = path.read_text().strip()
        return self.worker_token

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.replication_dir.mkdir(parents=True, exist_ok=True)
        self.attachment_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
