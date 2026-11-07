**Claim.** Men are less able than women to tell, from a photograph, a woman's friendliness apart from her sexual interest. The replication tests this as a gender × stimulus-category interaction on the per-category discrimination score defined below, with the categories friendly vs sexually interested. The prediction is that the gender difference in that score is not the same for the two categories: men's deficit lies in separating sexual interest from friendliness. The exact term is that interaction, not the gender main effect on the two scores averaged.

**Design.** Mixed: participant gender (male vs female) is between-participants; stimulus category is within. Presentation time (500 ms vs 3,000 ms per image, randomly assigned) is a further between factor, but it is not part of the key model.

**Task.** 280 full-body photographs of women, 70 in each of four categories: friendly, sexually interested, sad, rejecting. Each image is shown once, in four blocks of 70, after a 250 ms fixation. After each image the participant classifies it by pressing 1–4 (friendly / sexually interested / sad / rejecting).

**Measure.** Per-category discrimination score ln(α). For stimulus category i, with m = 4 categories: ln α_i = Σ over j ≠ i of ln[P(R_i|S_i) / P(R_j|S_i)], divided by √2 · m · (m − 1). Here P(R_i|S_i) is the proportion of category-i images classified correctly, and P(R_j|S_i) is the proportion classified as category j. Zero counts are replaced by 0.5. The scores are precomputed in the data file as `Sens_Friend` and `Sens_SI` (columns 22–23 of `d02.sav`); higher means better discrimination.

**Sample.** 144 heterosexual undergraduates (65 male, 79 female), aged 18–26. No exclusions: all completed the task and no outliers were identified.

**Test.** 2 (category: `Sens_Friend` vs `Sens_SI`, within) × 2 (`Gender`, between) mixed ANOVA, type III. The key term is the Gender × category interaction, F(1, 142), with partial η². Equivalently, a one-way between-gender ANOVA on `Sens_Friend − Sens_SI`.

<!-- files:start -->
**Data files given.** The raw data you receive, under neutral names:
- `d02.sav` (SPSS, 16 KB): 144 rows 25 columns ID, Age, Gender (79 F / 65 M), Pres_time, hit/FA/miss/correct-rejection counts and Sens_* scores; no missing on the key columns
<!-- files:end -->
