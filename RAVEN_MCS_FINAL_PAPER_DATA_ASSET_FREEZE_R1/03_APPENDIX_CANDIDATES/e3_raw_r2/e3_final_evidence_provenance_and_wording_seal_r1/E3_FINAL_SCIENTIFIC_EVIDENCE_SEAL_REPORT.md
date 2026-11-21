# E3 final scientific evidence seal report

## Teacher answers (do not bury)

1. Is Local-Hajek safe to keep as an inferential baseline? **YES.** Provenance is certified; keep it in the main same-backbone inferential family. Formal collapse to FedAvg is a uniform-weight protocol/data degeneracy, not wiring failure.
2. Are P2 warning-affected allocations feasibility-certified? **YES.**
3. Is exact P2 optimality reconstructable? **NO.**
4. Final C1–C5 statuses:
   - C1 `PARTIALLY_SUPPORTED`
   - C2 `PARTIALLY_SUPPORTED`
   - C3 `SUPPORTED` (SensorScope + U-Air only)
   - C4 `NOT_TESTABLE_AS_PERFORMANCE_CLAIM` / controlled reference
   - C5 `SUPPORTED` (context/reference)
5. Are any new experiments scientifically necessary? **NO.**
6. Can E3 experimentation stop now? **YES.**

## 1. Executive decision
Status: `E3_SCIENTIFIC_EVIDENCE_FINAL_SEALED_STOP_EXPERIMENTS`.

This round is offline only. It does not train, rerun, retune, or add datasets/baselines/seeds/metrics. It seals provenance and wording for already-completed E3 evidence.

## 2. Scope and no-new-experiment attestation
Absolute prohibitions observed: no training; no formal rerun; no Traffic 100 sealed rerun; no Local-Hajek/P2 training rerun; no model/optimizer/q/P2/debt/h(i)/s(i)/EventTrace changes; no new robustness/sensitivity/scalability experiments; no invented claims.

## 3. Parent evidence inventory
Preserved parent evidence includes E1-R2; E2 Traffic sealed; E3 560 new formal runs + 100 reused Traffic records; raw-results seal; Traffic cross-vintage NOT_COMPARABLE policy; secondary statistics; Delta_group / Delta_c_s / Tail_RMSE; Local-Hajek 9,666-window audit; P2 778-warning inventory and 6,438-window feasibility audit.

## 4. Raw E3 run integrity
Formal raw seal and source freeze remain immutable references under `artifacts/e3_formal_runs_r1/`. Parent immutability audit records before/after hashes as unchanged.

## 5. Traffic reuse policy
The 100 sealed Traffic records remain reuse-only evidence. They are never rewritten by this seal.

## 6. Traffic cross-vintage comparability
Cross-vintage Traffic RMSE_mu inference remains `NOT_COMPARABLE` / `NOT_TESTABLE` for new-vs-old superiority claims. Traffic may appear descriptively, not as a third scientifically comparable structural block for C3.

## 7. Local-Hajek checkpoint anomaly
Accepted Local-Hajek checkpoints are identical to FedAvg for all SensorScope/U-Air formal seeds (CASE A). This is the anomaly that required weight provenance, not a silent wiring failure.

## 8. 9666-window formal-weight evidence
Parent forensic audit reconstructed every effective Local-Hajek client-window with `n>=2` on SensorScope/U-Air: 9,666 windows, all uniform under `EPS_WEIGHT=1e-12`, max weight range 0. Source label: `EVENTTRACE_DETERMINISTIC_REPLAY_ZERO_UPDATE`.

## 9. Local-Hajek replay provenance
This seal binds all 40 formal Local-Hajek runs to immutable input identities (EventTrace/config/target/stratum and documented proxies). Dependency proof shows `a_bar` is MODEL_INDEPENDENT. Formal/replay equivalence is certified against frozen `window_runner.py` hash `f7bff5e30c76898f5ab3e3998021f9b09e52ccf73f135b44bc4e141d9e13c436`.

## 10. Local-Hajek final inference policy
Decision: `LOCAL_HAJEK_FORMAL_COLLAPSE_PROVENANCE_CERTIFIED`.

Policy: `KEEP_LOCAL_HAJEK_IN_MAIN_SAME_BACKBONE_INFERENTIAL_FAMILY`.

Interpretation: Local-Hajek remains scientifically valid as a same-backbone baseline; on these formal datasets/protocol states it collapses to FedAvg because applied local weights are uniform.

## 11. P2 warning inventory
Recovered inventory: 778 `Solution may be inaccurate` warnings on P2 methods across stage logs.

## 12. 85 affected formal runs
Those warnings map to 85 distinct formal (dataset, method, seed) runs. Window IDs are not present on warning lines; audits therefore recover all active windows of each affected run.

## 13. 6438-window feasibility certificate
All 6,438 recovered active-window returned alpha vectors pass reconstructable frozen feasibility residuals within tolerance (~1e-7 hard gate; max observed residual about 2.686e-8 in parent audit).

## 14. Feasibility vs optimality distinction
LEVEL 1 `P2_FEASIBILITY_CERTIFIED` is supported.

LEVEL 2 `P2_OPTIMALITY_CERTIFIED` is not supported.

LEVEL 3 `P2_OPTIMALITY_NOT_RECONSTRUCTABLE` applies because native solver status and complete objective/input state were not persisted.

## 15. Corrected P2 Gate semantics
- `E3FS-G_P2_FEASIBILITY = PASS`
- `E3FS-G_P2_OPTIMALITY = NOT_TESTABLE_FROM_SEALED_OUTPUTS` (must not be labeled PASS)

Final P2 decision R2:
`P2_INACCURATE_WINDOWS_FEASIBILITY_CERTIFIED_OPTIMALITY_NOT_RECONSTRUCTABLE`

## 16. C1 RMSE_mu conclusion
`PARTIALLY_SUPPORTED`: competitive overall, selective gains, no universal superiority; Traffic cross-vintage inference excluded where invalid.

## 17. C2 Tail conclusion
`PARTIALLY_SUPPORTED` within valid same-vintage families only.

## 18. C3 structural mismatch conclusion
`SUPPORTED` only for SensorScope and U-Air scientifically comparable blocks. Traffic is not a valid third inferential block for cross-vintage structural comparison.

## 19. C4 SimOracle context
`NOT_TESTABLE_AS_PERFORMANCE_CLAIM`. SimOracle is a controlled reference isolating estimated vs observed selection/usability probabilities, not a peer superiority baseline.

## 20. C5 Central context
`SUPPORTED` as context/reference evidence only.

## 21. Final paper mainline
Two-stage non-random selection → deployment-target mismatch → RAVEN opportunity/observation/usable-update correction with calibration/debt → strong structural mismatch reduction on comparable blocks → competitive prediction risk with selective gains. Tail partial; Traffic descriptive where not comparable; P2 feasibility certified / optimality not reconstructable.

## 22. Limitations
- Formal Local-Hajek weights were not persisted at training time; provenance relies on model-independent reconstruction + input-identity binding.
- P2 native solver/full objective state was not persisted; optimality cannot be reconstructed offline.
- Traffic cross-vintage inferential comparisons remain invalid.
- No universal RMSE superiority is claimed.

## 23. Whether any experiment is still required
No. No integrity failure invalidates evidence essential to the paper mainline. No minimal corrective rerun is required for publication of the sealed mainline.

## 24. Exact next action
STOP E3 EXPERIMENTS.

Proceed to:
- final paper tables
- final paper figures
- Results section
- Discussion / Limitations
- manuscript integration
