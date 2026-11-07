**Claim.** Words a participant has studied but then fails to recognise are still identified faster than words they never studied. Among test words a participant judges "new", words that were in fact studied (misses) are identified faster than words that were not studied (correct rejections). Predicted direction: mean identification RT for correct rejections is larger than for misses.

**Design.** Single group, fully within-subjects. Study phase: 70 word-identification trials of the kind described under Task and measure (the first and last 10 are filler words, never tested). Test phase: 100 identification trials of the same kind (50 studied, 50 new words, random order), each followed by an old/new recognition judgement. Which word list is old or new is counterbalanced across participants.

**Conditions.** Each test trial falls into one cell by item status × judgement: hit (old judged old), miss (old judged new), false alarm (new judged old), correct rejection (new judged new). The key test uses misses and correct rejections only.

**Task and measure.** On each trial a word is flashed for increasing durations inside a 250 ms block (17 ms more per block, the rest masked with #####, up to 15 blocks). The participant clicks as soon as they can identify the word, then reads it aloud. Identification RT is the time from stimulus onset to the click (ms; RTs over 3,750 ms are not recorded). The analysed score is each participant's mean test-phase RT in the miss cell and in the correct-rejection cell.

**Sample.** 32 adults, native German speakers, recruited from a university participant pool. No participant was excluded.

**Exclusion rules.** The protocol excludes trials where the word was misidentified, at study or at test. The per-participant means in the shared aggregate file (`d07.dat`: `meanRT_cr`, `meanRT_miss`) average over all classified test trials, with no identification filter, and the key test was run on that file.

**Test.** Two-sided paired t-test of `meanRT_cr` against `meanRT_miss`, n = 32, df = 31. Effect size dz = t / √n.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.txt` (text, 0 KB)
- `d03.dat` (text, 2 KB)
- `d04.sav` (SPSS, 2 KB)
- `d05.dat` (text, 2 KB)
- `d06.sav` (SPSS, 2 KB)
- `d07.dat` (text, 2 KB): 32 rows 5 columns tab-delimited, UTF-8 BOM, CRLF; per-participant mean RTs for hit/cr/fa/miss; meanRT_fa has 2 NA (not used by key test). The file the key test loads.
- `d08.sav` (SPSS, 2 KB): SPSS twin of the .dat, not opened
- `d09.dat` (text, 2 KB)
- `d10.sav` (SPSS, 2 KB)
- `d14.sav` (SPSS, 2.7 MB)
<!-- files:end -->
