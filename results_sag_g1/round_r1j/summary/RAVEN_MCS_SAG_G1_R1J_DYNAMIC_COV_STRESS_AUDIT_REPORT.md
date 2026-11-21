# RAVEN-MCS SAG G1 R1J Dynamic C_cov Stress Audit

## Executive verdict: R1J_CERTIFICATE_TOO_CONSERVATIVE

Natural E3-v2 and R1i oracle remain frozen. This round is an out-of-sample certificate audit, not predictor tuning.

STOP. No SAG / 5-seed.

## Answers

1. R1i oracle unchanged: sha256 `82444e4f495344856de94b0d72ab4a46843780c232e2f299b300fcafa8c4b4a1`.
2. Stress grid unchanged: [1.0, 0.8, 0.6, 0.4, 0.2].
3. Masks unchanged: `b87cf615ab34b447e87bf447d79b9e4183a6e16fcef6223c57fad7be4aec6502`.
4. TARGET_LAW unchanged: True.
5. PI_SAFE unchanged: `aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7`.
6. tau_cov=0.05: True.
7. delta_cal=0.05: True.
8. Predictor: `CONTEXT_AVAILABILITY_PRESENCE_V1` L2 logistic C=1.
9. Features: ['log1p_hist_active_count', 'lag1_active', 'lag2_active', 'rolling_active_rate_L8', 'rolling_pi_opp_mean_L8', 'rolling_pi_opp_trend_L8', 'hour_of_day_unit', 'weekend_flag', 'availability_level', 'rolling_active_rate_times_a'].
10. Lookback L=8.
11. Current mask not a feature.
12. Current R/O/U not features.
13. Oracle labels not used in training (evaluation only).
14. Future windows not in calibration (same-a residuals from t<r).
15. Pooled joint validity (eligible): 1.0.
16. SensorScope joint validity: 1.0.
17. U-Air joint validity: 1.0.
18. Joint by a: see R1J_GATE_METRICS.csv.
19. Pooled fraction C_cov=0: 1.0.
20. SensorScope a=0.4 fraction C_cov=0: 1.0.
21. U-Air a=0.2 fraction C_cov=0: 1.0.
22. R1d zero fractions were 0.976 / 1.0; R1j is reported above.
23. Pooled false-safe: 0.0.
24. SensorScope false-safe: 0.0.
25. U-Air false-safe: 0.0.
26. Boundary-near false-safe: 0.0.
27. Pooled false-unsafe: 1.0.
28. Pooled balanced accuracy: 0.5.
29. Median gap SS=0.0802139037433155 (see metrics); SS a=0.4 median gap=0.0536703937773456; U-Air a=0.2=0.040506329113924.
30. Over-conservative if C_cov near 0 while oracle crosses tau.
31. SS a=0.4 TP/TN/FP/FN=0/22/0/31.
32. SS a=0.4 false-safe=0.0.
33. SS a=0.4 false-unsafe=1.0.
34. SS a=0.4 balanced acc=0.5.
35. SS a=0.4 joint=1.0.
36. SensorScope usable? NO_DISCRIMINATION.
37. U-Air a=0.2 TP/TN/FP/FN=0/30/0/14.
38. U-Air a=0.2 false-safe=0.0.
39. U-Air a=0.2 false-unsafe=1.0.
40. U-Air a=0.2 balanced acc=0.5.
41. U-Air a=0.2 joint=1.0.
42. U-Air dataset verdict: NO_DISCRIMINATION.
43. q vs prediction scale: see R1J_Q_SCALE_AUDIT.csv (R1d was q >> hat).
44. median q/pi_safe eligible=33.89037876637798.
45. Mass lower-bound zeros: SS a=0.4 1.0; U-Air a=0.2 1.0.
46. Post-hoc predictor retune: False.
47. Post-hoc calibration retune: False.
48. Stress unchanged: True.
49. SAG: False.
50. 5-seed: False.
51. pytest R1j: PASS passed=31 failed=0.
52. full pytest: PASS passed=34 failed=0.
53. R1J-S0–S28: n_pass=29 n_fail=0.
54. Final verdict: R1J_CERTIFICATE_TOO_CONSERVATIVE.
