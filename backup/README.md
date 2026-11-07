# Backup: the researchers' reports

This folder is a marked copy of every finished researcher report, kept so the review can be run directly from here if the
two-machine demonstration is not ready. The source folders are `papers/S##/report/`; this copy is rebuilt by `score/backup.py`.

Each `reports/S##/` holds the card the researcher worked from, the report as PDF and Markdown, the researcher's log and
analysis script, and `conclusion.json`. Nothing here says what the paper was or what the replication found: that is in
`papers/S##/sealed/`, opened only by the scorer or at the reveal.

To run a review from here: give a reviewer `reports/S##/` and `papers/S##/data/` with `briefs/review-brief.md`, collect
`round1.json` (and `round2.json` after the board) under `verdicts/S##/<structure>/<reviewer>/`, then run `score/score.py`.
