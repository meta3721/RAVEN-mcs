# E3_PROTOCOL_REUSE_AND_READINESS_R1_REPORT

## 1. Executive decision

**E3_READY_WITH_REDUCED_DATASET_SCOPE_PENDING_TEACHER_AUTHORIZATION**

## 2. E1/E2 immutable parent status

- E1-R2: FULLY_SEALED
- E2-TRAFFIC: SCIENTIFICALLY_SEALED
- No E2 rerun; no training in this round

## 3. Original E3 scientific purpose

RQ2: Can full RAVEN-MCS improve deployment-target risk under Complete-aligned two-stage non-random selection?
See `E3_SCIENTIFIC_PROTOCOL.md`.

## 4. Reused Traffic Complete-aligned evidence

- Reusable runs: **100**
- Seeds: 30001..30020
- Methods: fedavg_window, fedasync_window, flamf_timealign_adapted, twostage_hajek, raven
- Registry hash: `7d9b8292522b6fbcc15d83ebb065fc8a73b79787ed643aea49c48f30596acbc7`

## 5. SensorScope readiness

Status: `NOT_READY_EVENTTRACE`
Blocker: No sealed PROFILE-style Complete-aligned EventTrace/formal harness for SensorScope comparable to Traffic PROFILE-S1

## 6. U-Air readiness

Status: `NOT_READY_TARGET_SUPPORT`
Blocker: Processed data exists but no frozen public-target/groups/profile/EventTrace formal harness

## 7. Traffic readiness

Status: `REUSE_EXISTING_E2_BLOCK`
Formal identity: 43 clients × 100 windows; reuse E2 Complete-aligned block.

## 8. Frozen E3 method registry

See `E3_METHOD_REGISTRY_AUDIT.csv`.

## 9. FLAMF-Original status

EXCLUDED_WITH_REASON — stub only; TimeAlign-Agg must not be renamed FLAMF-Original.

## 10. Metric availability

See `E3_METRIC_AVAILABILITY.csv`. Primary RMSE_mu available; MAE/Tail/Delta_* need emit/materialization rules.

## 11. Delta_pair / Delta_c-s readiness

`PAIR_METRIC_NOT_READY_BLOCK_E3_PAIR_CLAIMS` until runner materializes Pi_hat.

## 12. SimOracle readiness

Traffic: VALID_CONTROLLED_ORACLE (freeze MC count before formal). SensorScope/U-Air: NOT_AVAILABLE.

## 13. Primary statistical comparison freeze

See `E3_PRIMARY_COMPARISON_FREEZE.json` (RAVEN vs each main baseline; no post-hoc easiest baseline).

## 14. Formal seed and multiplicity freeze

Seeds 30001..30020; EPS_ZERO=1e-12; Holm families predeclared.

## 15. Minimum new-run matrix

- From-scratch estimate: 480
- Reusable: 100
- New runs needed (ready scope): 80
- Compute saved by reuse: 20.83%

## 16. Estimated compute cost of new runs

About 80 Traffic Complete-aligned trainings for missing methods (local_hajek/inst_cal/debt_cal/raven_simoracle × 20), excluding the sealed 100-run block.

## 17. Canary plan

`E3_CANARY_PLAN.md` — seed 31001; not executed this round.

## 18. Gate results

All E3P-G1..G18 **PASS**. See `gate_results.json` / `gate_diagnostics.json`.

## 19. Blocking issues

- SensorScope/U-Air lack sealed Complete-aligned formal harnesses
- Delta_pair claims blocked until pair-state materialization
- Central references blocked without runner
- FLAMF-Original not faithfully implemented

## 20. Exact next-step authorization

Authorized next round if gates pass:
**E3-REAL-RUNNER-CANARY-R1** on Traffic only, canary seed 31001, new methods only.
Do not expand to SensorScope/U-Air without teacher authorization for reduced/expanded dataset scope.
