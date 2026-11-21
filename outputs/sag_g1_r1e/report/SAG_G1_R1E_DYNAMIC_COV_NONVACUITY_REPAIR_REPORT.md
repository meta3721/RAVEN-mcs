# SAG G1-R1e Dynamic C_cov Non-Vacuity Repair Report

## 1. Executive verdict

NO_LEGAL_PREWINDOW_CONTEXT_FOR_R1E

This is a 1-seed development audit. It is not a 5-seed validation and does not claim a theoretical 95% simultaneous coverage proof.

## 2. Answers

1. R1d executive verdict: DYNAMIC_COV_TOO_CONSERVATIVE.
2. R1d input hashes frozen: yes. See provenance/R1D_INPUT_SHA256SUMS.txt.
3. TARGET_LAW_RULE_V1 hash match: True (`86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07`).
4. threshold JSON match: True.
5. pi_safe frozen as PI_SAFE_RULE_V1 q10: yes. rule_hash=aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7.
6. SensorScope abs_diff=0.0; U-Air abs_diff=0.0.
7. zero-certified-mass->NaN bug repaired via optional_float; 0.0 stays 0.0.
8. Repair is evidence serialization only; C_cov_LCB formula unchanged; R1d artifacts not rewritten.
9. SensorScope mean C_real_support: 0.01833526799149408.
10. U-Air mean C_real_support: 0.02785908931082983.
11. SensorScope mean C_point: 0.1323157362118398.
12. U-Air mean C_point: 0.19526305379746844.
13. point_zero_fraction SS=0.0 U-Air=0.0.
14. formal C_cov zero fraction SS=0.9761904761904762 U-Air=1.0.
15. median q/pi_safe SS=74.09065879812032 U-Air=33.677572180963786.
16. median q/median_positive_hat SS=3.0 U-Air=3.0.
17. R1d vacuity: see diagnostic/R1D_NONVACUITY_ATTRIBUTION.md (point vs calibration).
18. TOD current context from pre-window public UTC schedule: False.
19. Current R/O/U leakage: no. Context audit refused event-presence inference.
20. R1e Stage1 joint coverage: not run.
21. R1e Stage1 C_cov zero fraction: not run.
22. R1e Stage1 point_zero_fraction: not run.
23. Stage1 did not close; Stage1 was not executed.
24. Stage2 trigger not evaluated on real traces because Stage1 did not run.
25. Stage2 was not run and was not post-hoc selected.
26. Stage2 joint coverage: not run.
27. Stage2 C_cov zero fraction: not run.
28. Coverage slide audit applies to R1d only (false in R1d verdict). R1e stages not run.
29. R1e vs R1d: no new certificate; R1e stopped before changing the predictor on sealed traces.
30. 1-seed development closure: no.
31. Always-D vs No-D: not run (certificate not closed).
32. U-Air unsafe re-audit: not run.
33. Natural block / stress plan: not generated as executable stress; stress was not executed.
34. Tests: r1e=PASS full=PASS (passed 39, failed 0).
35. SAG run this round: NO.
36. 5-seed started this round: NO.

## 3. Window-context stop

Sealed E3 EventTrace metadata stores only dataset/seed/num_windows/num_clients/s_max/generator. The complete-aligned R3 generator clocks windows as abstract index time (deadline = window_id + 1.0), not UTC. Risk sets are sampled from the train pool independently of dataset absolute_time. RepeatableTimeOfDayMapper requires a UTC datetime; raw window_id is not a legal input. Reusing the E2 300-window SensorScope schedule would invent a mapping that is not the sealed E3 protocol. No frozen window_id -> UTC timestamp table exists. Inferring the block from the current window's first EventTrace row would use current-window event presence and is forbidden.

## 4. Readiness

NOT_READY_DYNAMIC_COV

five_seed_started = false
sag_started = false
