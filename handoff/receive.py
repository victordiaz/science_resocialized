#!/usr/bin/env python3
"""The reviewers' side of the wall: take bundles in, verify them, and check the verdicts written back.

    python3 handoff/receive.py <inbox>            # verify every bundle under <inbox> (a copy of handoff/) and list them
    python3 handoff/receive.py <inbox> --verdicts # also check every verdicts/<id>/<structure>/<reviewer>/round*.json

Standard library only, so it runs on the reviewers' machine without this repo's venv. A bundle passes when every file
named in its manifest.json is present with the same SHA-256; a receipt passes when it has the fields of
briefs/review-brief.md and odds between 0 and 1. Exit code 1 if anything fails."""
import argparse, hashlib, json, os, re, sys

REQUIRED = ("reviewer", "round", "study", "odds_holds", "reasons", "recomputed", "recognised_study", "minutes")

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()

def verify_bundle(d):
    mp = os.path.join(d, "manifest.json")
    if not os.path.exists(mp): return ["no manifest.json"]
    m = json.load(open(mp)); bad = []
    for name, info in m.get("files", {}).items():
        p = os.path.join(d, name)
        if not os.path.exists(p): bad.append(f"missing {name}")
        elif sha256(p) != info["sha256"]: bad.append(f"hash differs {name}")
    for rel, info in m.get("data_files", {}).items():
        p = os.path.join(d, "data", rel)
        if not os.path.exists(p): bad.append(f"missing data/{rel}")
        elif sha256(p) != info["sha256"]: bad.append(f"hash differs data/{rel}")
    for forbidden in ("truth.json", "survey.json", "reproduction.json", "files.json"):
        if os.path.exists(os.path.join(d, forbidden)): bad.append(f"must not be here: {forbidden}")
    return bad

def verify_receipt(p):
    try: r = json.load(open(p))
    except ValueError as e: return [f"not json: {e}"]
    bad = [f"missing {k}" for k in REQUIRED if k not in r]
    try:
        o = float(r.get("odds_holds"))
        if not 0 <= o <= 1: bad.append("odds_holds not in [0, 1]")
    except (TypeError, ValueError): bad.append("odds_holds not a number")
    if r.get("round") == 2 and not r.get("round2_change"): bad.append("round 2 without round2_change")
    parts = p.replace("\\", "/").split("/")
    if r.get("study") != parts[-4]: bad.append(f"study {r.get('study')} does not match folder {parts[-4]}")
    if r.get("reviewer") != parts[-2]: bad.append(f"reviewer {r.get('reviewer')} does not match folder {parts[-2]}")
    return bad

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inbox"); ap.add_argument("--verdicts", action="store_true")
    a = ap.parse_args(); ok = True
    bundles = sorted(d for d in os.listdir(a.inbox) if re.fullmatch(r"S\d{2}", d) and os.path.isdir(os.path.join(a.inbox, d)))
    for b in bundles:
        bad = verify_bundle(os.path.join(a.inbox, b))
        print(f"{b}: {'ok' if not bad else 'FAILED ' + '; '.join(bad)}"); ok &= not bad
    print(f"{len(bundles)} bundles")
    if a.verdicts:
        n = 0
        vd = os.path.join(a.inbox, "verdicts")
        for r, _, fs in os.walk(vd) if os.path.isdir(vd) else []:
            for f in fs:
                if f in ("round1.json", "round2.json"):
                    p = os.path.join(r, f); bad = verify_receipt(p); n += 1
                    if bad: ok = False; print(f"{os.path.relpath(p, a.inbox)}: FAILED {'; '.join(bad)}")
        print(f"{n} receipts checked")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
