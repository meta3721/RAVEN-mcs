# E4-WO-INST-REFERENCE-PENALTY-FINAL-CORRECTION-R1 Report

## 1. Executive decision
- Branch: `B` / `CURRENT_40_WO_INST_RUNS_INVALID_REFERENCE_PENALTY_MISMATCH`
- Recovered E3 λ_β: `1.0`
- Design decision: `WO_DESIGN_VALID_WEIGHT_SUPPORT_EFFECT_CONFIRMED`
- E4→E5: `E4_SEALED_STOP_EXPERIMENTS_AND_WRITE`

## 2. No-scope-expansion attestation
- No Traffic / new datasets / baselines / metrics / seeds / E5.

## 3. E3 full-RAVEN λ_β recovery
- recovered rows: 40 / 40
- evidence path: `artifacts/e4_wo_inst_reference_penalty_final_correction_r1/recovered_source/methods.py`
- evidence hash: `0729a2d8435f6a81dec1b9724b9d01809d76c435e34a23ea704945baf6cf615d`

## 4. Per-seed λ_β consistency
- See `E4_E3_LAMBDA_BETA_CONSISTENCY_AUDIT.json`.

## 5. Full P2 parameter identity
- See `E4_E3_FULL_RAVEN_P2_PARAMETER_IDENTITY.json`.

## 6. Existing corrected w/o-Inst parameter audit
- Gen1 used λ_β=1e-8 (mismatch vs E3=1.0) → Branch B.

## 7. One-factor w/o-Inst specification
- Keep matched E3 λ_β/λ_v/λ_s; only λ_g=0 + instant_calibration=False.

## 8. Branch A/B/C decision
- `CURRENT_40_WO_INST_RUNS_INVALID_REFERENCE_PENALTY_MISMATCH` (authorized runs=40)

## 9. w/o-Inst final regression
- See `E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json`.

## 10. Corrective source freeze
- See `E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json` (Branch B).

## 11. Corrective 40-run execution
- accepted: 40 / 40
- seal: `SEALED`

## 12. Superseded w/o-Inst provenance
- Gen0 INVALID_P2_OFF; Gen1 SUPERSEDED_REFERENCE_PENALTY_MISMATCH; Gen2 FINAL_VALID_ONE_FACTOR.

## 13. P2 state persistence
- Final runs persist `p2_invocation_states.json` with full lambdas/residuals.

## 14. U-Air 774-window Design layer audit
- rows: 774
- counts: {"aggregation_set_diff": 774, "observed_diff": 0, "opportunity_diff": 0, "p2_candidate_diff": 774, "positive_design_weight_diff": 774, "positive_final_weight_diff": 774, "registered_diff": 0, "scope_leakage": 0, "unresolved": 0, "usable_diff": 0, "valid_weight_support_effect": 774}

## 15. Design causal classification
- Physical EventTrace layers identical; first difference at weight-support / aggregation.

## 16. Design final decision
- `WO_DESIGN_VALID_WEIGHT_SUPPORT_EFFECT_CONFIRMED`

## 17. Final 240-cell evidence index
- `E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv`

## 18. Updated Inst statistics
- `E4_INST_FINAL_STATS.csv` (FULL RAVEN vs Gen2 wo_inst only).

## 19. Final component claim matrix
- **Debt**: `STRUCTURAL_ONLY_SUPPORTED` — Debt shows a small structural effect without robust prediction degradation.
- **Design**: `ENDPOINT_TRADEOFF` — Design shows mixed structural directions across endpoints/datasets (endpoint tradeoff).
- **Inst**: `STRUCTURAL_ONLY_SUPPORTED` — Under true one-factor w/o-Inst semantics (matched E3 λ_β), Inst shows structural mismatch contribution without robust prediction degradation.
- **Obs**: `ENDPOINT_TRADEOFF` — Obs shows mixed structural directions across endpoints/datasets (endpoint tradeoff).
- **Use**: `NO_CLEAR_EFFECT` — Use shows no clear sealed E4 effect under the pre-registered Holm families.

## 20. Final mechanism synthesis
- See `E4_CORE_MECHANISM_SYNTHESIS_FINAL_R3.md`.

## 21. Whether E5 is truly needed
- `E4_SEALED_STOP_EXPERIMENTS_AND_WRITE` (e5_started=false)

## 22. Exact next action
- Stop experiments and write the paper using sealed E4 evidence.

## Gates
- pass_count: 30 / 30
- all_pass: True
- failed: []
