#!/usr/bin/env python3
"""The backup: every finished researcher report, in one marked folder, so the review can be run directly from it
if the two-machine demonstration is not ready. Idempotent; run as reports land.

backup/
  README.md             what this is and how to run a review from it
  INDEX.md              one line per study: conclusion, statistic, minutes
  reports/S##/          card.md, report.pdf, report.md, conclusion.json, log.md (the researcher's log), analysis.py, fig1.png
  briefs/review-brief.md
Nothing from sealed/ is copied here.
"""
import json, os, shutil, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'backup'); os.makedirs(os.path.join(B, 'reports'), exist_ok=True); os.makedirs(os.path.join(B, 'briefs'), exist_ok=True)
KEEP = ['card.md', 'report/report.pdf', 'report/report.md', 'report/conclusion.json', 'report/log.md', 'report/analysis.py', 'report/analysis.R', 'report/analysis.out', 'report/fig1.png']
rows = []
for sdir in sorted(glob.glob(os.path.join(ROOT, 'papers', 'S*'))):
    code = os.path.basename(sdir); concl = os.path.join(sdir, 'report', 'conclusion.json')
    if not os.path.exists(concl): continue
    dst = os.path.join(B, 'reports', code); os.makedirs(dst, exist_ok=True)
    for rel in KEEP:
        s = os.path.join(sdir, rel)
        if os.path.exists(s): shutil.copy2(s, os.path.join(dst, os.path.basename(rel)))
    c = json.load(open(concl))
    rows.append(f"| [{code}](reports/{code}/report.pdf) | {c.get('holds','?')} | {c.get('statistic','')} | {c.get('p','')} | {c.get('n_after_exclusions','')} | {c.get('minutes','')} |")
shutil.copy2(os.path.join(ROOT, 'briefs', 'review-brief.md'), os.path.join(B, 'briefs', 'review-brief.md'))
open(os.path.join(B, 'INDEX.md'), 'w').write('# Reports on record\n\n| Study | Researcher says | Statistic | p | n | Minutes |\n|---|---|---|---|---|---|\n' + '\n'.join(rows) + '\n')
open(os.path.join(B, 'README.md'), 'w').write('''# Backup: the researchers' reports

This folder is a marked copy of every finished researcher report, kept so the review can be run directly from here if the
two-machine demonstration is not ready. The source folders are `papers/S##/report/`; this copy is rebuilt by `score/backup.py`.

Each `reports/S##/` holds the card the researcher worked from, the report as PDF and Markdown, the researcher's log and
analysis script, and `conclusion.json`. Nothing here says what the paper was or what the replication found: that is in
`papers/S##/sealed/`, opened only by the scorer or at the reveal.

To run a review from here: give a reviewer `reports/S##/` and `papers/S##/data/` with `briefs/review-brief.md`, collect
`round1.json` (and `round2.json` after the board) under `verdicts/S##/<structure>/<reviewer>/`, then run `score/score.py`.
''')
print(f'backup: {len(rows)} reports')
