"""SQLite storage. One short-lived connection per unit of work (safe across threads)."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    page_count INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    authors_json TEXT NOT NULL DEFAULT '[]',
    year INTEGER,
    venue TEXT,
    abstract TEXT,
    keywords_json TEXT NOT NULL DEFAULT '[]',
    field TEXT,
    doc_type TEXT,
    arxiv_id TEXT,
    doi TEXT,
    title_source TEXT NOT NULL DEFAULT 'pdf',
    metadata_status TEXT NOT NULL DEFAULT 'none',
    metadata_error TEXT
);

CREATE TABLE IF NOT EXISTS pages (
    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    width REAL NOT NULL,
    height REAL NOT NULL,
    text TEXT NOT NULL,
    words_json TEXT NOT NULL,
    PRIMARY KEY (paper_id, number)
);

CREATE TABLE IF NOT EXISTS personas (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind IN ('builtin', 'external')),
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    prompt TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT 'claude-sonnet-5-5',
    tagline TEXT NOT NULL DEFAULT '',
    enabled INTEGER NOT NULL DEFAULT 1,
    api_key_hash TEXT,
    created_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    page INTEGER,
    rects_json TEXT NOT NULL DEFAULT '[]',
    quote TEXT,
    anchor_kind TEXT,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    thread_id TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    author_type TEXT NOT NULL CHECK (author_type IN ('human', 'persona')),
    author_id TEXT,
    author_name TEXT NOT NULL,
    author_color TEXT NOT NULL,
    body TEXT NOT NULL,
    reply_to TEXT,
    run_id TEXT,
    round INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS comments_thread ON comments(thread_id, seq);

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    persona_ids_json TEXT NOT NULL,
    rounds INTEGER NOT NULL,
    include_initial INTEGER NOT NULL,
    status TEXT NOT NULL,
    current_round INTEGER,
    error TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS run_tasks (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    persona_id TEXT NOT NULL,
    round INTEGER NOT NULL,
    status TEXT NOT NULL,
    steps INTEGER NOT NULL DEFAULT 0,
    comment_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    activity TEXT,
    error TEXT,
    started_at TEXT,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS run_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    persona_id TEXT NOT NULL,
    round INTEGER NOT NULL,
    call TEXT NOT NULL,
    code INTEGER NOT NULL,
    at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS run_events_run ON run_events(run_id, seq);

-- Blind replication -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    status TEXT NOT NULL,            -- extracting | checking | ready | needs_review | failed
    title TEXT NOT NULL DEFAULT '',
    spec_md TEXT NOT NULL DEFAULT '', -- what the replicator sees
    outcome_md TEXT NOT NULL DEFAULT '', -- hidden from the replicator
    leak_check_md TEXT,
    leak_found INTEGER,
    verifier_ids_json TEXT NOT NULL DEFAULT '[]',
    budget_usd REAL NOT NULL DEFAULT 10,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS replications (
    id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    status TEXT NOT NULL,            -- queued | running | done | failed | cancelled
    spec_md TEXT NOT NULL,           -- the exact spec this run was given
    verifier_ids_json TEXT NOT NULL DEFAULT '[]',
    budget_usd REAL NOT NULL DEFAULT 10,
    timeout_min INTEGER NOT NULL DEFAULT 120,
    worker TEXT,
    workdir TEXT,
    report_md TEXT,
    cost_usd REAL,
    cancel_requested INTEGER NOT NULL DEFAULT 0,
    heartbeat_at TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS replication_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    replication_id TEXT NOT NULL REFERENCES replications(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,              -- text | tool | result | stderr | info
    text TEXT NOT NULL,
    at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS replication_events_rep ON replication_events(replication_id, seq);

CREATE TABLE IF NOT EXISTS verifications (
    id TEXT PRIMARY KEY,
    replication_id TEXT NOT NULL REFERENCES replications(id) ON DELETE CASCADE,
    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    persona_id TEXT NOT NULL,
    status TEXT NOT NULL,            -- pending | running | done | failed
    report_md TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT
);
"""

# Columns added after the first release: (table, column, DDL).
MIGRATIONS = [
    ("personas", "tagline", "ALTER TABLE personas ADD COLUMN tagline TEXT NOT NULL DEFAULT ''"),
    ("threads", "anchor_kind", "ALTER TABLE threads ADD COLUMN anchor_kind TEXT"),
    ("run_tasks", "reply_count", "ALTER TABLE run_tasks ADD COLUMN reply_count INTEGER NOT NULL DEFAULT 0"),
    ("run_tasks", "activity", "ALTER TABLE run_tasks ADD COLUMN activity TEXT"),
    ("papers", "authors_json", "ALTER TABLE papers ADD COLUMN authors_json TEXT NOT NULL DEFAULT '[]'"),
    ("papers", "year", "ALTER TABLE papers ADD COLUMN year INTEGER"),
    ("papers", "venue", "ALTER TABLE papers ADD COLUMN venue TEXT"),
    ("papers", "abstract", "ALTER TABLE papers ADD COLUMN abstract TEXT"),
    ("papers", "keywords_json", "ALTER TABLE papers ADD COLUMN keywords_json TEXT NOT NULL DEFAULT '[]'"),
    ("papers", "field", "ALTER TABLE papers ADD COLUMN field TEXT"),
    ("papers", "doc_type", "ALTER TABLE papers ADD COLUMN doc_type TEXT"),
    ("papers", "arxiv_id", "ALTER TABLE papers ADD COLUMN arxiv_id TEXT"),
    ("papers", "doi", "ALTER TABLE papers ADD COLUMN doi TEXT"),
    ("papers", "title_source", "ALTER TABLE papers ADD COLUMN title_source TEXT NOT NULL DEFAULT 'pdf'"),
    ("papers", "metadata_status", "ALTER TABLE papers ADD COLUMN metadata_status TEXT NOT NULL DEFAULT 'none'"),
    ("papers", "metadata_error", "ALTER TABLE papers ADD COLUMN metadata_error TEXT"),
]


def connect() -> sqlite3.Connection:
    settings.ensure_dirs()
    conn = sqlite3.connect(settings.db_path, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def tx() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with tx() as conn:
        for table, column, ddl in MIGRATIONS:
            cols = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            if cols and column not in cols:
                conn.execute(ddl)
        conn.executescript(SCHEMA)
