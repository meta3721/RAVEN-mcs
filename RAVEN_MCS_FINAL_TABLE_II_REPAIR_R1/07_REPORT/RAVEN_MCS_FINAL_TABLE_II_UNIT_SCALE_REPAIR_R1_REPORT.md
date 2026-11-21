# Table II unit/scale repair R1

Round: `RAVEN-MCS-FINAL-TABLE-II-UNIT-SCALE-CONSISTENCY-REPAIR-R1`

## 1. Executive decision

**Status A.** `RAVEN_MCS_TABLEII_REPAIR_R1_PASS_PAPER_SPEC_FINAL_SEALED`

Gates: 28/28. U-Air Table II prediction summaries rebuilt from frozen per-seed FIG-E3 evidence. SensorScope unchanged. Structural metrics unchanged. Statistics/Holm unchanged. **new experiments required = false.**

## 2. Zero-run attestation

No training, rerun, canary, T-Drive, new seed, dataset, or baseline. Metric definitions and Holm families unchanged. See `00_AUDIT/NO_NEW_EXPERIMENT_ATTESTATION.json`.

## 3. Original Table II inconsistency

U-Air RMSE_mu/Tail_RMSE in the prior Table II came from `E3_FINAL_STATISTICS` field `RMSE_mu_phys` / `Tail_RMSE_phys` (~20.x). Frozen per-seed FIG-E3 / Table III Full RAVEN use `RMSE_mu` / `Tail_RMSE` (~1.19). Ratio ≈ 17.36325122. SensorScope phys and per-seed scales already agreed.

## 4. U-Air scale audit

All U-Air Table II prediction fields classified `STALE_OR_WRONG_SCALE` against FIG-E3. FIG-E3 is byte-identical to freeze `E3_PREDICTION_METRICS_MASTER.csv`. No unresolved per-seed source conflict.

## 5. SensorScope control audit

All SensorScope prediction fields `MATCH_FINAL_SEED_SCALE`. SensorScope values were not altered.

## 6. Authoritative source selection

Per-seed E3 prediction evidence (FIG-E3 = freeze prediction master) outranks the stale `RMSE_mu_phys` summary. Structural values remain the frozen E3 structural summaries already in Table II / FIG-E2.

## 7. Rebuilt U-Air RMSE_mu

From 20 seeds 30001–30020, sample std (ddof=1). Checkpoints (not hard-coded): FedAvg mean=1.1882377206580421; TwoStage-Hajek mean=1.2159612028650515; RAVEN-MCS mean=1.191113924600986.

## 8. Rebuilt U-Air Tail_RMSE

FedAvg mean=1.1968390299611786; TwoStage-Hajek mean=1.2259670437620116; RAVEN-MCS mean=1.1998575601072905.

## 9. Structural metric preservation

U-Air and SensorScope Δ_group / Δ_{c,s} copied from the prior Table II after matching FIG-E2. Not recomputed from prediction rows.

## 10. Table II final reconstruction

`01_REBUILT_TABLE_II/TABLE_II_MAIN_EFFECTIVENESS_REPAIRED_R1.csv` SHA256 `826d1e7fac6f1a49f4166b51d7cc2af5029819f04fec18506591de287fb92184`. Method order preserved. Holm flags preserved. numerical_best recomputed from repaired means.

## 11. Table II vs Figure E3

Prediction mean/std EXACT_MATCH or ROUNDING_MATCH. No SCALE_MISMATCH.

## 12. Table II vs Figure E2

Structural EXACT_MATCH or ROUNDING_MATCH.

## 13. Table II vs Table III

Full RAVEN RMSE_mu, Tail_RMSE, Δ_group, Δ_{c,s} agree on SensorScope and U-Air.

## 14. Table II vs master evidence

Agrees with freeze `E3_PREDICTION_METRICS_MASTER.csv` (authoritative per-seed master). Stale `RMSE_mu_phys` is not used as paper-facing Table II.

## 15. Final statistical linkage

`02_STATISTICS_LINKAGE/TABLEII_FINAL_STATISTICAL_LINKAGE.csv` links each primary comparison to frozen Holm p_raw / p_holm. Tests not rerun.

## 16. Marker semantics

Bold = numerical best. Dagger = Holm-significant vs RAVEN. Independent marks.

## 17. Unit/scale registry

U-Air paper-facing prediction scale is FIG-E3 ~1.19. The old 20.x scale is forbidden in paper-facing Table II.

## 18. Superseded old Table II

`06_PROVENANCE/SUPERSEDED_TABLE_II/` classified `SUPERSEDED_SCALE_VERSION_MISMATCH`. Original specification-seal files were not overwritten.

## 19. Registry updates

Main table registry and figure-table registry now point at the repaired Table II hash. Table I and Table III scientific content unchanged.

## 20. Figure-count wording repair

5 main figures: framework + E2 risk non-interchangeability + E3 structural alignment + E3 prediction risk + E4 component ablation.

## 21. Section VI naming repair

Proposition 1; Proposition 2; Theorem 1; optimization program remains (P2). math_changed=false.

## 22. Frozen Paper Specification update

Only Table II path/hash, figure-count wording, and theorem naming were patched.

## 23. T-Drive status

PROTOCOL_SEALED, FORMAL_NOT_RUN, REVIEWER_RESERVE. Not run.

## 24. Quality gates

See `07_REPORT/T2R_GATES_R1.json`. 28/28.

## 25. Is the paper specification now safe to freeze?

Yes. Paper-facing Table II no longer mixes U-Air 20.x with 1.19.

## 26. Exact next action

WRITE SECTION III then IV then V then VI, then joint III–VI formula/symbol/logic audit.

STOP all data/experiment repair work. Do not activate T-Drive.

ZIP: `TO_SUBMIT_RAVEN_MCS_FINAL_TABLE_II_UNIT_SCALE_REPAIR_R1.zip` reopen-verify=PASS.
