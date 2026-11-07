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

## Presentation mode (7 November, 17:45)

`Main.dc.html` carries a `presentation` switch (on by default) for the stage:

1. **Produce the science.** On any study's cell. Desk 02 replays that study's finished run: its real lines (the files read, the test, the statistic, p, the effect size, `holds`) print fast, the files appear in `report/`, the PDF renders. No agent runs; the desk says "replay".
2. **Send over the wall (pretend).** Packs and sends nothing; the lane fills, the receipt comes back after a beat.
3. **Reveal the record.** Appears once the receipt is in. Two verdicts, each `matches` or `differs`: the blind researcher against the original paper, and the panel (a mock that endorses the report it read) against the replication on record. The paper and the replication open only on a further click in the drawer.

The numbers come from `papers/S##/report/conclusion.json` and `papers/S##/sealed/truth.json`, baked into `findings.js`. Nothing on the page names an RPP row; the citation is shown only behind the reveal, as `sealed/original/citation.md` already is.
