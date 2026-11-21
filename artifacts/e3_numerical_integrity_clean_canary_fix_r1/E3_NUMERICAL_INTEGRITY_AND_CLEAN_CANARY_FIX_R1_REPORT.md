# E3_NUMERICAL_INTEGRITY_AND_CLEAN_CANARY_FIX_R1_REPORT

## 1. Executive decision
**READY_FOR_E3_FORMAL_RUNS**

## 2. No-new-experiment attestation
No datasets/methods/metrics/seeds added. Canary seed remains 31001. Formal seeds not executed.

## 3. First Canary numerical failure summary
U-Air federated NaN/extreme; Traffic measurement/index scale mismatch; NaN accepted by broken gate; mixed source revisions.

## 4. Exact root cause
See `E3_NUMERICAL_ROOT_CAUSE_REPORT.md` (preprocessing feature mismatch, unit-scale/z-score measurement sync, acceptance `is not None`, provenance).

## 5–8. Audits
Scale/feature/local/aggregation/prediction audits are under this artifact directory.

## 9. Exact correctness fix
- eval uses `extract_features`
- train z-score + measurement index rebuild for U-Air/Traffic
- nonfinite hard-fail + finite acceptance
- source freeze binding in Ledger START

## 10. NaN/Inf acceptance-gate fix
Applicable metrics require `isfinite`.

## 11. Source-revision freeze
`b01db69e8554a33446c438c060ac464dcfadac24`

## 12–14. Prechecks / Phase1 / Phase2
Pre-clean regressions PASS required before freeze. Clean Canary accepted=28/28.

## 15. Traffic sealed-run protection
Sealed five methods not scheduled/rerun under clean art.

## 16–18. Metric finiteness / Ledger / before-after
clean nan=0 inf=0; ledger=PASS

## 19–20. Tests / Gates
test_returncodes={'targeted': 0, 'integ': 0, 'full': 0, 'pip': 0}

## 21. Formal readiness
READY_FOR_E3_FORMAL_RUNS

## 22. Exact next-round authorization
Authorize E3 formal matrix 30001-30020 (do not execute in this round).
