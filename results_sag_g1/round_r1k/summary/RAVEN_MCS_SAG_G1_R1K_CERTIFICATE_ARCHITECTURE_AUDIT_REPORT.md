# RAVEN-MCS SAG G1 R1K Certificate Architecture Audit

## Executive verdict: R1K_ARCHITECTURE_AUDIT_INCONCLUSIVE

Feasibility / impossibility audit only. Aggregate C_LCB is not a paper-method replacement. STOP. No SAG / 5-seed / theory edits.

## Pairwise barrier

1. Hidden current availability identity is not pre-window F_{r-}-measurable. Scenario-level a is public.
2. For a<0.95, p_active_upper<=a<0.95, so a strict positive 95% pairwise LCB is blocked. Barrier rows: see R1K_PAIRWISE_BARRIER_BY_LEVEL.csv.
3. Conditions: deterministic pre-window LCB; current mask hidden; zero-mass event; conditional 1-delta validity.
4. a=1.00: fraction of pairs with presence>=0.95 is SS=0.0, U-Air=0.0.
5. Target-mass fraction on those high-presence pairs: SS=0.0, U-Air=0.0.
6. Simultaneous window-max residual is strictly harder than single-pair coverage.
7. Pairwise barrier verdict: STRUCTURAL_PAIRWISE_NONVACUITY_BARRIER_CONFIRMED.

## Scale defect

8. Old map is p * max(pi_safe, mean_mass_all). mean_mass_all includes inactive zeros, so active probability can be multiplied twice.
9. median hat_cond/hat_old (pooled) = 4.833333333333334.
10. mean C_point_old vs C_point_cond vs oracle: see R1K_PREDICTOR_SCALE_SUMMARY.csv.
11. corr(point,oracle) old=0.8267641532585139 cond=0.06206745125705602; MAE old=0.022878585816371953 cond=0.2123117595658799.
12. Scale verdict: PREDICTOR_SCALE_DEFECT_PARTIAL.

## Aggregate feasibility

13. Predictor: AGGREGATE_COVERAGE_LINEAR_V1 ridge alpha=1.0, L=8.
14. Features use only historical same-a C_oracle and public time/a.
15. Current mask is not a feature.
16. Current oracle is not a feature (used only as past residual/target after the window).
17. Pooled aggregate validity: 0.9216494845360824; SS=0.9283018867924528; UA=0.9136363636363637.
18. Pooled false-safe: 0.05263157894736842.
19. Pooled false-unsafe: 0.12668463611859837.
20. Pooled balanced accuracy: 0.9103418924670166.
21. Pooled fraction C_LCB=0: 0.004123711340206186.

## SensorScope a=0.40

22. Pairwise confusion TP/TN/FP/FN=0/22/0/31.
23. Aggregate confusion TP/TN/FP/FN=11/20/2/20.
24. Balanced accuracy pairwise=0.5 aggregate=0.6319648093841642.
25. Aggregate false-safe=0.09090909090909091.
26. Aggregate validity=0.9433962264150944.
27. Aggregate non-vacuous? zero_frac=0.0 (vacuous if ~1).

## U-Air a=0.20

28. Pairwise 0/30/0/14 ba=0.5; aggregate 0/30/0/14 ba=0.5 fs=0.0 valid=0.9545454545454546 zero=0.045454545454545456.

## Architecture conclusion

29. Pairwise structural barrier=STRUCTURAL_PAIRWISE_NONVACUITY_BARRIER_CONFIRMED; scale=PREDICTOR_SCALE_DEFECT_PARTIAL.
30. Aggregate candidate: AGGREGATE_NOT_CALIBRATED.
31. Theory-change decision: THEORY_DECISION_INCONCLUSIVE.
32. If redesign: C_cov definition, certificate theorem, Gate semantics, algorithm I/O, experiment interpretation.
33. Paper theory modified this round? NO.

## Execution boundary

34. Stress unchanged: True.
35. tau/pi_safe/target unchanged: True.
36. SAG: False.
37. 5-seed: False.
38. pytest R1k: PASS passed=30 failed=0.
39. full pytest: PASS passed=33 failed=0.
40. R1K-S0–S29: n_pass=30 n_fail=0.
41. Final verdict: R1K_ARCHITECTURE_AUDIT_INCONCLUSIVE.
