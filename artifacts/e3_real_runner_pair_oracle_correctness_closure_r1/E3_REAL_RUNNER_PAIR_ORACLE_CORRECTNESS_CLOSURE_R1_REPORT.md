# E3 Real Runner Pair/Oracle Correctness Closure R1 Report

## 1. Executive decision
**READY_FOR_E3_MULTIDATASET_REAL_RUNNER_CANARY**

## 2. No-performance-experiment attestation
No formal E3 20-seed runs and no performance Canary were executed. Debug smoke seed=31999 only.

## 3. Parent evidence integrity
E2 sealed=True; registry hash match=True; Traffic reuse guard active=True.

## 4. Real federated runner integration
Production path: `run_e3_real` → `build_full_runner` / `FullWindowRunner`.

## 5. Method-specific execution audit
all_real_path=True (see E3_REAL_METHOD_SMOKE_AUDIT.*).

## 6. Exact Delta_pair definition
Client×atomic method-dependent Pi_hat; toy exactness A/B=True/True.

## 7. Pair-state implementation
Schema E3_PAIR_STATE_SCHEMA_V3; runner emits pair_state.parquet + delta_pair_summary.json.

## 8. Atomic p_obs truth
Materialized in atomic_p_obs_true.parquet; mean not used for Oracle atomic weights.

## 9. Joint pi_opp probability scale
sum_pi_opp_joint=1.0000000000000002; sum_pi_tar=1.0.

## 10. Staleness correction
Design P(age>S_max)≈0.20; diagnostic empirical rate=0.0625.

## 11. SimOracle fixed-prestate M_MC=2000
Implemented in simoracle_q.estimate_q_true_mc; M_MC_CHECK=10000.

## 12–13. Central real-data
Central-All uses frozen train IDs; Central-Delivered uses exact EventTrace U=1 train units (no Bernoulli).

## 14. Head/Tail final definition
EXACT_FROZEN_DEFINITION_RECOVERED: time_block in {0,1}=Head; {2,3}=Tail (protocol spatial×time groups; not performance)

## 15. q_hat path
Legal online estimator separated from SimOracle q_true (see audit).

## 16. P2/debt/calibration outputs
Emitted from FullWindowRunner for inst_cal/debt_cal/raven/raven_simoracle.

## 17. Real metric computation
Schema V3; smoke placeholder_fields empty for all methods.

## 18. End-to-end correctness smoke
status=PASS

## 19–20. Readiness R3
See E3_METHOD_READINESS_R3.* and E3_DATASET_READINESS_R3.*.

## 21. Minimum new-run matrix R3
total_new=560; reused Traffic=100.

## 22. Final Canary plan
Prepared, not executed (seed=31001).

## 23. Tests
unit_rc=0; full_rc=0; pip_rc=0

## 24. Gates
See check_e3_real_runner_pair_oracle_correctness_closure_gates.py

## 25. Hashes
See E3_REAL_RUNNER_CORRECTNESS_SOURCE_HASHES.json / HASH_MANIFEST.

## 26. Remaining blockers
None

## 27. Exact authorization for next round
Authorize E3-MULTIDATASET-REAL-RUNNER-CANARY-R1
