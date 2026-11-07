#!/usr/bin/env python3
"""The lab bench server, target side: one page over the thirty studies, the researcher desks, and the hand-off.

    .venv/bin/python -I env/server.py [--port 8765]

Serves env/bench.html and a small JSON API. State is on disk: env/state.json (desks and runs) and each study's
papers/<study>/report/status.json (written by run_researcher.py). Every study path goes through
common.safe_finding_file, which refuses sealed file names. The one exception is common.read_sealed, reached only through
common.reveal once the panel's receipt for that study is under handoff/<run>/; only two verdict words leave it."""
import argparse, json, os, re, subprocess, sys, threading, time, urllib.parse, signal
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ROOT, STATE, HANDOFF, selection, card_summary, survey_summary, finding_state, finding_dir, report_dir,
                    safe_finding_file, atomic_write_json, read_json, now_iso, pid_alive, REPORT_FILES, RUNNER_FILES, ID_RE,
                    HANDLES, run_info, run_dir, receipt_for, receipt_path, receipt_verdict, review_for, reveal, NO_VERDICTS)

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ROOT, ".venv", "bin", "python")
LOCK = threading.Lock()
TAIL_OK = set(REPORT_FILES) | {"runner.log", "status.json", "work.json", "report.html", "PROMPT.md"}
_cli = {"checked_at": 0, "logged_in": None, "detail": ""}
REVIEW_CALLS = ("agree", "disagree", "hold")
_reveal_cache = {}   # (run, study) -> (key, result): the sealed record is read once per receipt and conclusion, not per poll

def handles():
    h = read_json(HANDLES, {}) or {}
    return h if isinstance(h, dict) else {}

def mtime(p):
    try: return os.path.getmtime(p)
    except OSError: return None

def reveal_cached(lid, alias):
    """reveal() with a cache keyed on the receipt files and the researcher's conclusion.json, so the page's poll does
    not reopen the sealed record every 2.5 s; a new receipt or a new conclusion reads it again."""
    key = (mtime(receipt_path(lid, alias)), mtime(safe_finding_file(lid, "report", "conclusion.json")))
    hit = _reveal_cache.get((alias, lid))
    if hit and hit[0] == key: return hit[1]
    res = reveal(lid, alias) if key[0] else {"allowed": False, "verdicts": dict(NO_VERDICTS), "panel": None}
    _reveal_cache[(alias, lid)] = (key, res)
    return res

def state_load():
    s = read_json(STATE, None) or {}
    s.setdefault("slots", 3); s.setdefault("assignments", {}); s.setdefault("runs", {})
    return s

def state_save(s):
    s["updated_at"] = now_iso(); atomic_write_json(STATE, s)

def cli_status(force=False):
    if force or time.time() - _cli["checked_at"] > 120:
        try:
            r = subprocess.run(["claude", "auth", "status"], capture_output=True, text=True, timeout=20)
            d = json.loads(r.stdout.strip() or "{}")
            _cli.update(logged_in=bool(d.get("loggedIn")), detail=d.get("authMethod", ""))
        except Exception as e:
            _cli.update(logged_in=None, detail=str(e)[:120])
        _cli["checked_at"] = time.time()
    return {k: _cli[k] for k in ("logged_in", "detail")}

def one_finding(lid, cache, run=None, hn=None):
    cp = safe_finding_file(lid, "card.md"); mt = os.path.getmtime(cp) if os.path.exists(cp) else 0
    if lid not in cache or cache[lid].get("mtime") != mt:
        cache[lid] = {"card": card_summary(lid), "survey": survey_summary(lid), "mtime": mt, "reword": None}
    f = finding_state(lid)
    hand = read_json(os.path.join(HANDOFF, lid, "manifest.json"), None)
    sent = read_json(os.path.join(HANDOFF, lid, "sent.json"), None)
    st = dict(f["status"])
    if st.get("t0") and not st.get("finished_at"):
        st["elapsed_s"] = int(time.time() - st["t0"])
    run = run or run_info(); alias = run["alias"]; hn = hn if hn is not None else handles()
    card = cache[lid]["card"] or {}
    receipt = receipt_for(lid, alias)
    rv = reveal_cached(lid, alias)
    pkg_zip = os.path.join(run_dir(alias), lid + ".zip")
    package = None
    if os.path.exists(pkg_zip):
        package = {"path": os.path.relpath(pkg_zip, ROOT), "run": alias, "study": lid, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(os.path.getmtime(pkg_zip))),
                   "sha256": (hand or {}).get("files", {}).get("report.pdf", {}).get("sha256") if hand else None}
    return {"id": lid, "code": lid, "handle": hn.get(lid) or card.get("label") or lid,
            "review": review_for(lid, alias), "verdicts": rv["verdicts"] if rv.get("allowed") else dict(NO_VERDICTS),
            "package": package, "card": cache[lid]["card"], "survey": cache[lid]["survey"], "reword": cache[lid].get("reword"), "state": f["state"], "status": st, "recognised": f.get("recognised"),
            "files": f["files"],
            "handoff": {"at": hand.get("created_at"), "sha256": (hand.get("files", {}).get("report.pdf") or {}).get("sha256"),
                        "sent": sent,
                        "receipt": {"at": receipt.get("at"), "received_at": receipt.get("received_at"), "by": receipt.get("by"),
                                    "sha256_matches": receipt.get("sha256_matches"),
                                    "verdict": ({k: receipt_verdict(receipt).get(k) for k in ("odds_holds", "holds", "reviewers", "rounds")}
                                                if receipt_verdict(receipt) else None)} if receipt else None}
                        if hand else None}

CARD_CACHE = {}

def full_state():
    s = state_load(); run = run_info(s); hn = handles()
    findings = [one_finding(lid, CARD_CACHE, run, hn) for lid in selection()]
    counts = {}
    for f in findings: counts[f["state"]] = counts.get(f["state"], 0) + 1
    totals = {"mb": round(sum(f["survey"]["mb"] for f in findings), 1),
              "cost_usd": round(sum((f["status"].get("cost_usd") or 0) for f in findings), 3),
              "minutes": round(sum((f["status"].get("minutes") or 0) for f in findings), 1),
              "pdfs": sum(1 for f in findings if f["state"] in ("pdf rendered", "handed off")),
              "handed": sum(1 for f in findings if f["state"] == "handed off")}
    # a desk whose run has ended keeps its finding until cleared or replaced
    return {"time": now_iso(), "run": run, "admin": s.get("admin") is True, "slots": s["slots"], "assignments": s["assignments"], "cli": cli_status(), "transport": s.get("transport"),
            "findings": findings, "counts": counts, "totals": totals}

def start_run(lid, model, slot, backend="claude-cli", replace=False):
    with LOCK:
        s = state_load()
        f = finding_state(lid)
        if not f["has_card"]: return {"error": f"{lid}: no card.md yet"}, 400
        if f["state"] in ("assigned", "researcher running"): return {"error": f"{lid}: already running"}, 409
        for k, v in list(s["assignments"].items()):
            if v == lid: del s["assignments"][k]
        if slot is None:
            busy = set(s["assignments"].keys())
            for i in range(1, s["slots"] + 1):
                if str(i) not in busy: slot = str(i); break
            if slot is None:
                for i in range(1, s["slots"] + 1):   # reuse a desk whose run has ended
                    st = finding_state(s["assignments"].get(str(i), "")).get("state") if s["assignments"].get(str(i)) else None
                    if st not in ("assigned", "researcher running"): slot = str(i); break
            if slot is None: return {"error": "every desk is busy"}, 409
        os.makedirs(report_dir(lid), exist_ok=True)
        outp = open(os.path.join(report_dir(lid), "runner.stdout"), "ab")
        cmd = [PY, "-I", os.path.join(HERE, "run_researcher.py"), lid, "--model", model] + (["--attach"] if backend == "attached" else []) + (["--replace"] if replace else [])
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=outp, stderr=subprocess.STDOUT, start_new_session=True)
        s["assignments"][str(slot)] = lid
        s["runs"][lid] = {"pid": p.pid, "started_at": now_iso(), "model": model, "slot": str(slot), "backend": backend}
        state_save(s)
        return {"ok": True, "slot": slot, "pid": p.pid}, 200

def stop_run(lid):
    st = read_json(os.path.join(report_dir(lid), "status.json"), {}) or {}
    s = state_load(); pid = (s["runs"].get(lid) or {}).get("pid") or st.get("pid")
    killed = []
    for p in (st.get("agent_pid"), pid):
        if p and pid_alive(p):
            try: os.killpg(int(p), signal.SIGTERM); killed.append(p)
            except OSError:
                try: os.kill(int(p), signal.SIGTERM); killed.append(p)
                except OSError: pass
    if st and st.get("state") in ("assigned", "researcher running"):
        st.update(state="failed", finished_at=now_iso(), note="stopped from the bench", pid=None)
        atomic_write_json(os.path.join(report_dir(lid), "status.json"), st)
    return {"ok": True, "killed": killed}

def clear_slot(slot):
    with LOCK:
        s = state_load(); lid = s["assignments"].pop(str(slot), None); state_save(s)
    return {"ok": True, "cleared": lid}

def run_send(lid):
    s = state_load(); target = s.get("transport")
    if not target: return {"error": "no transport target set (the pill in the header)"}, 400
    r = subprocess.run([PY, "-I", os.path.join(HERE, "handoff.py"), lid, "--send", target], capture_output=True, text=True, timeout=600, cwd=ROOT)
    return {"ok": r.returncode == 0, "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]}, (200 if r.returncode == 0 else 500)

def record_review(body):
    """The admin's manual review of one study's verdicts, this side only: handoff/<run>/reviews/<study>.json and one line
    in handoff/<run>/reviews/LOG.md. It records what the admin saw; it never changes a verdict."""
    study = str(body.get("study") or ""); call = str(body.get("call") or "")
    if not ID_RE.match(study) or study not in selection(): return {"error": "study must be S## with a card"}, 400
    if call not in REVIEW_CALLS: return {"error": "call must be agree, disagree or hold"}, 400
    note = " ".join(str(body.get("note") or "").split())[:500]
    alias = run_info()["alias"]; receipt = receipt_for(study, alias)
    v = receipt_verdict(receipt)
    rec = {"at": now_iso(), "by": "vlad", "run": alias, "study": study,
           "verdict_seen": {"odds_holds": v.get("odds_holds"), "holds": v.get("holds"), "receipt_at": receipt.get("at")} if v else None,
           "call": call, "note": note}
    rdir = os.path.join(run_dir(alias), "reviews")
    with LOCK:
        atomic_write_json(os.path.join(rdir, study + ".json"), rec)
        with open(os.path.join(rdir, "LOG.md"), "a", encoding="utf-8") as lg:
            lg.write(f"- {rec['at']} {study} {call}: {note}\n")
    return rec, 200

def run_handoff(lid):
    r = subprocess.run([PY, "-I", os.path.join(HERE, "handoff.py"), lid], capture_output=True, text=True, timeout=300, cwd=ROOT)
    man = read_json(os.path.join(HANDOFF, lid, "manifest.json"), None)
    return {"ok": r.returncode == 0, "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:], "manifest": man}, (200 if r.returncode == 0 else 500)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)
    def send_file(self, path, ctype):
        with open(path, "rb") as f: b = f.read()
        self.send_response(200); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query); path = u.path
        try:
            if path in ("/", "/index.html"): return self.send_file(os.path.join(HERE, "bench.html"), "text/html; charset=utf-8")
            if path == "/api/state": return self.send_json(full_state())
            if path == "/api/cli": return self.send_json(cli_status(force=True))
            lid = (q.get("id") or [""])[0]
            if path == "/api/reveal":
                if not ID_RE.match(lid) or lid not in selection(): return self.send_json({"error": "bad id"}, 400)
                return self.send_json(reveal_cached(lid, run_info()["alias"]))
            if path == "/api/tail":
                name = (q.get("name") or ["log.md"])[0]; n = int((q.get("n") or ["6000"])[0])
                if not ID_RE.match(lid) or name not in TAIL_OK: return self.send_json({"error": "refused"}, 403)
                p = safe_finding_file(lid, "report", name)
                if not os.path.exists(p): return self.send_json({"name": name, "text": "", "bytes": 0})
                with open(p, "rb") as f:
                    size = os.path.getsize(p); f.seek(max(0, size - n)); text = f.read().decode("utf-8", "replace")
                return self.send_json({"name": name, "text": text, "bytes": size, "truncated": size > n})
            if path == "/api/card":
                if not ID_RE.match(lid): return self.send_json({"error": "bad id"}, 400)
                return self.send_json({"text": open(safe_finding_file(lid, "card.md"), encoding="utf-8").read()})
            if path.startswith("/report/"):
                parts = path.split("/")
                if len(parts) != 4: return self.send_json({"error": "refused"}, 403)
                _, _, lid, name = parts
                is_fig = re.fullmatch(r"fig[\w-]*\.(png|svg|jpg|jpeg)", name) is not None
                if not ID_RE.match(lid) or not (name in TAIL_OK or is_fig): return self.send_json({"error": "refused"}, 403)
                p = safe_finding_file(lid, "report", name)
                if not os.path.exists(p): return self.send_json({"error": "not yet"}, 404)
                ctype = {"pdf": "application/pdf", "html": "text/html; charset=utf-8", "json": "application/json", "png": "image/png",
                         "svg": "image/svg+xml", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(name.rsplit(".", 1)[-1], "text/plain; charset=utf-8")
                return self.send_file(p, ctype)
            self.send_json({"error": "not found"}, 404)
        except PermissionError as e:
            self.send_json({"error": str(e)}, 403)
        except Exception as e:
            self.send_json({"error": repr(e)[:300]}, 500)
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); body = json.loads(self.rfile.read(n) or b"{}")
        lid = body.get("id", "")
        try:
            if self.path in ("/api/run", "/api/stop", "/api/handoff") and not ID_RE.match(lid): return self.send_json({"error": "bad id"}, 400)
            if self.path == "/api/run": obj, code = start_run(lid, body.get("model") or "opus", body.get("slot"), body.get("backend") or "claude-cli", bool(body.get("replace"))); return self.send_json(obj, code)
            if self.path == "/api/stop": return self.send_json(stop_run(lid))
            if self.path == "/api/handoff": obj, code = run_handoff(lid); return self.send_json(obj, code)
            if self.path == "/api/send":
                if not ID_RE.match(lid): return self.send_json({"error": "bad id"}, 400)
                obj, code = run_send(lid); return self.send_json(obj, code)
            if self.path == "/api/transport":
                t = str(body.get("target") or "").strip()
                if t and not re.fullmatch(r"(tailscale:[\w.-]+|[\w.-]+@[\w.-]+:[\w./~ -]+|/[\w./~ -]+)", t): return self.send_json({"error": "target must be tailscale:<machine>, user@host:/path or /local/path"}, 400)
                with LOCK:
                    s = state_load(); s["transport"] = t or None; state_save(s)
                return self.send_json({"ok": True, "transport": s["transport"]})
            if self.path == "/api/clear": return self.send_json(clear_slot(body.get("slot")))
            if self.path == "/api/review": obj, code = record_review(body); return self.send_json(obj, code)
            if self.path == "/api/slots":
                with LOCK:
                    s = state_load(); s["slots"] = max(1, min(8, int(body.get("slots", 3)))); state_save(s)
                return self.send_json({"ok": True, "slots": s["slots"]})
            self.send_json({"error": "not found"}, 404)
        except Exception as e:
            self.send_json({"error": repr(e)[:300]}, 500)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765); ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    state_save(state_load())
    srv = ThreadingHTTPServer((a.host, a.port), H)
    print(f"lab bench: http://{a.host}:{a.port}/  (state: env/state.json; studies: papers/S##/report/status.json)")
    try: srv.serve_forever()
    except KeyboardInterrupt: pass

if __name__ == "__main__":
    main()
