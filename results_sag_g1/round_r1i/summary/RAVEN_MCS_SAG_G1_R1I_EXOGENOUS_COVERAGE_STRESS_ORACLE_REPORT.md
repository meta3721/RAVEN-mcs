# RAVEN-MCS SAG G1 R1I Exogenous Coverage-Stress Oracle

## Executive verdict: READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT

Natural E3-v2 remains the deployment-realism track. Controlled availability stress is a separate mechanism-validation track. Stress results do not replace natural results.

STOP. No dynamic certificate / SAG / 5-seed.

## Answers

1. Natural E3-v2 unchanged: identity hashes match freeze; R1i writes only round_r1i.
2. TARGET_LAW hash unchanged: True (`86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07`).
3. PI_SAFE hash unchanged: `aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7`.
4. tau_cov still 0.05: True.
5. Stress grid frozen as [1.0, 0.8, 0.6, 0.4, 0.2].
6. Levels/mask/routing frozen before oracle stress computation.
7. Mask is deterministic nested SHA256 unit-interval.
8. Mask is outcome-independent (no oracle/Gate/target-weight fields).
9. Stress is entity-level (spatial_id); all records of an unavailable entity are dropped.
10. a=1.00 reproduces natural: True.
11. max reproduction diff: 8.326672684688674e-17.
12. entity counts match at a=1.00: True.
13. C_real_support monotone in a: True.
14. C_oracle_safe monotone in a: True.
15. monotonicity violation count: 0.
16. SensorScope fraction_safe by a: {0.2: 0.0, 0.4: 0.5, 0.6: 0.9354838709677419, 0.8: 1.0, 1.0: 1.0}.
17. SensorScope BOUNDARY_RICH levels: [0.4].
18. SensorScope MILD_SAFE_EXISTS: True.
19. SensorScope SEVERE_UNSAFE_EXISTS: True.
20. SensorScope crossing windows: 62.
21. SensorScope boundary-near rows: 44.
22. SensorScope dataset verdict: BOUNDARY_USABLE.
23. U-Air fraction_safe by a: {0.2: 0.2830188679245283, 0.4: 0.9056603773584906, 0.6: 0.9056603773584906, 0.8: 0.9056603773584906, 1.0: 0.9056603773584906}.
24. U-Air BOUNDARY_RICH levels: [0.2].
25. U-Air MILD_SAFE_EXISTS: True.
26. U-Air SEVERE_UNSAFE_EXISTS: False.
27. U-Air crossing windows: 33.
28. U-Air boundary-near rows: 27.
29. U-Air dataset verdict: BOUNDARY_PARTIALLY_USABLE.
30. Stable safe→unsafe transition: SS=True U-Air=True.
31. At least one BOUNDARY_RICH dataset: True.
32. Both datasets BOUNDARY_USABLE: False.
33. all-safe/all-unsafe failure: SS all_safe=False all_unsafe=False; U-Air all_safe=False all_unsafe=False.
34. Need to add stress levels this round? **No. This round forbids adding midpoints.**
35. Allow next-round dynamic certificate stress audit? True (verdict=READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT).
36. predictor run: False.
37. calibration run: False.
38. dynamic C_cov: False.
39. SAG: False.
40. 5-seed: False.
41. pytest R1i: PASS passed=25 failed=0.
42. full pytest: PASS passed=28 failed=0.
43. R1I-S0–S24 artifact-derived: n_pass=25 n_fail=0.
44. Final verdict: READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT.
