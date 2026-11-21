# CCFA Paper Re-Review — RAVEN-MCS / IEEE TMC

> Current-version, independent assessment of the manuscript and its named public artifact on 2026-09-11. The report does not use earlier review reports or scores as evidence.

## 1. Scope

```text
Reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex, supplemental.tex, appendix.tex
  Current compiled main.log
  RAVEN_MCS_PUBLIC_REPRO_R1 and its supplied verification/rebuild scripts

Verified:
  python verify.py                       → checked=1883, mismatches=0
  python scripts/rebuild_table_ii.py     → canonical Table II matched
  python scripts/rebuild_table_ii_tolerance.py → disclosed percentages matched

Not verified:
  full GPU retraining, raw-data preprocessing, or a public source archive
  for the exact code revision that generated E3/E4 and the hybrid results
```

## 2. Summary

RAVEN-MCS separates three selection layers—opportunity, observation, and usable update—from a public deployment target. It constructs a sequential Hájek-style target-mass reference when the opportunity/design factor is enabled, then calibrates aggregation inside the current feasible set using P2 and target debt.

The current version now makes essential boundaries explicit: Design-off sets the opportunity factor to one and is **not** target-mass reconstruction; Proposition 2 is limited to ideal target-moment/group-mass recovery; the +0.5% endpoint is a descriptive tolerance, not a non-inferiority test; the coverage Gate is diagnostic; and T-Drive/City Scanner are hybrid rather than end-to-end MCS evidence. These revisions materially improve scientific honesty and remove the previous artifact-integrity failure.

## 3. Strengths

- **Clear statistical decomposition.** R/O/U, legal histories, target mass, and finite-window feasibility are separated coherently (`main.tex:360–500`, `620–805`).
- **Claim discipline.** The paper no longer presents target-mass recovery as a target-risk optimization/convergence theorem (`main.tex:210–220`, `1050–1056`, `1170–1188`).
- **Definitions are now closed.** The main paper defines \(I_{\rm tar}\) using \(\pi^{\rm tar}_{k,s}\); the supplement gives compatible target-pair mass and the \(\phi\) lookup construction (`main.tex:450–500`; `appendix.tex:19–70`).
- **Transparent negative evidence.** T-Drive does not satisfy the descriptive tolerance against FedAU/ObsUse; City Scanner/Pilot 2 also report stronger prediction baselines where appropriate (`main.tex:1560–1600`, `1612–1638`).
- **Artifact repair is real.** The canonical SCD Table II, per-seed worst-group data, and two rebuild scripts match the displayed table and stated tolerance. The SHA-256 manifest now passes completely.

## 4. Major Concerns

### C1 — The proposed operational method ceases target-mass reconstruction precisely on target-support conflicts

When \(\phi>0\), Algorithm 1 sets \(\widehat\zeta^o=1\) for observed pairs (`main.tex:670–676`, `1016–1026`). The manuscript now correctly says this is an uncorrected opportunity factor, rather than target-mass reconstruction. But this narrows the method substantially: \(\phi>0\) is plausible exactly in the difficult deployments the paper motivates, including U-Air and T-Drive. The evidence on those settings therefore evaluates a different, uncorrected factorization-plus-calibration configuration.

The \(\phi=0\) condition is also a dataset-global safeguard, not a target-positive overlap diagnostic. It is not necessary or sufficient for A1 positivity. More concretely, the model permits a unit \(i\) to be observed by multiple clients, yet \(\phi\) queries a unique, undefined \(k(i)\) (`main.tex:996`, `1016`; `appendix.tex:64`). The map must be defined from the system model or replaced by a test over all relevant \((k,i)\) pairs. The paper should rename the two configurations explicitly (e.g., *RAVEN-Design* and *RAVEN-NoDesign*) and state the target-mass claim only for the former. A stronger revision would define a target-positive support restriction or partial-identification policy, rather than turning Design fully off.

### C2 — The title and motivation still outrun the validated learning claim

The deployment objective is \(Y\)-based target risk, but the local objective fits observations \(Z_{k,r,i}\) (`main.tex:502–555`, `742–766`). The authors expressly disclaim a \(Z\!\to\!Y\) measurement model, gradient unbiasedness, target-risk convergence, and asynchronous optimization guarantee. That is scientifically responsible, but it means “Target-Risk-Calibrated” currently denotes an intended semantic reference, not a proved learning property.

Either add a measurement/heterogeneity model and a target-gradient or excess-risk result, or consistently title and frame the contribution as **target-mass-aware feasible aggregation**. The current paper is strongest as a target-composition and aggregation study.

### C3 — TMC systems validation remains incomplete

The E3 main table uses always-on protocol opportunity on station traces (`main.tex:1344–1433`). T-Drive supplies real mobility opportunity but controlled O/U; City Scanner supplies real visit opportunity, and Pilot 2 supplies measured O, but U remains controlled (`main.tex:1370–1392`, `1562–1599`, `1612–1638`). The manuscript states these limits accurately.

This is adequate evidence for controlled and hybrid evaluation, not for deployment-level performance under jointly observed R/O/U. The real-R T-Drive result also leaves FedAU/ObsUse strongest. A TMC revision needs either one end-to-end real mobile study or a tighter contribution/evidence claim that does not imply it.

### C4 — Reproducibility has improved but is table-level, not training-level

The artifact now passes all 1,883 SHA-256 checks and regenerates the Table II presentation/tolerance. However, it still says full retraining requires a “companion repository” without giving an immutable source URL/commit archive, environment lock, or executable end-to-end command (`RAVEN_MCS_PUBLIC_REPRO_R1/README.md:68–79`). It excludes full E3/E4 run dumps and T-Drive per-window dumps. The two City Scanner result blocks also are not in the released bundle (`main.tex:1941–1950`).

The NSW four-region artifact is useful but should not be represented as a formal confirmation experiment: its audit records only ten seeds, no held-out test seeds or formal NI result, and `p2_solver_nonneg_clip=true`; it identifies a missing runner path (`new_target/AUDIT.json:1–46`). The mean summaries and per-seed CSVs are internally consistent, but a current executable script, solver configuration, clipping audit, and pre-specified inferential analysis are needed.

Release a DOI/commit-pinned code archive, dependency lock, raw-data acquisition and preprocessing scripts, one command per experiment, and per-seed data for E2/E4/City Scanner. The present package supports result inspection, but not independent retraining.

### C5 — The evaluation narrative is fragmented and does not establish a stable predictive benefit

The main table, T-Drive, NSW four-region, City Scanner, and Pilot 2 have materially different selection realizations and are repeatedly declared non-comparable (`main.tex:244–264`, `1324–1342`, `1562–1638`). That disclosure is correct, but it makes the paper's empirical argument difficult to follow: SensorScope does not win RMSE; U-Air is statistically tied with adapted FedAU/ObsUse; T-Drive loses to both; City Scanner has FedAvg or TwoStage-Hájek as the best prediction method. The recurring RAVEN advantage is structural composition, not a stable completion-error improvement.

Keep one controlled protocol result and one external hybrid validation in the main paper, put the remaining role-specific blocks in the supplement, and introduce the evidence hierarchy once. The abstract should state the structural objective and one representative limitation rather than enumerate every ranking.

## 5. Moderate Concerns

- The arrival-risk display multiplies an observation probability by a usable-update quantity described as an evaluation-period marginal, although \(q^{\rm use}\) is conditional on a post-sensing history (`main.tex:418–440`, `520–536`). State the joint marginalization or conditional-independence step explicitly.
- FedAU-Window, ObsUse-Window, and TimeAlign-Agg are adaptations, rather than official baseline reproductions (`main.tex:1434–1450`). Publish their exact policies/configurations and state a uniform tuning/compute budget.
- The Gate is safely demoted to a diagnostic and the paper admits adaptive RESET/CERTIFIED validity is unproved (`main.tex:1270–1306`, `1900–1906`). Moving it fully to the supplement would improve focus.
- The main PDF currently compiles to 14 pages (`main.log:659`), with multiple underfull-box warnings. Confirm journal submission/camera-ready length policy and anticipated overlength handling; cut the long abstract and duplicated scope qualifications before relying on overlength.
- The source still mixes anonymized placeholders and identifying author, institution, grant, and email details (`main.tex:57–60`; `supplemental.tex:59–62`). Resolve this before upload.
- GPS/trajectory data governance is limited to source terms and CC BY disclosure. Add whether raw trajectories are redistributed, the de-identification boundary, and the applicable ethics/IRB or exemption status.
- Recompile against the current official TMC template: the `subfig`/`caption` stack logs a document-class compatibility message even though compilation completes.

## 6. Scorecard

| Dimension | Score (1–5) | Confidence | Basis |
| --- | ---: | ---: | --- |
| Novelty | 3 | 4 | MCS-specific R/O/U separation plus feasible calibration is a coherent integration; core ingredients are established. |
| Soundness | 2 | 5 | Conditional identification and convex-program scope are clear, but the global \(\phi\) test is not a positivity certificate and uses an undefined \(k(i)\) lookup. |
| Evidence | 3 | 4 | Table II and tolerance values are auditable; hybrid/mobile results are candid but mixed. |
| Significance | 3 | 4 | The target-versus-arrival framing matters for MCS, but deployment-level utility is not established. |
| Clarity | 2 | 4 | Definitions are improved, but the abstract over-enumerates incomparable blocks and duplicated scope qualifications obscure the main evidence chain. |
| Reproducibility | 2 | 5 | Integrity and table reconstruction pass; source-to-training-result closure and City Scanner release are absent. |
| Ethics / limitations | 2 | 4 | Scope limitations are candid; author mode and trajectory governance remain incomplete. |

**Recommendation: Major revision — 4/10.**  
**Review confidence: 4/5.**

## 7. Required Revision Priorities

```text
P0 — submission/release
  1. Resolve author mode and page-limit/overlength requirements.
  2. Publish a commit-pinned executable code archive and environment lock.
  3. Release City Scanner, E2, and E4 source-to-table evidence or remove
     unreleased results from the central argument.

P1 — scientific scope
  4. Separate RAVEN-Design (target-mass reconstruction) from RAVEN-NoDesign
     (uncorrected opportunity factor) everywhere in claims and tables.
  5. Define \(k(i)\), or test every relevant client–unit pair; replace global φ=0
     with a target-positive overlap/restriction policy, or present it only as a
     heuristic deployment guard.
  6. Narrow “target-risk-calibrated” to target-mass/composition alignment unless
     a Z-to-Y and asynchronous-optimization bridge is proven.

P2 — evidence quality
  7. Add a jointly measured R/O/U mobile experiment, or retain an explicit
     protocol/hybrid-only empirical claim.
  8. Publish exact adapted-baseline specifications and add stronger target-aware
     comparisons where implementation is feasible.
  9. Consolidate the main-paper evidence hierarchy to one controlled and one
     external block; move the remaining role-specific rankings to the supplement.
```

## 8. Verdict

The revision has removed several avoidable credibility failures: the artifact now verifies, target-pair notation is specified, and claims are far more disciplined. The remaining barriers are substantive scope rather than presentation: the Design-off configuration is not target-mass reconstruction, the learning objective is not connected to target-risk optimization, and the evidence is still controlled/hybrid rather than end-to-end mobile MCS. This is a credible major-revision submission, but not ready for acceptance in its current form.
