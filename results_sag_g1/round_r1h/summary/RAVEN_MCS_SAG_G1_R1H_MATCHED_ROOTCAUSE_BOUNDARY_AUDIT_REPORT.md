# RAVEN-MCS SAG G1 R1H Matched Root-Cause + Boundary Audit

## Executive verdict: R1H_ROOTCAUSE_PARTIAL_BOUNDARY_CLOSED

STOP.

## Answers

1. CF-M1 rule frozen before run: hash `272edf7acbc16d181dab4167914206f94a4d5c9a4f105aec1edf26f3f5b739f3`.
2. Matched inputs: per-client risk-set size, candidate=risk, seed 30001, target/pi_safe/tau.
3. exact-match rate SS=0.0 U-Air=1.0.
4. deficit windows SS=100 U-Air=0.
5. Deficits logged per window in CFM1_MATCHING_AUDIT.csv (no cross-time fill).
6. CF0 mean/median C_oracle SS=0.018333217584554487/0.01818181818181818; U-Air=0.028013361462728547/0.028270042194092827.
7. CF-M1 mean/median SS=0.06852142509896524/0.07000486144871172; U-Air=0.09333333333333334/0.04050632911392406.
8. pass rate CF0→CFM1 SS 0.0→0.76; U-Air 0.0125→0.4.
9. matched-only mean delta SS=nan U-Air=0.06531997187060479.
10. deficit-driven? SS=False U-Air=False.
11. STRONG? False (class=PARTIAL_CROSS_TIME_MIXING_EVIDENCE).
12. PARTIAL? True.
13. Write 'sampling caused ceiling'? only if STRONG (here False).
14. Conservative wording: matched-budget same-hour restriction raises oracle ceiling relative to CF0; residual co-occurrence coupling remains because active-pair count is an outcome, not a matched input.
15. Mechanism 1 evidence: mean Delta_oracle SS=0.05018820751441073 U-Air=0.06531997187060479.
16. Mechanism 2: R1g CF2 vs CF1 same oracle, higher lag-1 Jaccard — order affects predictability not the oracle ceiling.
17. Yes, split in ROOT_CAUSE_MECHANISM_SPLIT.md.
18. Completeness fields: timestamps, span, split edges, contiguity, entity counts — not oracle.
19. Outcome-blind: True.
20. SensorScope status counts: [(('sensorscope', 'FULL_BOUNDARY'), 2), (('sensorscope', 'FULL_INTERIOR'), 60)].
21. U-Air status counts: [(('uair', 'FULL_BOUNDARY'), 2), (('uair', 'FULL_INTERIOR'), 51)].
22. U-Air 0/1/2/51/52: see UAIR_UNSAFE_WINDOW_AUDIT.md.
23. Edge artifact class: UNSAFE_RARE_BUT_NATURAL.
24. complete-window pass SS=1.0 U-Air=0.9056603773584906.
25. interior pass SS=1.0 U-Air=0.9411764705882353.
26. SensorScope all-safe (main): True.
27. U-Air interior unsafe count: 3.
28. Natural interior unsafe regime: True.
29. predictor modified: False.
30. calibration modified: False.
31. threshold modified: False.
32. dynamic C_cov: False.
33. SAG: False.
34. 5-seed: False.
35. stress created: False.
36. pytest R1h: PASS passed=27 failed=0.
37. full pytest: PASS passed=30 failed=0.
38. R1H-S0–S25: n_pass=26 n_fail=0.
