# CCFA Paper Re-Review — RAVEN-MCS / IEEE TMC

> Independent current-version review after wording revisions. Assesses reviewer-visible sources and the manuscript-named public artifact only. Does not use prior review scores as evidence anchors.

## 1. Scope

```text
Review date: 2026-09-11 (evening wording pass)
Materials:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex, appendix.tex, supplemental.tex
  Current main.log / main.pdf (14 pages)
  RAVEN_MCS_PUBLIC_REPRO_R1
Verified:
  verify.py → checked=1883, mismatches=0
  rebuild_table_ii.py → Table II 4-decimal freeze matched
  rebuild_table_ii_tolerance.py → disclosed +0.5% percentages matched
Experiment follow-up (readonly):
  MANIFEST city|scanner hits = 0; CS SUMMARY CSVs exist outside the public bundle and match appendix decimals
  U-Air WorstGroup relative vs FedAU/ObsUse: ALL20 ≈ +0.002% / +0.075%; TEST10 ≈ +0.478% / +0.443%
  E3_FORMAL_HOLM_RESULTS.csv has no fedau/obsuse (or WorstGroup) rows for the stated Holm claim
```

## 2. Summary

RAVEN-MCS separates opportunity, observation, and usable-update selection from a public deployment target, forms a sequential Hájek-style reference when Design is on, and calibrates aggregation inside the current feasible set.

This wording pass improves claim alignment. The title and keywords now say **target-mass** rather than **target-risk**; Design-off is explicitly an uncorrected \(\widehat\zeta=1\) factor; \(k(i)\) is defined as the unique attached FL client on the frozen occupancy map; and Availability states that the bundle is not a pinned retraining archive and that NSW four-region is not a confirmation experiment. Those changes reduce overclaim risk.

They do not remove the main scientific barriers: Design-off changes the estimand precisely when support is difficult; \(\phi=0\) remains a dataset-global heuristic rather than a positivity certificate; no ranking jointly measures R/O/U; City Scanner tables remain unbundled; and the author block is still an illegal mix of placeholders and identifiers.

## 3. What improved in this wording pass

1. **Title/keywords.** `Target-Mass-Calibrated` and `target-mass alignment` match the proved scope better than the previous target-risk framing (`main.tex:55`, `100–102`).
2. **Design-off honesty.** The paper repeatedly states that \(\widehat\zeta=1\) does not reconstruct target mass (`main.tex:79–82`, `670–675`, `1918–1921`).
3. **\(k(i)\) definition.** The SCD lookup now states that \(k(i)\) is the unique attached client on the frozen occupancy map, with stations/cells as attachments (`main.tex:1000–1005`; `appendix.tex:63–71`).
4. **Availability ceiling.** The manuscript now says the verifier reconstructs tabulated cells, the bundle is not a pinned retraining archive, and NSW is not a confirmation experiment (`main.tex:1952–1956`).
5. **Artifact integrity holds.** SHA-256 verification and Table II rebuilds continue to pass.

## 4. Major concerns

### C1 — Design-off is still a different method, not a target-mass safeguard

When \(\phi>0\), Algorithm 1 sets \(\widehat\zeta^o=1\) on all observed pairs (`main.tex:670–675`, `1023–1029`). Target-zero observations can still receive positive observation/usable-update weights and enter local training and P2. The paper’s disclaimer is correct, but the operational method then becomes uncorrected factorization plus calibration. U-Air and T-Drive, the difficult-support cases, evaluate this second configuration.

Required: rename the two branches everywhere (e.g., RAVEN-Design vs RAVEN-NoDesign), and either zero/mask target-zero pairs or present NoDesign only as a non-identifying fallback.

### C2 — \(\phi=0\) is still not a positivity certificate, and its lookup object changes by block

Even with \(k(i)\) defined, \(\phi\) counts whether the attached client–stratum has zero target mass. It does not verify that every target-positive \((k,i)\) has positive opportunity/observation/usable probability. The appendix explicitly says that when several clients realize opportunity on the same unit, \(\phi\) still uses only the attached client (`appendix.tex:68–71`). The switch is also not derived from A1/A5 (`main.tex:1009–1010`).

Moreover, the frozen \(\phi\) constructions are not the same object across blocks (`appendix.tex:2181–2185`): SensorScope/U-Air look up test-split client–stratum mass; T-Drive looks up test-split stratum frequency; City Scanner assigns the test-group share \(\mu_{h(i)}\) to training atoms. The same \(\phi=0\) rule therefore compares differently constructed support statistics. City Scanner’s construction makes \(\phi=0\) especially easy when all regions are positive.

Required: either test all relevant target-positive pairs under one frozen construction, or label \(\phi\) as a pre-registered heuristic deployment rule and stop reading \(\phi=0\) as a comparable cross-block confirmation.

### C3 — Empirical evidence remains protocol/hybrid and prediction-mixed

Table II is always-on protocol opportunity on station traces. T-Drive has real \(R\) but controlled \(O/U\) and loses the descriptive +0.5% rule to FedAU/ObsUse. City Scanner/Pilot 2 are hybrid and also do not establish a stable RMSE win (`main.tex:1564–1638`, `1644–1668`). The strongest recurring RAVEN signal is structural composition.

The disclosed U-Air +0.5% tolerance is also slice-fragile: `rebuild_table_ii_tolerance.py` uses TEST seeds `30011–30020` (~+0.48% / +0.44% vs FedAU/ObsUse), while the ALL20 mean relative gaps collapse to ≈ +0.002% / +0.075%. Table II still reports 20-seed means, so the external descriptive endpoint rides on the second half of the seed list. Separately, the claim that Holm tests against FedAU/ObsUse are not significant (`main.tex:1669`) has no matching `fedau`/`obsuse` (or WorstGroup) rows in the public `E3_FORMAL_HOLM_RESULTS.csv`; directionally consistent Wilcoxon can be recomputed from per-seed CSV, but the stated Holm family is not released.

Required: one jointly measured R/O/U mobile study, or keep an explicit protocol/hybrid-only claim ceiling and demote prediction-superiority language; report ALL20 alongside TEST10 for the descriptive tolerance, and release the Holm family used in text.

### C4 — Reproducibility is table-level, and City Scanner evidence is still missing

The artifact verifies and rebuilds Table II. Availability now admits it is not a pinned retraining archive (`main.tex:1954–1956`), and README still points to a companion repository for end-to-end training (`RAVEN_MCS_PUBLIC_REPRO_R1/README.md:68–79`). City Scanner tables used in the abstract and conclusion remain unbundled (`main.tex:1952–1954`); `MANIFEST.csv` has zero `city|scanner` hits. Matching SUMMARY CSVs exist elsewhere in the repo and agree with appendix decimals, but that does not count as public-bundle reproducibility. T-Drive and NSW `new_target` are table-level packaged; NSW also carries a config trap (`configs/protocol_closure/traffic/public_target.json` is still UTC four-block uniform \(\mu\), not the four-region map).

Required: commit-pinned executable archive, environment lock, one-command runners, and City Scanner/E4/NSW runner provenance; or remove unreleased blocks from the main claim chain.

### C5 — Naming and presentation still fight the narrowed claim

The acronym expands to “Risk Alignment…” while the title is Target-Mass (`main.tex:155–157`, `623`). Section III is still titled “Target-Risk Formulation” (`main.tex:334`). The abstract is about 296 words and functions as a compressed evaluation dump rather than a problem–method–finding abstract (`main.tex:67–97`). City Scanner tables are cited in the main text but defined only in the supplement (appendix tables near `appendix.tex:2237–2315`), so a main-PDF reader cannot inspect the table body. The main PDF is 14 pages and relies on `\enlargethispage` (`main.log:659`; `main.tex:1958–1960`). The symbol \(\phi\) is also overloaded as both the SCD switch and the Proposition 2 test function (`main.tex:993` vs `1152`). Baseline short names also drift (`FedAU`/`ObsUse` versus `*-Window`; hyphenation of TwoStage-Hájek).

Required: align acronym/section titles with target-mass; rename one \(\phi\); compress the abstract to roughly 180 words; either move one City Scanner table into the main PDF or demote those rankings from the abstract; resolve page-limit/overlength policy.

## 5. Moderate / compliance concerns

- Author block mixes `****` with a real name, grant, institution, and emails (`main.tex:57–60`). Fix before ScholarOne.
- Trajectory/GPS governance still lacks redistribution, de-identification, and IRB/exemption statements beyond source terms and “FL is not a privacy guarantee” (`main.tex:1910`, Availability).
- FedAU/ObsUse/TimeAlign remain adaptations, not official reproductions.
- Arrival-law plug-in still multiplies an observation probability by a usable-update quantity described as an evaluation-period marginal (`main.tex:519–537`); state the joint marginalization step.
- Gate remains diagnostic and adaptive RESET validity is unproved; keep it out of the main contribution story.

## 6. Scorecard

| Dimension | Score (1–5) | Confidence | Basis |
| --- | ---: | ---: | --- |
| Novelty | 3 | 4 | MCS R/O/U separation plus feasible calibration is coherent; ingredients are established. |
| Soundness | 3 | 4 | Claim ceilings and \(k(i)\) definition improved; Design-off and \(\phi\) still lack optimality/positivity closure. |
| Evidence | 3 | 4 | Auditable Table II and candid negatives; U-Air tolerance TEST10-sensitive; no jointly measured R/O/U win. |
| Significance | 3 | 4 | Framing matters for MCS; deployment-level utility unshown; mixed real-\(R\) rankings. |
| Clarity | 3 | 4 | Title/keywords better; abstract, acronym, and multi-block narrative remain dense. |
| Reproducibility | 2 | 5 | Hash and Table II pass; no pinned retrain path; City Scanner unbundled; Holm-vs-FedAU family not in public Holm CSV. |
| Ethics / limitations | 2 | 4 | Scope honesty improved; author mode and trajectory governance incomplete. |

**Recommendation: Major revision — 5/10.**  
**Review confidence: 4/5.**

## 7. Revision priorities

```text
P0
  1. Resolve author anonymity mode.
  2. Bundle City Scanner evidence or remove it from abstract/conclusion claims.
  3. Publish a commit-pinned executable source archive and environment lock.

P1
  4. Separate RAVEN-Design and RAVEN-NoDesign claims and tables.
  5. Replace or demote φ=0 to an explicitly heuristic rule; define support tests over target-positive pairs.
  6. Align acronym/section titles with target-mass; compress abstract and evidence hierarchy.
  7. Disclose ALL20 vs TEST10 for the U-Air descriptive tolerance; release the Holm family cited against FedAU/ObsUse.

P2
  8. Add jointly measured R/O/U mobile evidence, or keep a protocol/hybrid-only ceiling.
  9. Add official or stronger target-aware baselines where feasible.
```

## 8. Verdict

The wording pass is a real improvement in scientific honesty: the paper now markets target-mass alignment, defines the SCD client lookup, and states the artifact’s table-only scope. It is still not acceptance-ready. The remaining barriers are method coverage under Design-off, the heuristic nature of \(\phi\), hybrid/mobile evidence limits, and incomplete release/compliance packaging.
