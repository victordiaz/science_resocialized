**Claim (hypothesis).** The brain's electrical response that follows a wrong button press (the error-minus-correct difference in scalp voltage in the first 100 ms after the response, a negative voltage; variable `ERN`) reflects a defensive reaction to errors, so across people, a larger error response goes with a larger increase, after errors compared with after correct responses, in the eye-blink to a sudden loud noise (variable `EPS`). Because the error response is a negative voltage, a larger one is a more negative value: the predicted effect is a **negative** correlation between `ERN` and `EPS`.

**Design.** Correlational, across participants; one session per participant with EEG and EMG recording.

**Conditions and procedure.** Each trial shows a row of five arrowheads; the participant presses a left or right button for the direction of the central one; on half the trials the outer arrowheads point the same way as the central one, on half the opposite way; 200 ms stimuli; intertrial interval 500–1,000 ms; one practice block and eight blocks of 30 trials, with accuracy/speed feedback after each block. A loud white-noise burst (the noise probe) is presented after some error responses and after some correct responses (on predictable and unpredictable correct trials).

**Measures.** `ERN`: the error-minus-correct difference in response-locked EEG, mean amplitude 0–100 ms after the response at the fronto-central sites, mastoid-referenced, 0.1–30 Hz, eye-movement corrected (µV; variable `ERN`). `EPS`: eye-blink EMG magnitude to the noise probe under the left eye (band-pass 28–512 Hz, rectified, low-pass 30 Hz, peak 20–120 ms after the probe) after errors minus after correct responses (µV; variable `EPS`). File: `d05.csv`, long format, one row per participant × probe type (`startle_type`: error / predict / unpred), with `ERN` and `EPS` repeated on each of a participant's rows; use one row per participant (e.g. the `error` rows).

**Sample and exclusions.** Adults aged 18–35, normal or corrected vision, no neurological history; planned N = 42. Protocol exclusions: participants with electrode impedance above 5 kΩ at any analysis electrode, or with excessive muscle artefact. The posted file holds the retained participants only (42 participant ids); no further exclusions.

**The test.** Pearson product-moment correlation between `ERN` and `EPS`, one value pair per participant, df = n − 2. The protocol (following the original study) evaluates it **one-tailed in the predicted negative direction**; effect size is r itself. Not the key test: the paired t-tests showing that the error response and the after-error blink increase exist at all.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.csv` (CSV, 1 KB): 72 rows 2 columns ERN/EPS pairs, apparently the combined original+replication set used for a secondary analysis; not the key test
- `d03.txt` (text, 54 KB)
- `d04.txt` (text, 54 KB): ERP waveform exports, not needed for the key test; not opened
- `d05.csv` (CSV, 6 KB): 126 rows 8 columns CR-only line endings; long format, ERN and EPS repeated across the 3 startle_type rows per participant; participant ids 1-51 minus 3,4,10,18,20,28,37,40,44; one startle value '???' in an unpred row (not used by the key test)
- `d08.csv` (CSV, 6 KB): 126 rows 8 columns CR-only line endings; long format, ERN and EPS repeated across the 3 startle_type rows per participant; participant ids 1-51 minus 3,4,10,18,20,28,37,40,44; one startle value '???' in an unpred row (not used by the key test)
<!-- files:end -->
