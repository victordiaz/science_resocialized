**Claim (hypothesis).** When a list of words is shown and the participant must reproduce it in order straight away, lists made of short words are recalled in the correct order better than lists made of long words. Direction: proportion of words recalled in the correct serial position is higher for short-word lists than for long-word lists. The confirmatory test uses the English-language lists only.

**Design.** Within-subjects. Each participant sees 80 lists of eight words: 2 list languages (English, Dutch) x 2 word lengths (short = 1, long = 2), 20 lists per cell. After each list the eight words are shown and the participant clicks them in the order they were presented. The Dutch lists are a second, exploratory condition and are not part of the key test.

**Measures.** Per trial, `nr_correct` = number of the eight words placed in their correct serial position (0 to 8). Per participant and cell, the DV is the mean of `nr_correct / 8` across the 20 lists of that cell, rounded to three decimals (the replication's script rounds before testing).

**Sample.** 15 university students, mostly native Dutch speakers (one native German speaker), recall tested in English as a second language. One data file per participant (`1.txt` to `dd09.txt`, 80 rows each); the participant is identified by the file, not by a column.

**Exclusions.** None. All 15 participants and all 80 trials enter the analysis.

**Test.** Paired t-test on the per-participant DV, English short-word lists vs English long-word lists, one-sided (H1: short > long), df = n - 1. Effect size d_z = t / sqrt(n).

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d06.txt` (text, 15 KB)
- `d07.txt` (text, 15 KB)
- `d08.txt` (text, 15 KB)
- `d09.txt` (text, 15 KB)
- `d10.txt` (text, 15 KB)
- `d11.txt` (text, 15 KB)
- `d12.txt` (text, 15 KB)
- `d13.txt` (text, 15 KB)
- `d14.txt` (text, 15 KB)
- `d15.txt` (text, 15 KB)
- `d16.txt` (text, 15 KB)
- `d17.txt` (text, 15 KB)
- `d18.txt` (text, 15 KB)
- `d19.txt` (text, 15 KB)
- `d20.txt` (text, 15 KB)
- `d21.txt` (text, 16 KB)
- `d22.txt` (text, 15 KB)
<!-- files:end -->
