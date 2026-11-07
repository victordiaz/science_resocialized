#!/usr/bin/env python3
"""The packets: one self-contained folder per study, the synthetic paper with its data, under a name anyone can find.
packets/S##/  paper.pdf, paper.md, card.md, conclusion.json, data/ (the given files, neutral names, manifest of hashes)
packets/INDEX.md, packets/README.md. Rebuilt from papers/S##/ by this script; idempotent."""
import os, shutil, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = os.path.join(ROOT, 'packets')
rows = []
for sdir in sorted(glob.glob(os.path.join(ROOT, 'papers', 'S*'))):
    code = os.path.basename(sdir); rep = os.path.join(sdir, 'report')
    if not os.path.exists(os.path.join(rep, 'report.pdf')): continue
    dst = os.path.join(P, code); os.makedirs(os.path.join(dst, 'data'), exist_ok=True)
    shutil.copy2(os.path.join(rep, 'report.pdf'), os.path.join(dst, 'paper.pdf'))
    shutil.copy2(os.path.join(rep, 'report.md'), os.path.join(dst, 'paper.md'))
    shutil.copy2(os.path.join(sdir, 'card.md'), os.path.join(dst, 'card.md'))
    if os.path.exists(os.path.join(rep, 'conclusion.json')): shutil.copy2(os.path.join(rep, 'conclusion.json'), os.path.join(dst, 'conclusion.json'))
    for f in os.listdir(os.path.join(sdir, 'data')):
        s = os.path.join(sdir, 'data', f); d = os.path.join(dst, 'data', f)
        if not os.path.exists(d) or os.path.getsize(s) != os.path.getsize(d): shutil.copy2(s, d)
    c = json.load(open(os.path.join(rep, 'conclusion.json'))) if os.path.exists(os.path.join(rep, 'conclusion.json')) else {}
    n = len([f for f in os.listdir(os.path.join(dst, 'data')) if f != 'MANIFEST.json'])
    rows.append(f"| [{code}]({code}/) | [paper.pdf]({code}/paper.pdf) | {c.get('holds','?')} | {c.get('statistic','')} | {n} |")
open(os.path.join(P, 'INDEX.md'), 'w').write('# Packets\n\n| Study | Paper | Researcher says | Statistic | Data files |\n|---|---|---|---|---|\n' + '\n'.join(rows) + '\n')
open(os.path.join(P, 'README.md'), 'w').write('''# Packets: the synthetic papers with their data

One folder per study. Each holds the paper a researcher agent wrote from the data alone (`paper.pdf`, `paper.md`), the card
it worked from (`card.md`: the hypothesis stated operationally, the design, the measures, the exclusion rules), its one-line
`conclusion.json`, and `data/`: the raw data under neutral names with a manifest of hashes. Nothing in a packet names the
original paper or says what the published replication found; that is in `papers/S##/sealed/`, opened only at the reveal.

Give a packet to a reviewer, a panel, or a person with an agent; collect their verdict; then open the seal and compare.
`INDEX.md` lists the thirty. Rebuilt from `papers/` by `score/packets.py`.
''')
print(f'packets: {len(rows)} studies')
