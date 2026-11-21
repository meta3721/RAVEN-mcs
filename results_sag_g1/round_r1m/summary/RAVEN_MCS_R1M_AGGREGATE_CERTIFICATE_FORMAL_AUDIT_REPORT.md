# RAVEN-MCS R1m aggregate certificate formal audit

**Executive verdict:** `R1M_CERTIFICATE_TOO_CONSERVATIVE`

This round implements the first formal aggregate coverage certificate under frozen R1l theory.
Empirical validity is an audit of realized certificates. It does **not** prove Assumption A or exchangeability.
Theorem 1 remains conditional on Assumption A. RESET is an operational abstention rule and does not protect the first unseen shift window.

## Freeze

1. target law unchanged: `86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07` (expected `86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07`).
2. pi_safe rule hash: `aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7`.
3. tau_cov = 0.05.
4. alpha = 0.05.
5. n_min = 19.
6. stress grid = [1.0, 0.8, 0.6, 0.4, 0.2].
7. canonical method = `raven_mcs` → `aggregate_coverage`.

## Predictor

8. `AGGREGATE_COVERAGE_RIDGE_V1`.
9. ridge_alpha = 1.0 (not scanned).
10. features: ['intercept', 'availability_level', 'lag1_C', 'lag2_C', 'rolling_mean_C_L8', 'rolling_trend_C_L8', 'hour_sin', 'hour_cos', 'weekend_flag'].
11. first-block fit uses E3-v2 train-split windows under the same R1i stress mechanism; test labels are not used to warm-start f_0.
12. snapshot frozen within block: True.
13. refit only after RESET, on data completed through the trigger window.

## Calibration

14. S_t = C_hat_t - C_t.
15. current window is not in its own q_t.
16. tracks do not mix availability levels.
17. tracks do not mix blocks.
18. n < 19 → WARMUP, C_LCB=0, Gate OFF, Design OFF.
19. k_n is never clipped to n.

## RESET

20. `MISCOVERAGE_TRIGGERED_RESET_V1`.
21. trigger only after a completed CERTIFIED miscoverage (C_LCB > C_t + tol).
22. the violating window stays CERTIFIED.
23. the next window is RESET (Gate OFF) then new-block WARMUP.
24. second detector: **NO**.

## Pooled (CERTIFIED unless noted)

25. certified windows = 243 / 575.
26. validity_rate = 0.9588477366255144.
27. miscoverage_count = 10.
28. false-safe count = 0; FSR_unsafe = 0.0; FSR_all = 0.0.
29. false-unsafe rate (certified) = 0.2553191489361702.
30. balanced_accuracy = 0.8723404255319149.
31. certified_duty_cycle = 0.4226086956521739.
32. fraction_C_LCB_zero = 0.01646090534979424.
33. Design ON count (certified) = 140.
34. reset_count = 10; blocks = 3.

## Primary (SensorScope a=0.40)

PRIMARY_USABLE = False.
certified=24, duty=0.3870967741935484, validity=0.9583333333333334,
FSR_unsafe=0.0, BA=0.5, zero=0.0, DesignON=0.

## Secondary (U-Air a=0.20)

SECONDARY_SAFE = True.
certified=34, validity=1.0, FSR_unsafe=0.0, BA=0.5.

## Routing

SAG was not started. 5-seed was not started. Even a READY_FOR_SAG_* verdict must STOP this round.

Git: `a7f02f08cba2c7038d60d41d24042fbc57c402fd`.
