# Literature Monitoring Report: venue-watch (IEEE / TMC) — RAVEN-MCS overlap scan

**Skill:** `ccf-literature-monitor` · mode `standard` (venue-watch + novelty-check)
**As of:** 2026-09-27
**Primary time range:** 2026-06-01 → 2026-09-27
**Extended sweep (where the productive hits came from):** 2026-01-01 → 2026-09-27
**Sources scanned:** public web search index only (36 queries). Target hosts IEEE Xplore, IEEE CSDL (`computer.org`), DBLP, OpenAlex, Crossref.
**Papers scanned:** ≈70 result entries screened; 14 distinct works examined at title/abstract level; 12 retained.
**High-relevance papers:** 2 (overlap score 3); no score-4/5 hit.
**Overall signal:** **RESEARCH**

---

## 0. Discovery limitation (read this before trusting the coverage claim)

`web_fetch` failed for **every** host attempted in this session — `api.openalex.org`, `dblp.org`, `api.crossref.org`, `www.computer.org`, `ieeexplore.ieee.org` all returned `URL hostname resolves to a non-public IP address` (local DNS/proxy restriction). Consequences:

- I could **not** enumerate TMC issue tables of contents (Vol. 25, issues 6–9), so **TMC coverage is index-derived and therefore incomplete**. Absence of a TMC hit below is not proof of absence.
- Venue and publication-date metadata for several candidates is **unverified**; those rows are marked `venue unverified`.
- A complete TMC sweep needs one of: reachable DBLP API (`dblp.org/search/publ/api?q=venue:TMC:`), reachable OpenAlex (`primary_location.source.issn:1558-0660`), or an IEEE Xplore/CSDL session. **This is a tooling blocker, not a finding.**

**Source-policy exclusions applied:** MDPI excluded from search results, citation, and scoring. One MDPI hit (`Applied Sciences` 16(700), "the client filtering strategy introduces a representativeness bias…") was **dropped on that rule** despite topical relevance. If the user wants it reconsidered, that requires an explicit policy override.

---

## 1. Findings

Overlap score (diagnostic only): 0 = unrelated · 1 = same broad area · 2 = same problem or dataset · 3 = same problem + related mechanism · 4 = same problem + similar mechanism or claim · 5 = same problem, mechanism, and evidence path.

| # | Title | Source | Date | Overlap | Overlap type | Evidence basis | Action |
|--:|:---|:---|:---|:--:|:---|:---|:--:|
| 1 | [Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases](https://ar5iv.labs.arxiv.org/html/2604.26604) | arXiv:2604.26604 (`venue unverified`) | 2026-04 | **3** | Problem + claimed gap | Title + abstract: selection bias enters at *enrollment* (who joins) and *participation* (who uploads per round), and must be corrected rather than assumed away | **RESEARCH** |
| 2 | Missing gradients in FL are likely MNAR ([10.1145/3766882](https://dlnext.acm.org/doi/pdf/10.1145/3766882)) | ACM (`venue field unverified`) | 2026 | **3** | Claimed gap + evidence type | Body text states the MNAR claim explicitly: "we have established missing gradients in FL systems are likely to be MNAR" | **RESEARCH** |
| 3 | [Federated Inverse Probability Treatment Weighting for Individual Treatment Effect Estimation](https://dl.acm.org/doi/pdf/10.1145/3787464) | ACM (`venue field unverified`) | 2026 | 2 | Mechanism | IPW applied *inside* a federated loop; different estimand (causal ITE, not target mass) | RESEARCH |
| 4 | [Toward Efficient and Scalable Asynchronous Federated Learning via Stragglers Version Control](https://ieeexplore.ieee.org/abstract/document/11162622) | IEEE (`venue unverified`) | 2026 | 2 | Setting | Asynchronous FL aggregation under stragglers; mechanism is version control, not mass reweighting | RELAX |
| 5 | [A Reliability-Aware Client Selection Framework for Federated Learning on Heterogeneous Resources under Dynamic Availability](https://hal.science/hal-05663449v1/file/NUNES-dynamic-avail.pdf) | HAL preprint | 2026 | 2 | Setting | Dynamic client availability drives selection; no target-distribution correction | RESEARCH |
| 6 | [A Coverage-Aware High-Quality Sensing Data Collection Method in Mobile Crowd Sensing](https://dl.acm.org/doi/10.1109/TMC.2024.3502158) | **IEEE TMC** (doc 10758242) | 2025 | 2 | Problem setting | Coverage-aware collection in MCS; **not currently in `reference.bib`** | RESEARCH |
| 7 | [Federated Learning-Based Distributed Data Completion in Sparse Mobile CrowdSensing](https://www.computer.org/csdl/journal/tm/2026/05/11278111/2cjCXbgYBwI) | **IEEE TMC** 2026/05 | 2026 | 1 | Problem setting | FL for sparse-MCS completion; **already cited** in `reference.bib` | RELAX |
| 8 | [Choose Wisely and Privately: Proactive Client Selection for Fair and Efficient Federated Learning](https://www.semanticscholar.org/paper/Choose-Wisely-and-Privately%3A-Proactive-Client-for-Bendoukha-Arcolezi/bf135c7e16d9956d5b8e1ab30d34070a7396030e) | Semantic Scholar record | 2026 | 2 | Mechanism + endpoint | Client selection with a *fairness* endpoint, adjacent to the worst-group endpoint | RESEARCH |
| 9 | [Towards Fairness-aware Federated Learning (taxonomy)](https://dr.ntu.edu.sg/bitstream/10356/179048/2/Towards%20Fairness-aware%20Federated%20Learning.pdf) | NTU repository | 2025 | 2 | Endpoint | Taxonomy of fairness notions in FL; useful for positioning the worst-group endpoint, not a mechanism threat | RELAX |
| 10 | [KAFL-HD: Knowledge Alignment in Asynchronous Federated Learning With Heterogeneous Data](https://ieeexplore.ieee.org/document/11314801) | IEEE (`venue unverified`) | 2026 | 1 | Setting | Async FL with heterogeneous clients; no selection/mass correction | RELAX |
| 11 | [Federated Reinforcement Learning for Efficient Mobile Crowdsensing Under Incomplete Information](https://www.semanticscholar.org/paper/Federated-Reinforcement-Learning-for-Efficient-Dongare-Weber/bc17fdffdaf751bad7f456540becfa9f3ebd3079) | Semantic Scholar record | 2026 | 1 | Problem setting | MCS + FL with incomplete information; RL-based control, not estimator correction | RELAX |
| 12 | [QUIDS: Quality-Informed Incentive-Driven Multiagent Dispatching System for Mobile Crowdsensing](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=11370477) | IEEE (`venue unverified`) | 2026 | 1 | Problem setting | Incentives and dispatching in MCS; orthogonal to aggregation correction | RELAX |

Also screened and set aside (overlap 0–1): [PEFL](https://ieeexplore.ieee.org/document/11359552) (privacy/collusion/backdoor in MEC crowdsensing FL); [CrowdFL](https://ieeexplore.ieee.org/document/9730020/citations) (2022, privacy in MCS-via-FL); [Noisy Multi-Label Aggregation With Self-Supervised Graph Transformer in Mobile Crowdsourcing](https://www.semanticscholar.org/paper/Noisy-Multi-Label-Aggregation-With-Self-Supervised-Liu-Tang/b48b7854ef377a3f79d3797dd306cb59f1dcf543); [Enhanced Byzantine-Robust FL Via Truncated-Quadratic Loss](https://ieeexplore.ieee.org/document/11710267); [HDFL: Hierarchical Decentralized FL for IoV](https://pureportal.coventry.ac.uk/files/122070465/Djahel2026AAM.pdf); [Caring Without Sharing: FL Crowdsensing for Diversifying Representation of Cities](https://export.arxiv.org/pdf/2201.07980) (2022, outside window but thematically adjacent).

---

## 2. TMC-specific verdict

**No TMC paper found in the scanned window that corrects non-random client participation/observation selection in federated aggregation.** The TMC 2026 material the index surfaced is spatio-temporal **data completion** and **spatio-temporal FL**, and the manuscript already cites five TMC 2026 entries plus four TMC 2023–2025 entries — its TMC citation vintage is current:

| Already cited TMC entries (from `reference.bib`) | Year |
|:---|:---|
| Adaptive Asynchronous Federated Learning in Resource-Constrained Edge Computing | 2023 |
| Spatiotemporal Urban Inference and Prediction in Sparse Mobile CrowdSensing | 2023 |
| Staleness-Controlled Asynchronous Federated Learning: Accuracy and Efficiency | 2024 |
| A New Data Completion Perspective on Sparse CrowdSensing | 2025 |
| Rethinking the Effect of Sparse Data Completion on Sparse Mobile Crowdsensing | 2025 |
| Federated Learning-Based Distributed Data Completion in Sparse Mobile CrowdSensing | 2026 |
| Spatio-Temporal Pyramid-Based Multi-Scale Data Completion in Sparse Crowdsensing | 2026 |
| MapT-STC: A One-Shot Spatiotemporal Data Completion Framework for Cold-Start | 2026 |
| STDFL: A Spatio-Temporal-Aware Dynamic Federated Learning Framework for Spatio-Temporal… | 2026 |

The one **uncited** TMC item worth acting on is **#6** (TMC 2025, coverage-aware MCS data collection) — it is the nearest TMC neighbour to the "coverage / representativeness" framing and belongs in Related Work as a contrast: it optimises *which* data to collect, whereas RAVEN-MCS corrects the *mass distortion* of what was already collected.

Given the discovery limitation in §0, treat "no TMC overlap" as **unsearched, not disproven** (per the evidence policy: unsearched novelty is uncertainty, not novelty).

---

## 3. Actionable flags

- **RESEARCH (items 1, 2):** these are the only two works that touch the manuscript's actual novelty claim — that non-random selection in a federated pipeline must be *modelled and corrected*, not assumed away. Neither one is MCS, neither uses a target map, and neither carries a worst-group or cross-source endpoint. **Differentiation is available on all three axes** (three-layer R/O/U decomposition; `ζ̂ = π^tar/max{π̂^opp, π_min}` target-mass alignment instead of an arrival law; endpoint-keyed evaluation). But the "first to notice participation bias in FL" framing is **no longer available**, and item 2 pre-empts the bare MNAR observation.
- **RELAX:** the remaining ten items share at most a setting or a broad area. No mechanism collision found. Do not claim full novelty proof — see §0.
- **No FOLLOW-UP item.** Nothing found matches problem + mechanism + evidence path simultaneously.

---

## 4. Handoff signals

- **`ccf-literature-searcher`** — deep-retrieve and pin venues/dates for items **1, 2, 3, 4, 5, 8**; specifically resolve whether arXiv:2604.26604 has an IEEE/ACM published version, and identify the title of ACM DOI `10.1145/3766882`. Cluster to build: *selection/participation bias correction in federated aggregation*.
- **`ccf-idea-reviewer`** — novelty-risk input: the "non-random participation in FL is unmodelled" gap statement is now occupied at the *problem* level by item 1 and at the *assumption* level by item 2. Score impact is on the gap/positioning axis, not the mechanism axis.
- **`ccf-idea-optimizer`** — differentiation route: keep the three-layer R/O/U decomposition and the target-map alignment, and explicitly scope the claim to *mobile crowdsensing spatial-mass correction with an externally supplied target map*, which none of the 12 items occupies.
- **`ccf-paper-writer`** — Related Work / positioning: add item **6** (TMC 2025 coverage-aware MCS) as the nearest TMC contrast, and add a one-sentence acknowledgement that participation bias in FL has been studied (items 1–2) while the target-mass distortion under a *known* target map has not.
- **`ccf-integrity-auditor`** — no attribution conflict found; every cited IEEE entry in `reference.bib` (54 entries total) was left untouched. Note the standing pending action to verify the 24 of 54 bib entries remains open and was **not** advanced by this run.

---

## 5. Proposed project-state key

No project-level `ccfa.yaml` exists at the workspace root (only `CCFA-Skills/ccf-project-scaffolder/assets/ccfa.yaml` and the demo copy). If one is created, record:

```yaml
artifacts:
  literature_monitor_last_run:
    date: 2026-09-27
    mode: venue-watch
    window: 2026-01-01..2026-09-27
    signal: RESEARCH
    top_items: [arXiv:2604.26604, doi:10.1145/3766882]
    uncited_citation_candidate: doi:10.1109/TMC.2024.3502158
    coverage_caveat: web_fetch blocked; TMC TOC not enumerated
```

---

**Output self-check:** date range explicit ✓ · source basis and its limitation stated ✓ · table valid markdown, scores are diagnostic only ✓ · no unsupported novelty conclusion (TMC absence recorded as unsearched, not disproven) ✓ · MDPI exclusion applied and disclosed ✓ · no private manuscript text, local absolute paths, or unpublished results used in any query ✓
