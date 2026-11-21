# RAVEN-MCS SAG G1 R1F Oracle Coverage Ceiling Report

## Executive verdict: E3_THRESHOLD_INCOMPATIBLE

STOP. No predictor repair, no calibration repair, no SAG, no 5-seed in this round.

## Answers

1. Frozen R1d/R1e artifacts reused: True.
2. target law hash consistent: True (`86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07`).
3. pi_safe rule/hash consistent: `aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7`.
4. tau_cov still 0.05: True.
5. E3 EventTrace hashes: sensorscope=`782df964fa2024cbc6b152c071d2ccd17b1cc2c210441710fe2c22fceb7058ef` uair=`67ce562381f755abc360b013ecf70561c9aa8d7d2108dfc45072d807f8bf228f`.
6. SensorScope warm-up windows: 84.
7. U-Air warm-up windows: 64.
8. SensorScope C_real_support mean/median/max: 0.01833526799149408/0.018181818181818132/0.022654350996596878.
9. SensorScope C_oracle_safe mean/median/max: 0.01833526799149408/0.018181818181818132/0.022654350996596878.
10. SensorScope oracle pass count/rate: 0/0.0.
11. U-Air C_real_support mean/median/max: 0.02785908931082983/0.02784810126582283/0.05098452883263012.
12. U-Air C_oracle_safe mean/median/max: 0.02785908931082983/0.02784810126582283/0.05098452883263012.
13. U-Air oracle pass count/rate: 1/0.015625.
14. C_oracle_safe <= C_real_support all warm-up windows: True.
15. C_cov_R1d <= C_oracle_safe on joint-valid windows: True.
16. SensorScope oracle reachability: E3_THRESHOLD_INCOMPATIBLE.
17. U-Air oracle reachability: E3_THRESHOLD_MARGINAL.
18. Robust natural safe regime: False.
19. Robust natural unsafe regime: True.
20. Vacuity shares (mean gaps): protocol=0.551 pi_safe=0.000 certificate=0.449.
21. E3 windows have real wall-clock semantics: False (abstract index clock).
22. E3 preserves temporal continuity: False in sealed trace clock.
23. E3 sampling may depress natural opportunity support: True.
24. target vs realized opportunity density mismatch: True.
25. predictor modified this round: False.
26. calibration modified this round: False.
27. threshold modified this round: False.
28. E3 modified this round: False.
29. SAG run this round: False.
30. 5-seed run this round: False.
31. pytest r1f: PASS passed=20 failed=0.
32. full pytest: PASS passed=24 failed=0.
33. R1F-S0–S20 artifact-derived: see summary/R1F_GATE_REPORT.json.
34. Final verdict: E3_THRESHOLD_INCOMPATIBLE.
35. Certificate repair allowed next round: False.
36. E3-v2 protocol specification required first: True.

## E3 context

Sealed E3 EventTrace metadata stores only dataset/seed/num_windows/num_clients/s_max/generator. The complete-aligned R3 generator clocks windows as abstract index time (deadline = window_id + 1.0), not UTC. Risk sets are sampled from the train pool independently of dataset absolute_time. RepeatableTimeOfDayMapper requires a UTC datetime; raw window_id is not a legal input. Reusing the E2 300-window SensorScope schedule would invent a mapping that is not the sealed E3 protocol. No frozen window_id -> UTC timestamp table exists. Inferring the block from the current window's first EventTrace row would use current-window event presence and is forbidden.
