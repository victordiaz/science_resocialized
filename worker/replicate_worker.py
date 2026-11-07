#!/usr/bin/env python3
"""Review Room replication worker.

Claims blind replication jobs from a Review Room server, runs Claude Code headless in a
fresh folder per job, streams progress back, and uploads the report and files.

Standalone: Python 3.10+ standard library only. Copy this file to any machine with
Python and Claude Code installed and run:

    ANTHROPIC_API_KEY=sk-... python3 replicate_worker.py \\
        --url http://<review-room-host>:8000 --token <worker token> --workdir ~/replications

The worker token is in the server's data/worker_token file (or set WORKER_TOKEN there).
By default Claude Code runs with --bare (no CLAUDE.md, hooks or plugins from this
machine), which needs ANTHROPIC_API_KEY. Use --no-bare to use the machine's normal login.

Note: the replicator runs code with permissions bypassed, inside its job folder. Run the
worker on a machine (or account, or container) where that is acceptable.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ALLOWED_TOOLS = "Bash,Read,Edit,Write,Glob,Grep"  # no WebSearch / WebFetch
UPLOAD_SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__", ".cache", "data", "datasets", "wandb", ".ipynb_checkpoints"}
UPLOAD_EXTS = {
    ".md", ".txt", ".py", ".ipynb", ".json", ".jsonl", ".csv", ".tsv", ".yaml", ".yml", ".toml", ".cfg", ".ini",
    ".sh", ".log", ".r", ".jl", ".c", ".cpp", ".h", ".rs", ".go", ".js", ".ts",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf",
}
MAX_FILE = 2 * 1024 * 1024
MAX_TOTAL = 20 * 1024 * 1024


def log(msg: str) -> None:
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


class Api:
    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.token = token

    def post(self, path: str, body: dict, timeout: float = 60) -> dict:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            self.url + path, data=data, method="POST",
            headers={"Content-Type": "application/json", "X-Worker-Token": self.token},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read() or b"{}")


# ---------------------------------------------------------------- stream-json -> short events

def summarize(obj: dict) -> list[dict]:
    """Turn one Claude Code stream-json message into short progress events."""
    t = obj.get("type")
    out: list[dict] = []
    if t == "assistant":
        for block in (obj.get("message") or {}).get("content") or []:
            if block.get("type") == "text" and block.get("text", "").strip():
                out.append({"kind": "text", "text": block["text"].strip()})
            elif block.get("type") == "tool_use":
                inp = block.get("input") or {}
                detail = inp.get("command") or inp.get("file_path") or inp.get("pattern") or inp.get("description") or ""
                out.append({"kind": "tool", "text": f"{block.get('name')}: {str(detail)[:300]}"})
    elif t == "user":
        for block in (obj.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error"):
                content = block.get("content")
                text = content if isinstance(content, str) else json.dumps(content)[:300]
                out.append({"kind": "stderr", "text": f"tool error: {text[:300]}"})
    elif t == "result":
        cost = obj.get("total_cost_usd")
        dur = obj.get("duration_ms")
        bits = [obj.get("subtype") or "finished"]
        if cost is not None:
            bits.append(f"${cost:.2f}")
        if dur:
            bits.append(f"{dur / 60000:.1f} min")
        if obj.get("num_turns"):
            bits.append(f"{obj['num_turns']} turns")
        out.append({"kind": "result", "text": "Claude Code " + ", ".join(bits)})
    return out


# ---------------------------------------------------------------- one job

def collect_files(folder: Path) -> list[dict]:
    files, total = [], 0
    candidates = []
    for p in folder.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(folder)
        if any(part in UPLOAD_SKIP_DIRS or part.startswith(".") for part in rel.parts[:-1]):
            continue
        if p.suffix.lower() not in UPLOAD_EXTS:
            continue
        size = p.stat().st_size
        if size > MAX_FILE:
            continue
        # REPORT.md and outputs first, then code.
        rank = 0 if rel.as_posix() == "REPORT.md" else 1 if rel.parts[0] == "outputs" else 2
        candidates.append((rank, rel.as_posix(), p, size))
    for _rank, rel, p, size in sorted(candidates):
        if total + size > MAX_TOTAL:
            continue
        total += size
        files.append({"path": rel, "content_b64": base64.b64encode(p.read_bytes()).decode()})
    return files


def run_job(api: Api, job: dict, args) -> None:
    rep_id = job["replication_id"]
    folder = Path(args.workdir).expanduser().resolve() / rep_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "TASK.md").write_text(job["task_md"])
    (folder / "outputs").mkdir(exist_ok=True)
    log(f"job {rep_id}: running in {folder}")

    cmd = [
        args.claude, "-p", job["prompt"],
        "--output-format", "stream-json", "--verbose",
        "--tools", ALLOWED_TOOLS,
        "--permission-mode", "bypassPermissions",
        "--append-system-prompt", job["system_append"],
        "--max-budget-usd", str(job["budget_usd"]),
        "--no-session-persistence",
    ]
    if args.bare:
        cmd.append("--bare")
    if args.model:
        cmd += ["--model", args.model]

    pending: list[dict] = [{"kind": "info", "text": f"Started Claude Code in {folder}"}]
    lock = threading.Lock()
    state = {"cost": None, "result_error": None, "cancel": False}

    proc = subprocess.Popen(
        cmd, cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        start_new_session=True,  # so we can stop its whole process group
    )

    def read_stdout():
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                evs = [{"kind": "text", "text": line[:1000]}]
            else:
                evs = summarize(obj)
                if obj.get("type") == "result":
                    state["cost"] = obj.get("total_cost_usd")
                    if obj.get("is_error"):
                        state["result_error"] = obj.get("subtype") or "error"
            with lock:
                pending.extend(evs)

    def read_stderr():
        for line in proc.stderr:
            if line.strip():
                with lock:
                    pending.append({"kind": "stderr", "text": line.strip()[:1000]})

    threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()

    deadline = time.time() + job["timeout_min"] * 60
    timed_out = False
    while True:
        done = proc.poll() is not None
        with lock:
            batch, pending[:] = pending[:], []
        try:
            resp = api.post(f"/api/worker/replications/{rep_id}/events", {"events": batch, "workdir": str(folder)})
            if resp.get("cancel"):
                state["cancel"] = True
        except Exception as e:  # keep running even if the server blips
            log(f"job {rep_id}: could not send events: {e}")
            with lock:
                pending[:0] = batch
        if done:
            break
        if state["cancel"] or time.time() > deadline:
            timed_out = not state["cancel"]
            log(f"job {rep_id}: {'cancelled' if state['cancel'] else 'time limit reached'}, stopping Claude Code")
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(30)
            except Exception:
                os.killpg(proc.pid, signal.SIGKILL)
            continue
        time.sleep(args.flush_seconds)

    time.sleep(0.5)  # let readers drain
    with lock:
        tail = pending[:]
    if tail:
        try:
            api.post(f"/api/worker/replications/{rep_id}/events", {"events": tail})
        except Exception:
            pass

    report = folder / "REPORT.md"
    if state["cancel"]:
        status, error = "cancelled", None
    elif timed_out:
        status, error = ("done", "Stopped at the time limit; REPORT.md may be partial.") if report.exists() else ("failed", "Stopped at the time limit before writing REPORT.md.")
    elif report.exists():
        status, error = "done", None if proc.returncode == 0 else f"Claude Code exited with code {proc.returncode} ({state['result_error']})"
    else:
        status, error = "failed", f"No REPORT.md written (Claude Code exit code {proc.returncode}, {state['result_error'] or 'no result'})."

    body = {
        "status": status,
        "report_md": report.read_text(errors="replace") if report.exists() else None,
        "cost_usd": state["cost"],
        "error": error,
        "files": collect_files(folder),
    }
    for attempt in range(5):
        try:
            api.post(f"/api/worker/replications/{rep_id}/complete", body, timeout=300)
            log(f"job {rep_id}: {status}, uploaded {len(body['files'])} files")
            return
        except Exception as e:
            log(f"job {rep_id}: upload failed ({e}), retrying")
            time.sleep(5 * (attempt + 1))
    log(f"job {rep_id}: could not upload results; they remain in {folder}")


# ---------------------------------------------------------------- main loop

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("REVIEW_ROOM_URL", "http://127.0.0.1:8000"))
    ap.add_argument("--token", default=os.environ.get("WORKER_TOKEN"))
    ap.add_argument("--workdir", default=os.environ.get("REPLICATION_WORKDIR", "~/review-room-replications"))
    ap.add_argument("--name", default=socket.gethostname())
    ap.add_argument("--claude", default=shutil.which("claude") or "claude", help="path to the claude CLI")
    ap.add_argument("--model", default=os.environ.get("REPLICATOR_MODEL"), help="model for Claude Code (default: its own)")
    ap.add_argument("--no-bare", dest="bare", action="store_false", help="don't pass --bare (use this machine's login and settings)")
    ap.add_argument("--poll-seconds", type=float, default=5)
    ap.add_argument("--flush-seconds", type=float, default=2)
    ap.add_argument("--once", action="store_true", help="run at most one job, then exit")
    args = ap.parse_args()

    if not args.token:
        print("missing --token (or WORKER_TOKEN)", file=sys.stderr)
        return 2
    if args.bare and not os.environ.get("ANTHROPIC_API_KEY"):
        log("warning: --bare needs ANTHROPIC_API_KEY; Claude Code will fail to authenticate (or use --no-bare)")
    api = Api(args.url, args.token)
    log(f"worker {args.name} polling {args.url}, workdir {Path(args.workdir).expanduser()}")
    while True:
        try:
            job = api.post("/api/worker/claim", {"worker": args.name}).get("job")
        except urllib.error.HTTPError as e:
            log(f"claim failed: HTTP {e.code} {e.read()[:200]!r}")
            if e.code == 401:
                return 1
            job = None
        except Exception as e:
            log(f"server not reachable: {e}")
            job = None
        if job:
            try:
                run_job(api, job, args)
            except Exception as e:  # report and keep serving
                log(f"job {job['replication_id']} crashed: {e}")
                try:
                    api.post(f"/api/worker/replications/{job['replication_id']}/complete",
                             {"status": "failed", "error": f"Worker error: {e}", "files": []})
                except Exception:
                    pass
            if args.once:
                return 0
        else:
            if args.once:
                return 0
            time.sleep(args.poll_seconds)


if __name__ == "__main__":
    sys.exit(main())
