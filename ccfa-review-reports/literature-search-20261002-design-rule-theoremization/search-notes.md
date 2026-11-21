# Search Notes

Mode: standard (feeds experiment design + manuscript revision).
Date: 2026-10-02.
Purpose: find **new data** that would let the Design-factor rule (`main.tex` eqs. (42)–(43)) be stated as a
theorem rather than measured on two block types.

## Safe Queries Used

Public keywords only; no draft sentences, no private results.

1. exogenous target population distribution open data mobile crowdsensing post-stratification auxiliary data
2. NYC Open Data 311 service requests census tract population auxiliary sampling frame crowdsourced sensing
3. Beijing air quality monitoring station open data U-Air dataset target population distribution
4. public dataset with documented sampling frame ground truth participation mobile crowdsensing coverage
5. LEAF benchmark federated learning dataset natural population sampling frame Caldas 2018
6. generalized raking calibration estimator auxiliary totals design-based consistency survey weights
7. limited overlap positivity propensity weight trimming bias bound theorem
8. federated learning benchmark real-world client population metadata distribution shift dataset
9. Crump Hotz Imbens Mitnik dealing with limited overlap optimal trimming rule average treatment effects
10. inference with non-probability samples calibration weighting review quasi-randomization
11. City Scanner dataset MIT Senseable City Lab municipal vehicles air quality data release
12. Mobile Data Challenge Nokia Lausanne dataset participation traces real population
13. Dealing with limited overlap in estimation of average treatment effects Crump Biometrika 2009 trimming rule
14. UCI Machine Learning Repository Beijing PM2.5 data set air quality multivariate
15. WorldPop gridded population estimates open data license census auxiliary covariates
16. ParticipAct dataset Bologna mobile crowdsensing participation traces public release
17. "Dealing with limited overlap in estimation of average treatment effects"
18. NYC Open Data 311 service requests from 2010 to present API dataset
19. mass imputation propensity weighting nonprobability sample target population auxiliary data review
20. federated learning client participation bias correction survey calibration 2024 2025 conference
21. support restriction target mass calibration proposition crowdsensing federated target distribution
22. auxiliary population data representativeness crowdsourced environmental sensing urban coverage bias

## Sources Checked

Via search results only (no page retrieval): Statistics Sweden R&D report; BLS/OSMR 2024 review; FCSM
slides (Valliant 2018); Statistics Canada survey-methods article; arXiv 2006.04038, 2510.05454,
2511.22003, 1812.01097; Idiap MDC paper; NYC Open Data portal; Azure Open Datasets mirror; UCI dataset
381; Zenodo record 3902671; WorldPop Earth Engine catalog; LEAF mirror; ParticipAct project and a 2024
MCS-security paper referencing it; RI-URBANS deliverable mentioning City Scanner; McGill thesis on
crowdsourced (Netatmo) sensor networks; AGU WRR paper on crowd observation density.

## Excluded Sources

- Policy-excluded or low-quality sources: one MDPI survey on client selection in non-IID federated
  learning appeared in the results and is **excluded by the source-quality policy**; it is not listed in
  the scored table. Two patent PDFs and several slide decks/theses also surfaced and were dropped as
  low-signal for citation purposes (kept only as discovery hints).
- Other exclusions: search-result PDFs whose only accessible content was a snippet were not promoted to
  the paper table, per the "snippet-only evidence" rule.

## Unknowns

- Papers not accessible: **all of them.** `web_fetch` is blocked in this environment (every host resolves
  to a non-public IP address), so no page, PDF or dataset landing page was opened. Venue, year, licence
  and numeric claims in `papers.md` are snippet-derived and must be re-verified before any citation.
- Venue status not verified: arXiv identifiers are recorded as such and are not claimed to be published.
- Missing benchmark details: LEAF's exact partition metadata, ParticipAct's release terms, and the NYC
  311 licence were not read.
- Not retrieved: Crump–Hotz–Imbens–Mitnik (Biometrika 2009). Repeated targeted queries returned only a
  faculty publication list; it is **not** in the scored table and must be retrieved before it is cited.
- Not found at all: any existing work that states a **support gate for a Design factor** in mobile
  crowdsensing or federated learning. Snippet-level impression: the slot looks open, but this is a weak
  basis for a novelty claim.

## Handoff Notes

- For writing: if the theorem route is taken, the citation set is T1 (calibration/raking) + T2
  (quasi-randomization taxonomy) + T3/T4 (limited overlap / bounded violation), all of which need page-level
  verification first. No MCS-specific prior art on support gates was found.
- For idea optimization: the two open slots are `theory/analysis gap` (the gate is measured, not proved)
  and `benchmark gap` (no MCS benchmark ships an exogenous target map).
- For direction scouting: the data exist as **raw auxiliary layers** (D1–D5), not as ready-made targets;
  the missing work is a documented mapping onto the client–stratum structure.
- For experiment design: three routes, in increasing cost —
  **(A) theorem with an exogenous map, one block** (City Scanner + NYC 311/ACS): freeze a mapping rule,
  recompute `ρ_r` and the gate, and re-run the endpoint comparison; read-only over existing runs, no
  training; the proposition would combine the appendix's Support Lemma with Proposition 3 at `ε_π = 0`
  and add the complementary lower bound when `ρ_r > 0`;
  **(B) cross-block validation** (ParticipAct/MDC/LEAF): shows the gate's decision is stable across
  participation laws; no theorem, but removes the "two blocks" scope limit;
  **(C) theory-only**, importing the trimming argument to derive eq. (43)'s switch point from a stated
  loss: no new data, but the external review has already said wording alone does not buy credit.
- For review: the honest risk is that (A) is *re-labelling*: the Support Lemma already implies `ε_π = 0`
  when the support matches, so the new content must be the exogenous map plus the `ρ_r > 0` direction.
