# E3 Numerical Root-Cause Report

Classification: **CORRECTNESS_ONLY_NOT_PERFORMANCE_TUNING**

## Exact root causes

### A. PREPROCESSING_CONSISTENCY_FIX
Federated `ClientTrainer` trains with `extract_features` (`trend = time_index / total_slots`).
Eval `_predict` previously used raw `time_index` and `weekday=0`. Central training matched the broken eval path.
**Effect:** U-Air/Traffic predictions exploded; SensorScope (smaller temperature scale) remained finite.

### B. UNIT_SCALE_FIX / PREPROCESSING_CONSISTENCY_FIX
1. **Traffic:** train z-score applied to frames but `_measurement_index` stayed on raw speeds → train on raw, metrics on z-score.
2. **U-Air:** raw PM2.5 (~1–210) with frozen `lr=0.01` exploded by windows 3–4 → NaN.
**Fix:** `apply_train_zscore_standardization` rebuilds measurement index; apply to Traffic and U-Air. Metrics stay on the same train-zscore scale (no inverse needed).

### C. ACCEPTANCE_GATE_FIX
`RMSE_mu is not None` accepted `NaN`. Fixed with `math.isfinite` / `is_finite_number` hard reject.

### D. NONFINITE_PROPAGATION_FIX
Local updates that become nonfinite now raise `NONFINITE_NUMERICAL_STATE` instead of silent zeroing.
Runner refuses to finish with nonfinite required metrics.

### E. SOURCE_PROVENANCE_FIX
First Canary changed code mid-matrix. Clean Canary requires `E3_CLEAN_CANARY_SOURCE_FREEZE.json` and Ledger START binds `git_commit` + `source_manifest_hash`.

## Why SensorScope stayed stable
Temperature targets are O(10) and were already on a scale compatible with frozen LR; feature mismatch hurt less before overflow.

## Why U-Air/Traffic exploded
Larger raw magnitudes + feature mismatch + (Traffic) train/eval scale desync.

## Proof not performance tuning
LR, local_steps, horizons, seeds, methods, q/P2 unchanged. Only wiring/scale consistency and finite gates.
