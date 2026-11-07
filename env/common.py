#!/usr/bin/env python3
"""Shared paths and readers for the lab bench (env/), target side: papers/<study>/ holds card.md, data/ and report/.
Nothing here opens a sealed file, ever: see safe_finding_file(). There is none on this side by design; the guard stays."""
import json, os, re, time, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS = os.path.join(ROOT, "papers")
RUNS = os.path.join(ROOT, "env", "runs")            # sandboxes, git-ignored
STATE = os.path.join(ROOT, "env", "state.json")     # the bench's own state (slots, runs)
HANDOFF = os.path.join(ROOT, "handoff")

SEALED = {"truth.json", "files.json", "survey.json", "reproduction.json", "RPPdataConverted.csv"}   # never read, served or copied; none exists here
REPORT_FILES = ("report.md", "report.pdf", "analysis.py", "analysis.R", "analysis.out", "log.md", "conclusion.json")
RUNNER_FILES = ("status.json", "runner.log", "runner.jsonl", "runner.stdout", "work.json", "PROMPT.md")

ID_RE = re.compile(r"^S\d{2}$")

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")

def selection():
    """The study codes: every papers/S##/ folder with a card.md, in order."""
    return sorted(d for d in os.listdir(PAPERS) if ID_RE.match(d) and os.path.exists(os.path.join(PAPERS, d, "card.md")))

def check_id(lid):
    if not ID_RE.match(lid) or lid not in selection():
        raise SystemExit(f"{lid}: not a study code with a card under papers/")
    return lid

def finding_dir(lid):
    return os.path.join(PAPERS, lid)

def report_dir(lid):
    return os.path.join(finding_dir(lid), "report")

SEALED_DIR = "sealed"                         # papers/<study>/sealed/: the trio's other two thirds; never read on this side before the verdicts

def safe_finding_file(lid, *parts):
    """A path inside papers/<study>/ that is never a sealed file, never under sealed/, and never leaves the folder."""
    base = os.path.realpath(finding_dir(lid))
    p = os.path.realpath(os.path.join(base, *parts))
    rel = os.path.relpath(p, base).split(os.sep)
    if not p.startswith(base + os.sep) or os.path.basename(p) in SEALED or any(x in SEALED for x in parts) or SEALED_DIR in rel:
        raise PermissionError(f"refused: {os.path.join(*parts)}")
    return p

def sealed_dirs():
    """Every papers/<study>/sealed/ folder, for the researcher's deny-read list."""
    return [os.path.join(PAPERS, d, SEALED_DIR) for d in sorted(os.listdir(PAPERS)) if ID_RE.match(d)]

def atomic_write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

def read_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default

def read_status(lid):
    return read_json(os.path.join(report_dir(lid), "status.json"), {}) or {}

def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False

# ---- the card, as the page shows it -------------------------------------------------------------------------------
SECTION_RE = re.compile(r"\*\*([^*]+?)\.?\*\*\s*")

def parse_card(text):
    """card.md is a list of bold-labelled paragraphs: **Claim (hypothesis).** ... **Design.** ... Returns {label: text}."""
    out, cur = {}, None
    for para in re.split(r"\n\s*\n", text.strip()):
        m = SECTION_RE.match(para)
        if m:
            cur = m.group(1).strip().rstrip(".").lower()
            out[cur] = para[m.end():].strip()
        elif cur:
            out[cur] += "\n\n" + para.strip()
    return out

def card_summary(lid):
    p = safe_finding_file(lid, "card.md")
    if not os.path.exists(p):
        return None
    text = open(p, encoding="utf-8").read()
    files_md = ""
    m = re.search(r"<!-- files:start -->(.*?)<!-- files:end -->", text, re.S)
    if m:
        files_md = m.group(1).strip(); text = text[:m.start()] + text[m.end():]
    c = parse_card(text)
    claim = next((v for k, v in c.items() if k.startswith("claim")), "")
    given = re.findall(r"`(d\d+\.[A-Za-z0-9]+)`", files_md)
    first = re.split(r"(?<=[.;:])\s", claim.strip(), 1)[0]
    first = re.sub(r"\s*\([^)]*\)", "", first).strip().rstrip(".")
    label = first if len(first) <= 72 else first[:72].rsplit(" ", 1)[0] + "…"
    return {
        "label": label, "files_given": given, "files_md": files_md,
        "hypothesis": claim,
        "design": c.get("design", ""),
        "sample": c.get("sample", ""),
        "measures": c.get("measures", c.get("measure", "")),
        "exclusions": c.get("exclusions", ""),
        "test": c.get("test", ""),
    }

def survey_summary(lid):
    """What the data folder holds, from papers/<study>/data/MANIFEST.json (neutral names, bytes, hashes)."""
    m = read_json(safe_finding_file(lid, "data", "MANIFEST.json"), {}) or {}
    files = m.get("files", {})
    fmts = sorted({n.rsplit(".", 1)[-1].lower() for n in files if "." in n})
    size = sum(int(v.get("bytes", 0)) for v in files.values())
    return {"formats": fmts, "n_files": len(files), "mb": round(size / 1e6, 1), "n_table": None}

STATES = ["no card", "data ready", "assigned", "researcher running", "report written", "pdf rendered", "handed off", "failed"]

def finding_state(lid):
    """The state of one finding, from disk only."""
    d = finding_dir(lid); rd = report_dir(lid)
    has_card = os.path.exists(os.path.join(d, "card.md"))
    has_data = os.path.isdir(os.path.join(d, "data")) and any(f for f in os.listdir(os.path.join(d, "data")) if f != "MANIFEST.json")
    st = read_status(lid)
    handed = os.path.exists(os.path.join(HANDOFF, lid, "manifest.json"))
    has_pdf = os.path.exists(os.path.join(rd, "report.pdf"))
    has_report = os.path.exists(os.path.join(rd, "report.md"))
    running = st.get("state") in ("assigned", "researcher running") and (pid_alive(st.get("pid")) or st.get("backend") == "attached" and not st.get("finished_at"))
    if running: state = st.get("state")          # a new run outranks what the last one left behind
    elif handed and has_pdf: state = "handed off"
    elif has_pdf: state = "pdf rendered"
    elif has_report: state = "report written"
    elif st.get("state") == "failed" or (st.get("finished_at") and not has_report): state = "failed"
    elif has_card and has_data: state = "data ready"
    else: state = "no card"
    files = []
    if os.path.isdir(rd):
        for f in sorted(os.listdir(rd)):
            p = os.path.join(rd, f)
            if os.path.isfile(p) and f in REPORT_FILES + ("report.html", "figure.png") or (os.path.isfile(p) and f.startswith("fig")):
                files.append({"name": f, "bytes": os.path.getsize(p), "mtime": os.path.getmtime(p)})
    # the researcher's recognition line (rule 1 of the brief) is a fact the humans on this side should see
    recognised = None
    lp = os.path.join(rd, "log.md")
    if os.path.exists(lp):
        try:
            head = open(lp, encoding="utf-8", errors="replace").read(1500).lower()
            if "recogni" in head:
                recognised = not re.search(r"(do not|don't|did not|didn't|no[t]?)\s+recogni", head)
        except OSError:
            pass
    return {"state": state, "status": st, "files": files, "has_card": has_card, "has_data": has_data, "recognised": recognised}
