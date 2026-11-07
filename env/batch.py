#!/usr/bin/env python3
"""Drive many researcher runs from the bench, one study per command, for an operator or an outside agent loop.

    .venv/bin/python -I env/batch.py queue                 # studies with no finished report, in order
    .venv/bin/python -I env/batch.py start S01 [--backend attached|claude-cli] [--port 8766]
         posts the run to the bench, waits for the sandbox, copies PROMPT.md into it, prints the sandbox path
    .venv/bin/python -I env/batch.py finish S01 [--tokens N] [--tool-uses K] [--seconds S]
         ends an attached run if the agent is done (STOP file), waits for the runner's final state, records the agent's
         usage in status.json, packs and verifies the hand-off bundle, prints one line
    .venv/bin/python -I env/batch.py status                # one line per study: state, minutes, tokens, conclusion
"""
import argparse, json, os, subprocess, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, RUNS, selection, finding_state, report_dir, read_json, atomic_write_json, check_id, HANDOFF

PY = os.path.join(ROOT, ".venv", "bin", "python")
FINAL = ("pdf rendered", "report written", "failed")

def api(port, path, body=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def queue():
    return [s for s in selection() if finding_state(s)["state"] not in ("pdf rendered", "handed off", "assigned", "researcher running")]

def start(sid, backend, port):
    r = api(port, "/api/run", {"id": sid, "backend": backend, "model": "opus"})
    if r.get("error"): raise SystemExit(r["error"])
    sb = os.path.join(RUNS, sid); pr = os.path.join(report_dir(sid), "PROMPT.md")
    for _ in range(60):
        if os.path.exists(pr) and os.path.isdir(os.path.join(sb, "papers", sid, "data")): break
        time.sleep(1)
    else: raise SystemExit(f"{sid}: sandbox not ready")
    time.sleep(1)
    if backend == "attached":
        with open(pr) as f, open(os.path.join(sb, "PROMPT.md"), "w") as g: g.write(f.read())
    print(json.dumps({"study": sid, "desk": r.get("slot"), "sandbox": sb}))

def finish(sid, tokens, tool_uses, seconds):
    sb_rep = os.path.join(RUNS, sid, "papers", sid, "report"); st = read_json(os.path.join(report_dir(sid), "status.json"), {}) or {}
    if st.get("state") not in FINAL and st.get("backend") == "attached":
        if not os.path.exists(os.path.join(sb_rep, "conclusion.json")):
            os.makedirs(sb_rep, exist_ok=True); open(os.path.join(sb_rep, "STOP"), "w").write("agent done\n")
    for _ in range(120):
        st = read_json(os.path.join(report_dir(sid), "status.json"), {}) or {}
        if st.get("state") in FINAL: break
        time.sleep(2)
    else: raise SystemExit(f"{sid}: runner did not finish")
    if tokens is not None:
        st["tokens_total_from_agent"] = tokens; st["agent_tool_uses"] = tool_uses; st["agent_duration_s"] = seconds
        st["note"] = f"attached run: an Opus subagent of the bench session worked in the sealed sandbox; {tokens:,} tokens over {tool_uses} tool calls; the cost is not reported by that backend"
        atomic_write_json(os.path.join(report_dir(sid), "status.json"), st)
    packed = False
    if st.get("state") == "pdf rendered":
        r = subprocess.run([PY, "-I", os.path.join(ROOT, "env", "handoff.py"), sid], capture_output=True, text=True, cwd=ROOT)
        packed = r.returncode == 0 and "of" in r.stdout and "FAILED" not in r.stdout
    c = st.get("conclusion") or {}
    print(json.dumps({"study": sid, "state": st.get("state"), "minutes": st.get("minutes"), "tokens": tokens, "holds": c.get("holds"),
                      "statistic": c.get("statistic"), "conclusion_json": bool(c), "bundle": packed}))

def status():
    tot_min = tot_tok = 0; done = failed = noconc = 0
    for sid in selection():
        f = finding_state(sid); st = f["status"]; c = st.get("conclusion") or {}
        tk = st.get("tokens_total_from_agent") or sum((st.get("tokens") or {}).values())
        if f["state"] in ("pdf rendered", "handed off"): done += 1
        elif f["state"] == "failed": failed += 1
        if st.get("finished_at") and not c: noconc += 1
        tot_min += st.get("minutes") or 0; tot_tok += tk or 0
        print(f"{sid} {f['state']:18} {st.get('minutes') or '':>5} min {tk or '':>8} tok  {c.get('holds') or '':12} {c.get('statistic') or ''}")
    print(f"finished {done}, failed {failed}, without conclusion.json {noconc}, {tot_min:.1f} min, {tot_tok:,} tokens")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["queue", "start", "finish", "status"]); ap.add_argument("study", nargs="?")
    ap.add_argument("--backend", default="attached"); ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--tokens", type=int); ap.add_argument("--tool-uses", type=int); ap.add_argument("--seconds", type=int)
    a = ap.parse_args()
    if a.cmd == "queue": print(" ".join(queue()))
    elif a.cmd == "status": status()
    elif a.cmd == "start": start(check_id(a.study), a.backend, a.port)
    elif a.cmd == "finish": finish(check_id(a.study), a.tokens, a.tool_uses, a.seconds)

if __name__ == "__main__":
    main()
