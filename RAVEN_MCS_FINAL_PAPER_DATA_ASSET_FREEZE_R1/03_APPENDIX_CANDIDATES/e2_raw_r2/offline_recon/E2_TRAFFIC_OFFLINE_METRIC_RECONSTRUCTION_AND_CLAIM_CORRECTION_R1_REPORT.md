# E2_TRAFFIC_OFFLINE_METRIC_RECONSTRUCTION_AND_CLAIM_CORRECTION_R1_REPORT

## 1. Executive decision

**E2_TRAFFIC_SCIENTIFICALLY_SEALED**

## 2. No-training attestation

No model was trained. No optimizer.step. No formal run was re-executed. Metrics were reconstructed from frozen `group_rmse`, diagnostics, and EventTraces only.

## 3. Frozen 600-run evidence identity

Verification: `PASS` — 600 logical runs unchanged.

## 4. Metric-definition recovery

See `FROZEN_METRIC_DEFINITIONS.md`.

## 5. Reconstruction feasibility

See `METRIC_RECONSTRUCTION_FEASIBILITY.csv`.

## 6–9. Reconstructed metrics

- Head_RMSE / Tail_RMSE: exact from frozen partition + stored group_rmse (600/600 finite)
- Delta_group: diagnostics+eventtrace reconstruction (600/600 finite; nonnegative=True)
- Delta_pair: DEFINITION_NOT_RECOVERABLE for traffic formal

## 10–11. Structural analyses

See `STRUCTURAL_SCENARIO_VS_BALANCED_STATS.csv` and `STRUCTURAL_RAVEN_VS_BASELINE_STATS.csv` (Holm-corrected).

## 12–13. Corrected claims

See `E2_CLAIM_MATRIX.md`. Mandatory corrections applied (C2 conservative; C6/C7/C8 UNSUPPORTED; C9 from structural evidence only).

## 14. Claim-evidence validator

See `CLAIM_EVIDENCE_VALIDATION.json`.

## 15. Ledger anomaly semantic correction

START=601, FINISH=600, orphan/interrupted START=0. Historical ledger not rewritten.

## 16. Paper-ready statements

- Selection bias can make arrival- and target-weighted risks non-interchangeable (esp. Complete-aligned).
- Original Complete-aligned / Complete-counteracting directional hypotheses remain unsupported.
- RAVEN does not have Holm-significant RMSE_mu or RMSE_rho dominance over all baselines.
- Structural Head/Tail recovered; Delta_pair unavailable.

## 17. Unsupported statements that must not appear

- "RAVEN significantly outperforms all baselines"
- "smaller Gap_mis means less misalignment" (signed)
- "Complete-counteracting confirms the preregistered directional event"

## 18. Remaining missing evidence

Delta_pair (no frozen Π̂ / unbound traffic definition).

## 19. Final E2 closure decision

**E2_TRAFFIC_SCIENTIFICALLY_SEALED**

## 20. Recommended next experiment stage

Proceed to paper drafting under the corrected claim matrix. Do not start E3–E9 until paper needs explicitly require a new sealed experiment stage.
