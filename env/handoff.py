#!/usr/bin/env python3
"""Pack one finding's report for the reviewers' machine.

    .venv/bin/python -I env/handoff.py S01            # write handoff/S01/ and update handoff/MANIFEST.json
    .venv/bin/python -I env/handoff.py S01 --verify   # recompute every hash in the bundle and compare
    .venv/bin/python -I env/handoff.py S01 --zip      # also write handoff/S01.zip (for tailscale file cp)
    .venv/bin/python -I env/handoff.py S01 --send user@host:/path/handoff/   # rsync the bundle (works over a tailnet)
    .venv/bin/python -I env/handoff.py S01 --send tailscale:<machine>         # tailscale file cp of the zip

The bundle: report.pdf, report.md, log.md, card.md, manifest.json, and data/ (the study's data folder as the researcher
saw it; git-ignored, so git carries the report and the folder copy carries the data). Nothing in it names the paper:
the manifest has study codes, hashes, times, the researcher's model and cost."""
import argparse, json, os, re, shutil, subprocess, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, HANDOFF, RUNS, check_id, finding_dir, report_dir, read_json, now_iso, sha256, atomic_write_json, safe_finding_file

BUNDLE_VERSION = 1
RECOG_RE = re.compile(r"^\s*[*#]*\s*recogni|\bI (do not |don't )?recogni[sz]e\b", re.I)
FILES = ("report.pdf", "report.md", "log.md", "card.md")

def pack(lid):
    rd = report_dir(lid); fd = finding_dir(lid); dst = os.path.join(HANDOFF, lid)
    pdf = os.path.join(rd, "report.pdf")
    if not os.path.exists(pdf): raise SystemExit(f"{lid}: no report/report.pdf yet")
    if not os.path.exists(os.path.join(fd, "card.md")): raise SystemExit(f"{lid}: no card.md")
    os.makedirs(dst, exist_ok=True)
    files = {}
    for name in FILES:
        src = os.path.join(fd if name == "card.md" else rd, name)
        if not os.path.exists(src):
            if name in ("report.pdf", "card.md"): raise SystemExit(f"{lid}: missing {name}")
            continue
        if name == "log.md":
            # the brief makes the researcher say in one line whether it recognised the study; that line can name the
            # paper, so the bundled copy withholds it (the full log stays in papers/<study>/report/)
            text = open(src, encoding="utf-8").read()
            out_lines = [("Recognition: [withheld from the bundle; the full line is in the record]" if RECOG_RE.search(l) else l)
                         for l in text.splitlines()]
            open(os.path.join(dst, name), "w", encoding="utf-8").write("\n".join(out_lines) + "\n")
        else:
            shutil.copy2(src, os.path.join(dst, name))
        files[name] = {"sha256": sha256(os.path.join(dst, name)), "bytes": os.path.getsize(os.path.join(dst, name))}
    # the data, as the researcher saw it (the sandbox copy if it exists, else the study's data folder itself)
    sb_dl = os.path.join(RUNS, lid, "papers", lid, "data")
    if not os.path.isdir(sb_dl): sb_dl = safe_finding_file(lid, "data")
    ddst = os.path.join(dst, "data")
    data_files = {}
    if os.path.isdir(sb_dl):
        if os.path.isdir(ddst): shutil.rmtree(ddst)
        shutil.copytree(sb_dl, ddst)
        for r, _, fs in os.walk(ddst):
            for f in fs:
                p = os.path.join(r, f); rel = os.path.relpath(p, ddst)
                data_files[rel] = {"sha256": sha256(p), "bytes": os.path.getsize(p)}
    st = read_json(os.path.join(rd, "status.json"), {}) or {}
    concl = read_json(os.path.join(rd, "conclusion.json"), None)
    manifest = {
        "bundle_version": BUNDLE_VERSION, "study": lid, "created_at": now_iso(),
        "files": files, "data_files": data_files, "data_included": bool(data_files),
        "researcher": {k: st.get(k) for k in ("model", "backend", "cost_usd", "tokens", "turns", "tool_calls", "minutes", "started_at", "finished_at")},
        "conclusion_stated": (concl or {}).get("holds") if isinstance(concl, dict) else None,
        "reviewers_write_back": f"verdicts/{lid}/<structure>/<reviewer>/round1.json and round2.json (see handoff/README.md)",
    }
    atomic_write_json(os.path.join(dst, "manifest.json"), manifest)
    top = read_json(os.path.join(HANDOFF, "MANIFEST.json"), {"bundles": []}) or {"bundles": []}
    top["bundles"] = [b for b in top.get("bundles", []) if b.get("study") != lid]
    top["bundles"].append({"study": lid, "created_at": manifest["created_at"], "report_pdf_sha256": files["report.pdf"]["sha256"],
                           "model": st.get("model"), "cost_usd": st.get("cost_usd"), "minutes": st.get("minutes")})
    top["bundles"].sort(key=lambda b: b["study"])
    top["updated_at"] = manifest["created_at"]; top["bundle_version"] = BUNDLE_VERSION
    atomic_write_json(os.path.join(HANDOFF, "MANIFEST.json"), top)
    return manifest

def verify(lid):
    dst = os.path.join(HANDOFF, lid); man = read_json(os.path.join(dst, "manifest.json"), None)
    if not man: raise SystemExit(f"{lid}: no bundle")
    bad = []
    for name, info in man["files"].items():
        p = os.path.join(dst, name)
        if not os.path.exists(p) or sha256(p) != info["sha256"]: bad.append(name)
    for rel, info in man.get("data_files", {}).items():
        p = os.path.join(dst, "data", rel)
        if not os.path.exists(p) or sha256(p) != info["sha256"]: bad.append("data/" + rel)
    n = len(man["files"]) + len(man.get("data_files", {}))
    print(f"{lid}: {n - len(bad)} of {n} hashes verify" + (f"; FAILED: {bad}" if bad else ""))
    return not bad

def make_zip(lid):
    dst = os.path.join(HANDOFF, lid); z = os.path.join(HANDOFF, f"{lid}.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for r, _, fs in os.walk(dst):
            for f in fs: zf.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), HANDOFF))
    print("zip:", z, os.path.getsize(z), "bytes"); return z

def send(lid, target):
    """Move one bundle over the wall. target: user@host:/path (rsync over ssh, works on a tailnet), /local/path (rsync),
    or tailscale:<machine> (tailscale file cp of a zip). Writes handoff/<id>/sent.json with the target and the time."""
    if target.startswith("tailscale:"):
        z = make_zip(lid)
        subprocess.run(["tailscale", "file", "cp", z, target.split(":", 1)[1] + ":"], check=True)
    else:
        subprocess.run(["rsync", "-a", "--delete", os.path.join(HANDOFF, lid) + "/", target.rstrip("/") + f"/{lid}/"], check=True)
        subprocess.run(["rsync", "-a", os.path.join(HANDOFF, "MANIFEST.json"), os.path.join(HANDOFF, "README.md"), os.path.join(HANDOFF, "receive.py"), target.rstrip("/") + "/"], check=True)
    atomic_write_json(os.path.join(HANDOFF, lid, "sent.json"), {"study": lid, "target": target, "at": now_iso(),
                      "report_pdf_sha256": (read_json(os.path.join(HANDOFF, lid, "manifest.json"), {}) or {}).get("files", {}).get("report.pdf", {}).get("sha256")})
    print("sent", lid, "to", target)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("study")
    ap.add_argument("--verify", action="store_true"); ap.add_argument("--zip", action="store_true"); ap.add_argument("--send")
    a = ap.parse_args(); lid = check_id(a.study)
    if a.verify: sys.exit(0 if verify(lid) else 1)
    m = pack(lid); verify(lid)
    print(json.dumps({"study": lid, "files": {k: v["sha256"][:16] for k, v in m["files"].items()}, "data_files": len(m["data_files"])}))
    if a.zip: make_zip(lid)
    if a.send: send(lid, a.send)

if __name__ == "__main__":
    main()
