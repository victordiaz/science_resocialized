# Packets: the synthetic papers with their data

One folder per study. Each holds the paper a researcher agent wrote from the data alone (`paper.pdf`, `paper.md`), the card
it worked from (`card.md`: the hypothesis stated operationally, the design, the measures, the exclusion rules), its one-line
`conclusion.json`, and `data/`: the raw data under neutral names with a manifest of hashes. Nothing in a packet names the
original paper or says what the published replication found; that is in `papers/S##/sealed/`, opened only at the reveal.

Give a packet to a reviewer, a panel, or a person with an agent; collect their verdict; then open the seal and compare.
`INDEX.md` lists the thirty. Rebuilt from `papers/` by `score/packets.py`.
