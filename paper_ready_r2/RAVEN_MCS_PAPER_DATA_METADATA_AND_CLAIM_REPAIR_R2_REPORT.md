# RAVEN-MCS paper-data metadata and claim repair R2

## 1. Executive decision

- Final status: `PAPER_DATA_R2_FINAL_READY_FOR_TDRIVE_PROTOCOL_SEAL`
- Inst paper-facing label: `ENDPOINT_TRADEOFF`
- w/o-Inst generation in core: `2`
- T-Drive: `NOT_READY_OPPORTUNITY_UNFROZEN` (formal runs started = false)

## 2. No-training attestation

See `00_index/R2_NO_TRAINING_ATTESTATION.json`. No training, no E1–E4 reruns, no T-Drive formal runs, no new seeds/datasets/baselines, no preprocessing or metric-definition changes.

## 3. R1 issues addressed

- Incomplete E4 ablation_mean / raw_p / CI fields rebuilt from 240 cells.
- Inst label inconsistency (R3 seal `STRUCTURAL_ONLY_SUPPORTED` vs instruction `ENDPOINT_TRADEOFF`) unified to paper-facing `ENDPOINT_TRADEOFF`.
- Sparse dataset summary rebuilt with provenance.
- Sparse config registry rebuilt.
- Pipeline summary / ZIP manifests generated from physical ZIP members after creation.

## 4. E4 Inst claim repair

- Sealed R3 status (historical): `STRUCTURAL_ONLY_SUPPORTED` tagged `OLD_SUPERSEDED_LABEL`.
- R2 paper-facing: `ENDPOINT_TRADEOFF` (claim ceiling C8).
- Numeric basis: mixed point-estimate directions. Under frozen 5-component Holm, SensorScope `Delta_c_s` worsen and U-Air RMSE/Tail worsen remain significant; improve-side Holm p-values sit at ~0.0515 (not significant). That cross-endpoint pattern is still an endpoint tradeoff.
- Audit: `05_provenance/E4_COMPONENT_LABEL_CONSISTENCY_AUDIT.csv`.

## 5. E4 statistics reconstruction

- Input: `E4_FINAL_VALID_EVIDENCE_240.csv` sha256=`36dfedb95bf1990009f80e02fe739f64d19ec3633dad357beaa5c840da02224c`.
- Protocol: paired Wilcoxon signed-rank, Holm per (dataset, metric) × 5 ablations, Cohen dz, CI = mean ± 1.96 sd/√n, EPS_ZERO=1e-12.
- Holm note: R3 mixed Gen1 Inst into parent Holm and Holm-adjusted Inst Gen2 in isolation (m=1). R2 rebuilds Holm from the 240 Gen2 cells with the frozen 5-component family. `sealed_r3_p_holm` retained for provenance.
- Optional MAE_mu / RMSE_rho: not in the 240 CSV (`MISSING_NOT_RECORDED`); extracted from sealed `final_metrics.json` as supporting diagnostics only.
- Mechanical classifier: `{'Design': 'ENDPOINT_TRADEOFF', 'Obs': 'ENDPOINT_TRADEOFF', 'Use': 'NO_CLEAR_EFFECT', 'Inst': 'ENDPOINT_TRADEOFF', 'Debt': 'STRUCTURAL_ONLY_SUPPORTED'}`
- Claim-numeric conflicts: `[]`

## 6. E4 final component interpretation

| Component | Paper-facing label |
|-----------|-------------------|
| Design | ENDPOINT_TRADEOFF |
| Obs | ENDPOINT_TRADEOFF |
| Use | NO_CLEAR_EFFECT |
| Inst | ENDPOINT_TRADEOFF |
| Debt | STRUCTURAL_ONLY_SUPPORTED (quantitatively small) |

## 7. Dataset metadata reconstruction

- Datasets: 4 (SensorScope, U-Air, NSW-Traffic, T-Drive-Speed readiness-only).
- Provenance rows: 112. Guessed fields: 0.

## 8. Dataset metadata provenance

`05_provenance/DATASET_METADATA_PROVENANCE.csv` — every recovered field has source path, key, sha256, method, and status.

## 9. Config registry reconstruction

- Rows: 7. Provenance gaps: 0.
- E3 source revision: `b01db69e8554a33446c438c060ac464dcfadac24`. E2: `e56687813f2bcb919a9208391f68a4db3488602e`.

## 10. Source/config identity audit

See `05_provenance/FINAL_CONFIG_IDENTITY_AUDIT_R2.csv`. E1 is PARTIAL_BUT_PAPER_SAFE (sanity block). T-Drive is readiness-only.

## 11. Traffic comparability boundary

E2 Traffic is usable for risk-semantic evidence. E3 Traffic cross-vintage inference is `NOT_COMPARABLE`. Encoded in `00_index/TRAFFIC_COMPARABILITY_BOUNDARY_R2.json`.

## 12. P2 claim boundary

Allowed: audited feasibility. Not allowed: certified exact optimality of warning-affected experimental P2 outputs. Encoded in `00_index/P2_CLAIM_BOUNDARY_R2.json`.

## 13. Optional diagnostics recovered

- Run-level scalars: 280 rows (ESS, MAE_mu, RMSE_rho, clip rates, Q norms, runtime, solver_status).
- Window active-client rows: 25200.
- Supporting only; not new RQ answers.

## 14. Optional diagnostics still missing

Debt/ESS/P2-runtime *trajectories* (time series) remain `MISSING_NOT_RECORDED`. window_metrics.json keys observed: ['a_r_size', 'active', 'active_clients', 'alpha', 'beta_hat', 'window_id'].

## 15. T-Drive readiness refresh

- status: `NOT_READY_OPPORTUNITY_UNFROZEN`
- formal_tdrive_runs_started: false
- Not READY_FOR_50_RUNS.

## 16. Master evidence rebuild

- run-level rows: 1305
- long rows: 7350
- E3 Traffic in master inferential cells: 0 (must be 0)
- E4 run-level: 240 (must be 240)

## 17. Figure/table provenance

`00_index/FIGURE_TABLE_PROVENANCE_MAP_R2.csv` — TABLE-1/2/3 and FIG-1/2/3 plus optionals.

## 18. Numeric consistency audit

Unresolved core VALUE_CONFLICT count: 0. See `10_reports/PAPER_READY_NUMERIC_CONSISTENCY_AUDIT_R2.csv`.

## 19. ZIP manifest verification

- CORE members: 140 pass=True
- FULL members: 4795 pass=True
- Manifests generated from physical ZIP members after creation.

## 20. Missing core/supporting/optional data

No CORE E1–E4 cells missing. Supporting/optional gaps listed in `MISSING_POTENTIALLY_USEFUL_DATA_R2.md`.

## 21. Can the paper-ready evidence now be frozen?

YES — E1–E4 paper-ready evidence can be frozen for manuscript drafting. T-Drive remains a separate future protocol-seal authorization.

## 22. Exact recommended next step

Do **not** start T-Drive. Next authorized scientific step is a **T-Drive protocol seal** (opportunity, EventTrace, split, seed policy) under a separate instruction file. Manuscript drafting may use `RAVEN_MCS_PAPER_DATA_CORE_R2.zip`.
