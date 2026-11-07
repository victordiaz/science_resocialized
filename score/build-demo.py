#!/usr/bin/env python3
"""Build demo/mock.html: the one-button presentation. Embeds, per study: the hypothesis (first sentence of the card),
the researcher's conclusion and statistic (real, from report/conclusion.json), the sealed record's outcome and statistics
(real, from sealed/truth.json: this page IS the reveal, so it is for the presenter's screen), a link to the paper on GitHub,
and a MOCK panel verdict (deterministic pseudo-random, labelled as mock on the page) because no panel has run yet.
Usage: python3 score/build-demo.py [github_base]"""
import json, os, re, glob, sys, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://github.com/vnicolescu/science-resocialized/blob/master'
studies = []
for sdir in sorted(glob.glob(os.path.join(ROOT, 'papers', 'S*'))):
    code = os.path.basename(sdir)
    card = open(os.path.join(sdir, 'card.md'), encoding='utf-8').read()
    claim = next((l for l in card.splitlines() if l.startswith('**Claim')), '')
    claim = re.sub(r'^\*\*Claim[^*]*\*\*\s*', '', claim); first = re.split(r'(?<=[.!?])\s', claim, 1)[0]
    c = json.load(open(os.path.join(sdir, 'report', 'conclusion.json'))) if os.path.exists(os.path.join(sdir, 'report', 'conclusion.json')) else {}
    t = json.load(open(os.path.join(sdir, 'sealed', 'truth.json')))
    rng = random.Random(code)
    researcher_yes = str(c.get('holds', '')).lower() == 'yes'
    agree = rng.random() < 0.8
    odds = rng.uniform(0.62, 0.93) if (researcher_yes == agree) else rng.uniform(0.08, 0.42)
    studies.append({'code': code, 'hypothesis': first, 'researcher': c.get('holds', '?'), 'statistic': c.get('statistic', ''), 'p': c.get('p', ''),
                    'es': c.get('effect_size', ''), 'n': c.get('n_after_exclusions', ''), 'minutes': c.get('minutes', ''),
                    'record': t.get('replicate_r', '?').lower(), 'record_p': t['table'].get('p_r', ''), 'record_es': t['table'].get('es_r', ''), 'record_n': t['table'].get('n_r', ''),
                    'paper': f'{BASE}/packets/{code}/paper.pdf', 'panel_mock_odds': round(odds, 2)})
data = json.dumps(studies)
html = open(os.path.join(ROOT, 'demo', 'mock.template.html'), encoding='utf-8').read().replace('/*DATA*/[]', data)
os.makedirs(os.path.join(ROOT, 'demo'), exist_ok=True)
open(os.path.join(ROOT, 'demo', 'mock.html'), 'w', encoding='utf-8').write(html)
print(f'demo/mock.html: {len(studies)} studies; {sum(1 for s in studies if s["researcher"]==s["record"])} researcher/record agreements')
