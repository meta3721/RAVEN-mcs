# E4 Ablation Semantic Integrity Repair R1 Report

## 1. Executive decision
`E4_CORE_MECHANISM_ABLATION_SEMANTICALLY_REPAIRED_AND_SEALED`

Task A: `E4_FULLMODE_EQUIVALENT_TO_E3_RAVEN`
Task B: `WO_INST_EXISTING_40_RUNS_INVALID_TARGETED_RERUN_REQUIRED` (40 corrective Inst reruns)
Task C: `WO_DESIGN_ACTIVE_SET_DIFFERENCE_IS_VALID_WEIGHT_SUPPORT_EFFECT` (no Design rerun)

## 2. No-scope-expansion attestation
No new datasets/baselines/metrics/seeds/scenarios; no E5; no retuning; Obs/Use/Debt/full RAVEN never rerun.

## 3. Parent E4 evidence preservation
Parent `artifacts/e4_core_mechanism_ablation_r1` raw runs retained. Invalid Inst runs marked superseded, not deleted.

## 4. E3-vs-E4 source diff
See `E4_E3_VS_E4_FULLMODE_SOURCE_DIFF.md`. Ablation plumbing differs; full-mode RAVEN path remains equivalent.

## 5. Full-mode equivalence result
`E4_FULLMODE_EQUIVALENT_TO_E3_RAVEN`. Keep 40 E3 RAVEN references; do not rerun them.

## 6. w/o-Inst observed P2 disappearance
All 40 parent Inst runs had `P2_invoked=false`.

## 7. w/o-Inst control-flow root cause
`uses_instant_calibration=False` branched to `alpha=beta` and skipped `compute_server_weights` — accidental coupling, not frozen theory.

## 8. w/o-Inst one-factor test
See `E4_WO_INST_ONE_FACTOR_REGRESSION.json`.

## 9. w/o-Inst repair
Always invoke aggregator; `RavenWoInstAggregator` runs P2 with λ_g=0 and λ_β=1e-8 uniqueness, keeping debt/variance/staleness.

## 10. w/o-Inst corrective rerun
40/40 accepted under `corrective_runs/`; all show `P2_invoked=true`.

## 11. U-Air w/o-Design active-set anomaly
Parent audit noted differing active-client memberships vs other ablations.

## 12. Active-set layer decomposition
See `E4_WO_DESIGN_ACTIVE_SET_LAYER_AUDIT.csv` / active-set summaries.

## 13. Design difference causal explanation
Valid weight-support effect from design-ratio zeroing (`zeta=ones` expands positive-mass support). Unexplained=0.

## 14. w/o-Design repair
Not required.

## 15. w/o-Design corrective rerun
0 runs.

## 16. Minimal rerun count
40 (Inst only).

## 17. Superseded evidence provenance
`E4_SUPERSEDED_RUN_PROVENANCE.csv`.

## 18. Final 240-record evidence index
`E4_FINAL_VALID_EVIDENCE_INDEX.csv` has 240 cells.

## 19. Updated Delta_group results
See `E4_ABLATION_PAIRED_TESTS_R2.csv` (Inst uses corrected runs).

## 20. Updated Delta_c_s results
Same paired-tests R2 artifact.

## 21. Updated RMSE_mu results
Same paired-tests R2 artifact (secondary).

## 22. Updated Tail_RMSE results
Same paired-tests R2 artifact (secondary).

## 23. Final component claim matrix
{
  "Debt": "STRUCTURAL_ONLY_SUPPORTED",
  "Design": "ENDPOINT_TRADEOFF",
  "Inst": "STRUCTURAL_ONLY_SUPPORTED",
  "Obs": "ENDPOINT_TRADEOFF",
  "Use": "NO_CLEAR_EFFECT"
}

## 24. Effect-size interpretation
Debt remains statistically consistent but quantitatively small. Design/Obs are endpoint tradeoffs, not universal necessity. Inst structural-only after correction. Use: no clear effect.

## 25. Whether E5 is truly needed
Not auto-launched. Decision: `E4_SEMANTICALLY_SEALED_STOP_EXPERIMENTS_AND_WRITE`.

## 26. Exact next action
Stop additional E4 compute. Use R2 sealed claims for manuscript. Do not start E5 from this round.
