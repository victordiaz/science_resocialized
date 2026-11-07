#!/usr/bin/env python3
"""Run one researcher agent for one study, sealed off from everything but its card and data.

    .venv/bin/python -I env/run_researcher.py S01 [--model opus] [--budget 20] [--attach] [--dry-run]

What it does, in order:
 1. Builds a sandbox at env/runs/<study>/ shaped like the repo: briefs/research-brief.md, score/md2pdf.py, .venv
    (symlink), papers/<study>/card.md and papers/<study>/data/ (everything in data/ is given on this side; the
    withholding happened on the operator side before export). papers/<study>/sealed/ (the paper, the outcome, the
    reproduction) never enters the sandbox: the run refuses to start if a sealed/ folder or anything named truth.json,
    files.json, survey.json or reproduction.json is reachable from it, or a symlink leads back into the repo; and the
    agent's filesystem sandbox denies reads of every papers/*/sealed/.
 2. Starts `claude -p` on an Opus model in the sandbox, with the brief as the prompt, no settings, no MCP, no web tools,
    and Claude Code's own filesystem sandbox denying reads of data/, .git/, results/, handoff/ and the user's Claude
    transcripts. It records every tool call and the tokens from the stream into report/status.json and report/runner.log.
 3. Syncs the agent's report/ into papers/<study>/report/ every few seconds, renders report.pdf with score/md2pdf.py
    when report.md exists and no PDF does, and writes the final cost and minutes.

--attach prepares the sandbox and waits for an outside agent to write the report there (for a Claude Code subagent when
the CLI is logged out); the status then says backend "attached" and carries no token counts.
--dry-run builds the sandbox, checks the seal and prints the command without starting the agent."""
import argparse, json, os, shutil, signal, subprocess, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ROOT, RUNS, PAPERS, atomic_write_json, check_id, finding_dir, report_dir, read_json, now_iso,
                    REPORT_FILES, read_status, SEALED, SEALED_DIR, sealed_dirs)

def deny_in_repo(sb):
    """Everything in this repository except the agent's own sandbox and the Python environment: every top-level entry
    but env/ and .venv, every entry of env/ but runs/, and every other study's sandbox under env/runs/. Computed at run
    time, so a folder added later (interface/, results/, demo/ ...) is denied without anyone remembering to list it."""
    out = [os.path.join(ROOT, e) for e in os.listdir(ROOT) if e not in ("env", ".venv")]
    env = os.path.join(ROOT, "env")
    out += [os.path.join(env, e) for e in os.listdir(env) if e != "runs"]
    mine = os.path.realpath(sb)
    out += [p for p in (os.path.join(RUNS, e) for e in os.listdir(RUNS)) if os.path.realpath(p) != mine]
    return sorted(out)
# the operator repository on the same laptop holds the sealed record; the agent's Bash sandbox may not read it
DENY_READ_ABS = [os.path.join(os.path.dirname(ROOT), "science-resocialized")]

def log(fp, msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    fp.write(line + "\n"); fp.flush()

def build_sandbox(lid, sb, out):
    """The researcher's work folder: the study's card and its data folder as they are (neutral names, a manifest of
    hashes). The withholding of reports, scripts and codebooks happened before the export to this repository."""
    if os.path.exists(sb):
        shutil.rmtree(sb)
    os.makedirs(os.path.join(sb, "briefs")); os.makedirs(os.path.join(sb, "score"))
    shutil.copy(os.path.join(ROOT, "briefs", "research-brief.md"), os.path.join(sb, "briefs"))
    shutil.copy(os.path.join(ROOT, "score", "md2pdf.py"), os.path.join(sb, "score"))
    os.symlink(os.path.join(ROOT, ".venv"), os.path.join(sb, ".venv"))
    fd = os.path.join(sb, "papers", lid); os.makedirs(os.path.join(fd, "report"))
    # only card.md and data/ cross: papers/<study>/sealed/ (the paper, the outcome, the reproduction) never does
    shutil.copy(os.path.join(finding_dir(lid), "card.md"), fd)
    src = os.path.join(finding_dir(lid), "data"); dst = os.path.join(fd, "data"); os.makedirs(dst)
    given = []
    for f in sorted(os.listdir(src)):
        p = os.path.join(src, f)
        if f.startswith(".") or not os.path.isfile(p) or os.path.islink(p) or f in SEALED: continue
        shutil.copy(p, os.path.join(dst, f))
        if f != "MANIFEST.json": given.append({"file": f, "bytes": os.path.getsize(p)})
    if not given:
        raise SystemExit(f"{lid}: no data files under papers/{lid}/data/")
    if out: atomic_write_json(os.path.join(out, "work.json"), {"study": lid, "given": [g["file"] for g in given], "at": now_iso()})
    return given, 0

def check_seal(sb):
    """Refuse if anything sealed or identifying is reachable inside the sandbox."""
    bad = []
    for r, dirs, files in os.walk(sb):
        for f in files + dirs:
            p = os.path.join(r, f)
            if f in SEALED or f == SEALED_DIR:
                bad.append(p)
            if os.path.islink(p):
                tgt = os.path.realpath(p)
                if tgt != os.path.realpath(os.path.join(ROOT, ".venv")) and tgt.startswith(os.path.realpath(ROOT)):
                    bad.append(f"{p} -> {tgt}")
    if bad:
        raise SystemExit("refusing to run: sealed or identifying files reachable from the sandbox:\n  " + "\n  ".join(bad))

def prompt_text(lid, brief):
    return (f"You are the researcher for study {lid}. Your working directory is a sealed copy of the project: it holds "
            f"briefs/research-brief.md (this brief), papers/{lid}/card.md, papers/{lid}/data/ (the card's last section says "
            f"what each file holds), score/md2pdf.py and .venv. Every path in the brief is relative to this directory. "
            f"Write only under papers/{lid}/report/. Do not read anything outside this directory except the Python "
            f"environment and R. There is no network. The study code is {lid}. Begin now; the brief follows.\n\n" + brief)

def claude_cmd(sb, model, budget, lid):
    deny = deny_in_repo(sb) + DENY_READ_ABS + sealed_dirs()
    deny += [os.path.expanduser(p) for p in ("~/.claude/projects", "~/.claude/sessions", "~/.claude/todos",
                                              "~/Library/Application Support/Claude/side-session-notes")]
    settings = {"sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True,
                            "filesystem": {"denyRead": deny, "allowWrite": [sb]},
                            "network": {"allowedDomains": []}},
                "includeCoAuthoredBy": False}
    return ["claude", "-p", "--model", model, "--output-format", "stream-json", "--verbose",
            "--dangerously-skip-permissions", "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands",
            "--no-session-persistence", "--disallowedTools", "WebSearch", "WebFetch", "Agent", "Task",
            "--max-budget-usd", str(budget), "--settings", json.dumps(settings)], settings

def child_env():
    keep = {"PATH", "HOME", "LANG", "LC_ALL", "TERM", "USER", "SHELL", "TMPDIR", "R_HOME"}
    env = {k: v for k, v in os.environ.items() if k in keep}
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    for k in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL"):
        if os.environ.get(k): env[k] = os.environ[k]
    return env

def sync_report(sb_rep, out):
    changed = []
    if not os.path.isdir(sb_rep): return changed
    for r, dirs, files in os.walk(sb_rep):
        dirs[:] = [d for d in dirs if d not in ("work", "__pycache__", ".ipynb_checkpoints")]
        for f in files:
            if f.startswith("."): continue
            src = os.path.join(r, f); rel = os.path.relpath(src, sb_rep); dst = os.path.join(out, rel)
            try:
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst) + 0.5 or os.path.getsize(src) != os.path.getsize(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(src, dst); changed.append(rel)
            except OSError:
                pass
    return changed

def render_pdf(out, logf):
    md = os.path.join(out, "report.md"); pdf = os.path.join(out, "report.pdf")
    if not os.path.exists(md): return False
    if os.path.exists(pdf) and os.path.getmtime(pdf) >= os.path.getmtime(md): return True
    r = subprocess.run([os.path.join(ROOT, ".venv/bin/python"), "-I", os.path.join(ROOT, "score/md2pdf.py"), md, pdf],
                       capture_output=True, text=True, timeout=180)
    log(logf, f"md2pdf: {r.stderr.strip()} {r.stdout.strip()}")
    return os.path.exists(pdf)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("study"); ap.add_argument("--model", default="opus"); ap.add_argument("--budget", type=float, default=20.0)
    ap.add_argument("--attach", action="store_true"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--replace", action="store_true")
    ap.add_argument("--timeout", type=int, default=75 * 60, help="seconds before the agent is stopped")
    a = ap.parse_args()
    lid = check_id(a.study)
    fd = finding_dir(lid); out = report_dir(lid)
    if not os.path.exists(os.path.join(fd, "card.md")): raise SystemExit(f"{lid}: no card.md yet")
    if not os.path.isdir(os.path.join(fd, "data")): raise SystemExit(f"{lid}: no data/ folder")
    st = read_status(lid)
    if st.get("state") in ("assigned", "researcher running") and st.get("pid") and st["pid"] != os.getpid():
        try: os.kill(st["pid"], 0); raise SystemExit(f"{lid}: already running (pid {st['pid']})")
        except OSError: pass
    if a.dry_run:
        # a dry run builds and checks the sandbox only; it never touches papers/<study>/report/
        sb = os.path.join(RUNS, lid) + ".dryrun"
        kept, _ = build_sandbox(lid, sb, None); check_seal(sb)
        cmd, settings = claude_cmd(sb, a.model, a.budget, lid)
        print("sandbox:", sb, f"({len(kept)} data files)"); print("cmd:", " ".join(cmd[:14]), "...")
        print("denyRead:", *settings["sandbox"]["filesystem"]["denyRead"], sep="\n  ")
        shutil.rmtree(sb); return
    if os.path.exists(os.path.join(out, "conclusion.json")) and not a.replace:
        raise SystemExit(f"{lid}: a finished report is already in papers/{lid}/report/; pass --replace to run again "
                         f"(the bench's 'Run again' does), or move the folder aside first")
    os.makedirs(out, exist_ok=True)
    for f in REPORT_FILES + ("report.html", "runner.log", "runner.jsonl"):   # a fresh run replaces the last report
        p = os.path.join(out, f)
        if os.path.exists(p): os.remove(p)
    logf = open(os.path.join(out, "runner.log"), "a")
    sb = os.path.join(RUNS, lid); sb_rep = os.path.join(sb, "papers", lid, "report")
    status = {"study": lid, "state": "assigned", "backend": "attached" if a.attach else "claude-cli", "model": a.model,
              "pid": os.getpid(), "started_at": now_iso(), "t0": time.time(), "sandbox": sb, "turns": 0, "tool_calls": 0,
              "tokens": {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0}, "cost_usd": None, "last_tool": None,
              "budget_usd": a.budget, "elapsed_s": 0}
    def save(**kw):
        status.update(kw); status["elapsed_s"] = int(time.time() - status["t0"]); atomic_write_json(os.path.join(out, "status.json"), status)
    save()
    log(logf, f"building sandbox {sb}")
    given, withheld = build_sandbox(lid, sb, out); check_seal(sb)
    log(logf, f"sandbox ok: {len(given)} data files under neutral names; seal checked")
    brief = open(os.path.join(sb, "briefs", "research-brief.md")).read()
    prompt = prompt_text(lid, brief); open(os.path.join(out, "PROMPT.md"), "w").write(prompt)
    cmd, settings = claude_cmd(sb, a.model, a.budget, lid)
    stop = {"flag": False}
    def syncer():
        while not stop["flag"]:
            ch = sync_report(sb_rep, out)
            if ch: log(logf, "report/ now has: " + ", ".join(ch))
            save(); time.sleep(3)
    th = threading.Thread(target=syncer, daemon=True); th.start()
    rc = None
    try:
        if a.attach:
            save(state="researcher running", note=f"attached: an outside agent works in {sb}; waiting for report.md and conclusion.json")
            log(logf, "attached mode: waiting for the report to appear in the sandbox")
            t0 = time.time()
            while time.time() - t0 < a.timeout:
                if os.path.exists(os.path.join(sb_rep, "conclusion.json")) and os.path.exists(os.path.join(sb_rep, "report.md")):
                    time.sleep(5); break
                if os.path.exists(os.path.join(sb_rep, "STOP")): break
                time.sleep(3)
            rc = 0
        else:
            log(logf, f"starting claude ({a.model}) in the sandbox, budget ${a.budget}")
            raw = open(os.path.join(out, "runner.jsonl"), "a")
            p = subprocess.Popen(cmd, cwd=sb, env=child_env(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, start_new_session=True)
            p.stdin.write(prompt); p.stdin.close()
            save(state="researcher running", agent_pid=p.pid)
            def killer():
                try: os.killpg(p.pid, signal.SIGTERM)
                except OSError: pass
            timer = threading.Timer(a.timeout, killer); timer.start()
            for line in p.stdout:
                raw.write(line); raw.flush()
                line = line.strip()
                if not line.startswith("{"):
                    if line: log(logf, "cli: " + line[:300])
                    continue
                try: ev = json.loads(line)
                except ValueError: continue
                t = ev.get("type")
                if t == "system" and ev.get("subtype") == "init":
                    save(model=ev.get("model", a.model), session_id=ev.get("session_id"))
                    log(logf, f"agent up: model {ev.get('model')}, tools {len(ev.get('tools', []))}")
                elif t == "assistant":
                    m = ev.get("message", {}); u = m.get("usage") or {}
                    tk = status["tokens"]
                    tk["input"] += u.get("input_tokens", 0); tk["output"] += u.get("output_tokens", 0)
                    tk["cache_read"] += u.get("cache_read_input_tokens", 0); tk["cache_create"] += u.get("cache_creation_input_tokens", 0)
                    status["turns"] += 1
                    for b in m.get("content", []):
                        if b.get("type") == "tool_use":
                            status["tool_calls"] += 1
                            inp = b.get("input", {}); name = b.get("name")
                            what = inp.get("command") or inp.get("file_path") or inp.get("pattern") or json.dumps(inp)[:120]
                            status["last_tool"] = f"{name}: {str(what)[:160]}"
                            log(logf, f"{name}: {str(what)[:200].replace(chr(10), ' ')}")
                        elif b.get("type") == "text" and b.get("text", "").strip():
                            log(logf, "says: " + b["text"].strip().replace("\n", " ")[:300])
                    save()
                elif t == "result":
                    save(cost_usd=ev.get("total_cost_usd"), duration_ms=ev.get("duration_ms"), num_turns=ev.get("num_turns"),
                         result_text=(ev.get("result") or "")[:2000], is_error=ev.get("is_error"), usage=ev.get("usage"),
                         model_usage=ev.get("modelUsage"))
                    log(logf, f"result: cost ${ev.get('total_cost_usd')}, {ev.get('num_turns')} turns, error={ev.get('is_error')}")
                    if ev.get("is_error"): log(logf, "result text: " + (ev.get("result") or "")[:500])
            rc = p.wait(); timer.cancel()
            log(logf, f"claude exited {rc}")
    finally:
        stop["flag"] = True; th.join(timeout=5)
        sync_report(sb_rep, out)
        has_report = os.path.exists(os.path.join(out, "report.md"))
        pdf = render_pdf(out, logf) if has_report else False
        concl = read_json(os.path.join(out, "conclusion.json"))
        state = "pdf rendered" if pdf else ("report written" if has_report else "failed")
        save(state=state, finished_at=now_iso(), exit_code=rc, minutes=round((time.time() - status["t0"]) / 60, 1),
             conclusion=concl if isinstance(concl, dict) else None, pid=None)
        log(logf, f"done: {state}, {status['minutes']} min, cost {status['cost_usd']}")
        print(json.dumps({k: status.get(k) for k in ("study", "state", "minutes", "cost_usd", "tokens", "turns")}))

if __name__ == "__main__":
    main()
