# Literature Search: exogenous target data and theorem anchors for the Design-factor rule (M1)

Date: 2026-10-02
Search purpose: dataset/auxiliary-data discovery + theory anchoring, to upgrade the *measured* Design
rule of `main.tex` eqs. (42)–(43) into a **theorem-shaped** statement (or to make it a law over more
blocks). Feeds: experiment design (new data) and manuscript revision.
Target venue/family: IEEE TMC (journal; theory + measurement).
Source-quality policy: applied (MDPI and other policy-excluded sources kept out of the scored table; see
`search-notes.md`).
Verification level: **snippet-level only.** `web_fetch` is blocked in this environment (every host
resolves to a non-public IP), so no linked page or PDF was opened. Every row below is traceable to a
search result URL, but venue/year/claims must be re-checked at the source before any citation is written.

## Summary

- **What the user asked for:** "new data" that would let the Design rule be stated as a theorem.
- **What exists:** raw *public auxiliary data* that can serve as an exogenous target map for two of the
  four blocks (NYC: 311 + census; Beijing: UCI PM2.5 + WorldPop), plus MCS/FL datasets that carry real
  participation or population metadata (ParticipAct, MDC, LEAF). **No ready-made benchmark ships an
  exogenous client–stratum target map aligned with RAVEN-MCS's structure**, so a mapping step is needed.
- **Closest theorem templates:** design-based calibration / generalized raking, quasi-randomization for
  non-probability samples, and propensity-weighting under limited overlap. These host the *shape* of a
  support-gate theorem, and the paper already owns the missing bound (Support Lemma + Proposition 3).
- **Opportunity map:** `theory/analysis gap` (the gate is measured, not proved) + `benchmark gap` (no
  MCS benchmark with an exogenous target map) — both open at snippet level.
- **Recommended next action:** route A below (theorem-ize with an exogenous map on City Scanner), which
  needs **read-only recomputation, no training**.

## Data / auxiliary-source candidates (the "new data")

| # | Source | Link | What it provides | Fit for a block | Access/licence status | Risk |
|---|---|---|---|---|---|---|
| D1 | NYC 311 Service Requests (2010–present) | https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data | City-wide service-request counts by time and location | **City Scanner (NYC)**: exogenous proxy for *deployment demand* `π^tar` per tract × time block | Open data portal; licence not read (unverified) | Requests ≠ sensor interest; needs a defensible mapping rule |
| D2 | Azure Open Datasets: New York City safety | https://learn.microsoft.com/pt-br/Azure/open-datasets/dataset-new-york-city-safety | Mirror of NYC 311/incident data via a managed endpoint | Same as D1, easier join | Mirror; licence inherits the portal | Same as D1 |
| D3 | UCI Beijing PM2.5 | http://archive.ics.uci.edu/dataset/381/beijing+pm2.5+data | Hourly PM2.5 + meteorology, 12 stations, 2010–2014 | **U-Air (Beijing)**: exogenous station-level target mass | UCI repository, widely reused; licence unverified | Station→district mapping onto 144 client–strata not defined by the dataset |
| D4 | Beijing PM2.5 (Zenodo export record) | https://zenodo.org/records/3902671 | Archival copy of the same data | Same as D3 | Zenodo record; licence unverified | Duplicate of D3 |
| D5 | WorldPop 100 m population | https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop | Gridded residential population, global | Exogenous *population* prior for any city block (Beijing, NYC) | Open via Earth Engine; licence unverified | Population ≠ crowdsensing demand; coarse for stratum-level mass |
| D6 | ParticipAct (Bologna) | https://www.lia.deis.unibo.it/ (project) — dataset described in a 2024 MCS-security paper (snippet only) | Real participation traces, ~171 users, GPS | Cross-block **gate validation**: a block with real participation and no air-quality target | Release terms unverified | Only ~171 users; demand map absent |
| D7 | Mobile Data Challenge (Nokia/Idiap, Lausanne) | https://www.idiap.ch/~gatica/publications/LaurilaGaticaEtal-mdc12.pdf | Large real smartphone dataset with a documented volunteer population | Cross-block gate validation with a *documented sampling frame* | Research-release terms unverified | Volunteer sample ≠ deployment population |
| D8 | LEAF benchmark (Caldas et al., arXiv:1812.01097) | http://xxx.itp.ac.cn/abs/1812.01097v3 (arXiv mirror) | Federated benchmark with real natural partitions: FEMNIST writers, Shakespeare characters, Sent140 users | Population-level target weights are *documented*, so `ρ_r`/the gate can be computed without inventing a map | Public benchmark | Not an MCS block: no geography, no `O/U` semantics; would be a *method* transfer, not a deployment one |

## Theory anchors (theorem-ization templates)

| # | Anchor | Link | Theorem shape it hosts | Verification |
|---|---|---|---|---|
| T1 | Calibration estimators / generalized raking (Deville–Särndal tradition; SCB R&D report) | https://scb.se/contentassets/7d78fc7dc1e643729f7e8388cd3adf32/rnd-report-1990-01-green.pdf | "Weights calibrated to known auxiliary totals are design-consistent when the calibration support contains the target" → the gate becomes the *support condition* of a calibration theorem | Snippet-level |
| T2 | Quasi-randomization review for non-probability samples (BLS/OSMR 2024) | https://www.bls.gov/osmr/research-papers/2024/pdf/st240030.pdf | Taxonomy: propensity, calibration, mass imputation — i.e. three ways to inject an *exogenous* target | Snippet-level |
| T3 | Propensity-score weighting under limited overlap and model misspecification | https://web3.arxiv.org/pdf/2006.04038v1 | Weight trimming/bounding with an explicit bias–variance trade-off → the *switch point* of eq. (43) as an optimal-trimming analogue | Snippet-level |
| T4 | Bounded-violation treatment-effect estimation | https://browse-export.arxiv.org/pdf/2510.05454 | Estimator behaviour when overlap/positivity is violated by a bounded amount → matches the paper's `ε_π` residual | Snippet-level |
| T5 | Weighting non-probability samples (Valliant, FCSM slides) | https://www.fcsm.gov/assets/files/docs/A-4_Valliant_2018FCSM_slides.pdf | Practical conditions under which weighting repairs a non-random sample | Snippet-level |
| T6 | Kennedy (2022)-style discussion of opt-in survey misreporting (Statistics Canada) | https://www150.statcan.gc.ca/n1/pub/12-001-x/2022002/article/00005-eng.pdf | Caveats for self-reported auxiliary variables | Snippet-level |
| — | Crump–Hotz–Imbens–Mitnik, "Dealing with limited overlap…" | not retrieved | The canonical optimal-trimming rule; would be the closest prior art for eq. (43) | **Not retrieved** (repeated queries returned a faculty publication list only) — retrieve before citing |

## Paper table (only what the search result itself establishes)

| # | Title | Year | Venue/source | Link | Type | Insight | Completeness | Numeric evidence | Overall | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | LEAF: A Benchmark for Federated Settings | 2018 | arXiv:1812.01097 | http://xxx.itp.ac.cn/abs/1812.01097v3 | pure benchmark | 4 | 4 | N/A benchmark | B | benchmark with real natural partitions and documented populations |
| 2 | The Mobile Data Challenge: Big Data for Mobile Computing Research | 2012 | Idiap/Nokia (conference paper PDF) | https://www.idiap.ch/~gatica/publications/LaurilaGaticaEtal-mdc12.pdf | pure benchmark | 3 | 4 | N/A benchmark | B | real smartphone population; pre-dates current MCS framing |
| 3 | Review of Quasi-Randomization Approaches for Estimation from Non-probability Samples | 2024 | BLS/OSMR research paper | https://www.bls.gov/osmr/research-papers/2024/pdf/st240030.pdf | survey | 4 | 4 | 3 | B | official-statistics review; the cleanest taxonomy to place the gate |
| 4 | Propensity score weighting under limited overlap and model misspecification | 2020 | arXiv:2006.04038 | https://web3.arxiv.org/pdf/2006.04038v1 | theory/proof | 4 | 4 | 4 | B | trimming/bounding theory; closest to eq. (43) |
| 5 | Calibration estimators and generalized raking (SCB R&D report) | 1990 | Statistics Sweden R&D report | https://scb.se/contentassets/7d78fc7dc1e643729f7e8388cd3adf32/rnd-report-1990-01-green.pdf | theory/proof | 5 | 4 | 2 | A | the anchor for "calibrate to known totals" |
| 6 | Estimating treatment effects under bounded (violation) | 2025 | arXiv:2510.05454 | https://browse-export.arxiv.org/pdf/2510.05454 | theory/proof | 3 | 3 | 3 | C | adjacent; useful for the `ε_π` residual |

Scores are the skill's 1–5 anchors (insight / completeness / numeric evidence) and are **provisional**:
they were assigned from search snippets, not from reading the papers, because retrieval is blocked here.

## Clusters

### Cluster 1: exogenous auxiliary data for urban demand (`benchmark gap`, `deployment/system gap`)
- Representative sources: D1–D5.
- Already solved: public, joinable city-scale demand/population layers exist for NYC and Beijing.
- Remaining gap: **none of them is expressed in the paper's client–stratum structure**, so an exogenous
  `π^tar` requires a documented mapping rule (station/tract → client × time block).
- Rescue/differentiation route: define the map once, publish it as a frozen artifact, and evaluate the
  gate against the measured endpoint trade-off on that block.
- How it affects the paper: turns `ρ_r` from a *local* statistic into an *exogenous* input, which is
  exactly the condition a theorem needs.

### Cluster 2: design-based calibration / non-probability inference (`theory/analysis gap`)
- Representative anchors: T1, T2, T5.
- Already solved: the theory of calibrating weighted estimators to known totals, and its consistency
  conditions.
- Remaining gap: nobody states the condition we need — *what to do when the delivered support does not
  cover the target support* — as a gate on a method's design factor; the closest work trims or bounds
  propensity weights instead.
- Rescue route: state Proposition 3's bound with `ε_π = 0` under `ρ_r = 0`, and add the complementary
  direction (a lower bound on the excess when `ρ_r > 0`).
- How it affects the paper: this is the theorem, and it reuses machinery the appendix already proves.

### Cluster 3: limited-overlap / positivity theory (`crowded but open`)
- Representative anchors: T3, T4, plus the un-retrieved Crump et al. rule.
- Already solved: optimal trimming and bounded-violation estimation in causal inference.
- Remaining gap: those results are about *treatment-effect* weighting; the analogue for target-mass
  calibration under a Design factor is not written.
- Rescue route: import the trimming argument to define the *switch point* as an explicit bias–variance
  optimum rather than a measured indifference condition.
- How it affects the paper: gives eq. (43) a derivation instead of a measurement, if the paper is willing
  to state the deployment's endpoint weights as a loss.

### Cluster 4: MCS/FL datasets with real populations (`benchmark gap`)
- Representative sources: D6–D8.
- Already solved: real participation traces and real population partitions exist.
- Remaining gap: none ships an exogenous *target* mass for the sensing quantity.
- Rescue route: use them only to show the gate's decision is stable across blocks with different
  participation laws (not to prove the theorem).
- How it affects the paper: converts "two blocks" into "N blocks" at the cost of a mapping and a
  re-run; does not by itself produce a theorem.

## Opportunity Map

| Cluster | Status | Open gap | Possible direction | Evidence needed | Risk |
|---|---|---|---|---|---|
| 1 exogenous data | benchmark gap | no map in client–stratum form | publish a frozen exogenous map for ≥1 block | mapping rule + recomputed gate + endpoint trade-off | mapping may be contestable |
| 2 calibration theory | theory/analysis gap | no support condition stated for this factor | proposition: `ρ_r = 0` ⇒ `ε_π = 0` and the factor is admissible | proof sketch from Support Lemma + Prop 3 | may be seen as re-labelling an existing lemma |
| 3 overlap theory | crowded but open | trimming analogue not written | derive the switch point as an optimum | a stated loss + the trimming argument | needs a loss the deployment actually owns |
| 4 MCS/FL data | benchmark gap | no exogenous target | cross-block gate validation | 2–3 more blocks with a target | mapping effort, no theorem |

## Benchmark And Dataset Candidates

| Name | Link | Task | Metrics | Baselines | Fit | Risks |
|---|---|---|---|---|---|---|
| NYC 311 + ACS tract population | https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data | exogenous demand map for City Scanner | `ρ_r`, gate decision, `Δ_group`, `Δ_c-s`, `RMSE_μ` | current locally constructed map | **high** (same city as a reported block) | mapping rule must be pre-registered |
| UCI Beijing PM2.5 + WorldPop | http://archive.ics.uci.edu/dataset/381/beijing+pm2.5+data | exogenous map for U-Air | same | current map | medium (144 strata mapping) | station→stratum assignment |
| LEAF (FEMNIST/Shakespeare/Sent140) | http://xxx.itp.ac.cn/abs/1812.01097v3 | population-documented FL blocks | gate decision vs. endpoint trade-off | — | medium (method transfer only) | no geography, no `O/U` |
| ParticipAct, MDC | see D6/D7 | participation-law variation | gate stability | — | low–medium | no demand target |

## Citation And Positioning Cautions

- Claims that need direct citation before use: the calibration/raking anchor (T1), the non-probability
  review (T2), and the limited-overlap theory (T3, and Crump et al. if used).
- Papers that may weaken novelty: none found that states a *support gate for a Design factor* in MCS or
  FL; the nearest neighbours are client-selection fairness surveys in FL (one MDPI hit, excluded by
  policy and therefore not listed) and the overlap-trimming theory.
- Papers that only support background: D6–D8 (real-population datasets), T5–T6 (practical caveats).
