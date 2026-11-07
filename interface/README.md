# The redesigned bench, as a Design canvas

Live canvas (Claude Design, private until shared): https://claude.ai/artifact/Dtsvh87MC7UvTKcX1fYnh7

This folder is a copy of the canvas's own files, taken 7 November 2026 ~17:20. It is the source for the replacement
`bench.html` (one file, no build step, same `/api/state` contract as `page/server.py`), built with Vlad's Vivarium
design system.

| File | What |
|---|---|
| `Main.dc.html` | the live board: masthead and the thirty ticks, the desks, the wall, the findings cells, the finding drawer with the two-verdict reveal and the admin's manual review |
| `Phone.dc.html` | the same page at 390 px |
| `States.dc.html` | a finding's eight states as the API names them |
| `Record.dc.html` | the drawer with the paper and the reproduction opened, for the humans on this side |
| `Wall.dc.html` | the wall in three moments: packed, crossing, received |
| `Factory.dc.html` | the two-part system: production here, verification on the other machine, the reveal |
| `Reveal.dc.html` | the reveal played through for S23 with a mock verdict: the two matches first, the paper and the replication on a further click |
| `bench.css` | every style the artboards share, on Vivarium's tokens (`ds/vivarium/tokens.css`) |
| `findings.js` | the thirty findings as `/api/state` reports them, plus `code` (S01..S30) and `handle` (four to seven words, no label from the literature) |
| `ds/vivarium/` | the design system's tokens and the three faces (SIL OFL 1.1) |
| `canvas.json` | the canvas index: artboards, notes, the design-system record |

Each `.dc.html` is a self-contained page: the markup between `<x-dc>` tags is plain HTML with `{{holes}}` and
`<sc-for>`/`<sc-if>` for loops and branches; the script at the bottom computes the values. Port the markup and the CSS;
replace `window.BENCH` with the polled `/api/state`.

Fields the page reads that `/api/state` must carry: `run {alias, strategy}`, `findings[].code` (S01..S30),
`findings[].handle`, `findings[].package {path, sha256, run, study, at}`, `findings[].handoff.receipt {at,
sha256_matches, verdict {odds_holds, holds}}`, `findings[].verdicts {researcher_vs_paper, panel_vs_replication}`
(computed on this side against the sealed record, `matches | differs | null`), `findings[].review {at, by, call, note}`
(the admin's manual review, this side only).
