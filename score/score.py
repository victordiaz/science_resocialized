#!/usr/bin/env python3
"""Score the target repository against its sealed records. Run on the operator's side, or on the reviewers' machine
once the reveal is allowed. It is the only script that opens papers/S##/sealed/truth.json.

Reads, per study papers/S##/:
  sealed/truth.json          the outcome on record (replicate_r yes/no) and our verified reproduction
  report/conclusion.json     the researcher's conclusion: holds yes | no | cannot tell
and the reviewers' receipts, wherever the hand-off contract put them:
  verdicts/<study>/<structure>/<reviewer>/round1.json, round2.json   (or handoff/verdicts/...)
Writes results/table.md and results/table.json with two tables: the researchers against the record, and each
review structure against "the conclusion holds" (the researcher agrees with the record and with the reproduction).
"""
import json, glob, os, math, statistics
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'results')

def load(p):
    try: return json.load(open(p))
    except Exception: return None

def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'), float('nan'))
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((c-h)/d, (c+h)/d)
def logit(p): p = min(max(p, 1e-4), 1-1e-4); return math.log(p/(1-p))
def inv(x): return 1/(1+math.exp(-x))

def final_odds(rdir):
    r2 = load(os.path.join(rdir, 'round2.json')) or load(os.path.join(rdir, 'out', 'round2.json'))
    r1 = load(os.path.join(rdir, 'round1.json')) or load(os.path.join(rdir, 'out', 'round1.json'))
    r = r2 or r1
    if not r or 'odds_holds' not in r: return None, r1, r2
    return float(r['odds_holds']), r1, r2

def main():
    studies = {}
    for sdir in sorted(glob.glob(os.path.join(ROOT, 'papers', 'S*'))):
        code = os.path.basename(sdir)
        truth = load(os.path.join(sdir, 'sealed', 'truth.json')); concl = load(os.path.join(sdir, 'report', 'conclusion.json'))
        if not truth: continue
        published_yes = str(truth.get('replicate_r', '')).strip().lower() == 'yes'
        researcher = str((concl or {}).get('holds', '')).strip().lower() or None
        reproduced = bool(truth.get('reproduced'))
        agrees = (researcher == 'yes') == published_yes if researcher in ('yes', 'no') else None
        studies[code] = {'published_yes': published_yes, 'researcher': researcher, 'agrees_with_record': agrees, 'reproduced': reproduced,
                         'holds': bool(agrees) if agrees is not None else None, 'recognised': truth.get('recognised_by_probe'), 'planted': truth.get('planted')}
    # table 1: researchers against the record
    done = {c: s for c, s in studies.items() if s['researcher']}
    concl_yes = sum(1 for s in done.values() if s['researcher'] == 'yes'); concl_no = sum(1 for s in done.values() if s['researcher'] == 'no')
    cannot = sum(1 for s in done.values() if s['researcher'] not in ('yes', 'no'))
    agree = sum(1 for s in done.values() if s['agrees_with_record']); n_judged = sum(1 for s in done.values() if s['agrees_with_record'] is not None)
    base_yes = sum(1 for s in studies.values() if s['published_yes'])
    lo, hi = wilson(agree, n_judged)
    t1 = {'studies': len(studies), 'reports': len(done), 'researcher_yes': concl_yes, 'researcher_no': concl_no, 'cannot_tell': cannot,
          'agree_with_record': agree, 'of': n_judged, 'accuracy': agree / n_judged if n_judged else float('nan'), 'ci95': [lo, hi],
          'record_held_up': base_yes, 'base_rate_always_no': (len(studies) - base_yes) / len(studies) if studies else float('nan')}
    # table 2: review structures
    rows = []
    for vroot in (os.path.join(ROOT, 'verdicts'), os.path.join(ROOT, 'handoff', 'verdicts')):
        for sdir in sorted(glob.glob(os.path.join(vroot, 'S*'))):
            code = os.path.basename(sdir); st = studies.get(code)
            if not st or st['holds'] is None: continue
            for stdir in sorted(glob.glob(os.path.join(sdir, '*'))):
                if not os.path.isdir(stdir): continue
                structure = os.path.basename(stdir)
                odds = [o for o, _, _ in (final_odds(r) for r in sorted(glob.glob(os.path.join(stdir, 'R*')))) if o is not None]
                if not odds: continue
                rows.append({'structure': structure, 'study': code, 'n_reviewers': len(odds), 'mean': statistics.mean(odds),
                             'median': statistics.median(odds), 'logpool': inv(statistics.mean(logit(o) for o in odds)),
                             'holds': st['holds'], 'recognised': st['recognised']})
    def agg(sub):
        n = len(sub); acc = sum((r['mean'] >= 0.5) == r['holds'] for r in sub)
        brier = sum((r['mean'] - (1 if r['holds'] else 0))**2 for r in sub) / n if n else float('nan')
        lo, hi = wilson(acc, n); return {'n': n, 'accuracy': acc / n if n else float('nan'), 'ci95': [lo, hi], 'brier': brier}
    t2 = []
    judged = [s for s in studies.values() if s['holds'] is not None]
    if judged:
        p = sum(s['holds'] for s in judged) / len(judged)
        t2.append({'structure': 'Base rate (always "holds", odds at the base rate)', **agg([{'mean': p, 'holds': s['holds']} for s in judged])})
    for structure in sorted({r['structure'] for r in rows}):
        sub = [r for r in rows if r['structure'] == structure]
        t2.append({'structure': structure, **agg(sub), 'unrecognised': agg([r for r in sub if r['recognised'] is False]) if any(r['recognised'] is False for r in sub) else None})
    os.makedirs(OUT, exist_ok=True)
    json.dump({'researchers': t1, 'structures': t2, 'rows': rows, 'studies': studies}, open(os.path.join(OUT, 'table.json'), 'w'), indent=1)
    L = ['# Results', '', '## 1. The researchers against the record', '',
         f"Studies: {t1['studies']}. Reports: {t1['reports']} (holds: {t1['researcher_yes']}, does not hold: {t1['researcher_no']}, cannot tell: {t1['cannot_tell']}).",
         f"Agree with the record: {t1['agree_with_record']} of {t1['of']} = {t1['accuracy']:.2f} (95% CI {lo:.2f} to {hi:.2f}).",
         f"On record, {t1['record_held_up']} of {t1['studies']} held up; saying \"did not hold\" every time scores {t1['base_rate_always_no']:.2f}.", '',
         '## 2. The review structures', '', '| Structure | n | Accuracy (95% CI) | Brier | Accuracy, unrecognised (n) |', '|---|---|---|---|---|']
    for t in t2:
        u = t.get('unrecognised'); ucell = f"{u['accuracy']:.2f} ({u['n']})" if u else '–'
        L.append(f"| {t['structure']} | {t['n']} | {t['accuracy']:.2f} ({t['ci95'][0]:.2f}–{t['ci95'][1]:.2f}) | {t['brier']:.3f} | {ucell} |")
    if len(t2) <= 1: L.append('| (no reviewer receipts yet) | | | | |')
    open(os.path.join(OUT, 'table.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))

if __name__ == '__main__':
    main()
