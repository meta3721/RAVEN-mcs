# 1. Executive Verdict

TARGET_COMPATIBILITY_BUG_FIXED

R1c is a 1-seed target-compatibility + coverage-certificate repair (SensorScope 30001, U-Air 30001). Frozen `tau_*` were not changed. 5-seed was not started.

# 2. Target Compatibility

`varpi_tar` is uniform over train-split supported atoms (`build_frozen_atomic_target_law`).
`μ` is the paper-`h(i)` marginal of that law.
`π^{tar}` is the client×stratum pushforward of the same law with frozen `ξ_{k|i}=1{client(spatial_id)=k}`.

R1b source split: μ from train, `π^{tar}` from `build_pi_target(..., split="test")`. **BUG_CONFIRMED** then **FIXED**.

max compatibility error = 1.7208456881689926e-13 (atol=1e-10).

# 3. pi_safe Freeze

rule=PI_SAFE_RULE_V1; quantile=0.1; source=public_pi_opp_joint_on_target_positive_pairs;
excludes=['labels', 'test_outcomes', 'test_prediction_residuals', 'current_window_events', 'gate_ON_OFF'];
SensorScope=0.0006326708489355371; U-Air=0.0013918758676581813;
hash=aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7.

# 4. Old C_cov Failure Mechanism

Old estimator: empirical-Bernstein on per-window normalized pair masses, lookback ≤ 32.
Typical pair mass ≈ 0.125. For n=32, δ=0.05: `sqrt(2v log(1/δ)/n) + 3 log(1/δ)/n` exceeds the mean, so LCB clips to 0.
Old C_cov zero fraction (R1b vs this run) = 0.9888888888888889.

# 5. New Opportunity LCB

Event-count one-sided Clopper–Pearson on completed events `t<r` (all history, not 32 mass samples).
Assumption: completed opportunity events are exchangeable marks of the frozen EventTrace event-mark law.
Simultaneous correction: Bonferroni `δ_pair = delta_cal / m_{π^{tar}>0}`.
SensorScope max completed events = 3168.0.
U-Air max completed events = 2528.0.

# 6. C_cov Results

SensorScope: median=0.1899854156538676 p05=0.05035488575595587 p95=0.2984151677199849 frac>0=1.0 pass=0.89
U-Air: median=0.1916315049226454 p05=0.04950773558368525 p95=0.34957805907173073 frac>0=1.0 pass=0.875
New vs old zero fraction: old=0.9888888888888889 new=0.011111111111111112.
Calibration pairwise/target-mass/joint (SS mean): 0.7463181818181818 / 0.7435819154107942 / 0.0
U-Air calibration pairwise mean: 0.7405381944444445

# 7. A8b 95% Calibration

SensorScope: cover β=0.9479166666666666 M=1.0 V=0.9895833333333334 joint=0.9375 n=97
U-Air: cover β=0.9452054794520548 M=1.0 V=0.9863013698630136 joint=0.9315068493150684 n=74
A8B_CALIBRATION_NOT_YET_CLOSED

# 8. Gate Re-Diagnostic

Dataset | Ccov | Cret | CESS | Cclip | deltaA | Btot | ALL | ON
---|---|---|---|---|---|---|---|---
SensorScope | 0.89 | 0.92 | 0.92 | 0.92 | 0.92 | 0.92 | 0.89 | 0.89
U-Air | 0.875 | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 | 0.875 | 0.875

SensorScope first-fail: {'ON': 89, 'OFF_COLD_START': 8, 'OFF_LOW_COVERAGE': 3}
U-Air first-fail: {'ON': 70, 'OFF_COLD_START': 8, 'OFF_LOW_COVERAGE': 2}

# 9. Scientific Interpretation

SensorScope legal ON windows: 89 / 100.
U-Air legal ON windows: 70 / 80.
U-Air delta_A pass rate: 0.9.

C_cov is no longer the unique all-zero blocker. After the train-split unified `π^{tar}` and event-count CP LCB, both datasets produce legal ALL-pass windows. U-Air is **not** mainly intercepted by the active-set-risk certificate in this 1-seed diagnostic, so the intended SS-vs-U-Air Gate discrimination is not yet established.

# 10. Next Decision

Verdict TARGET_COMPATIBILITY_BUG_FIXED. Do not auto-start 5-seed.
READY_FOR_G1_R2_5SEED requires SensorScope legal ON **and** U-Air support-unsafe windows still mostly OFF. The second clause is not met.
