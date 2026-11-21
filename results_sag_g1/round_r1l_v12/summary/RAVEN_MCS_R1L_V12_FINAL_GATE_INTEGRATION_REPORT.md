# RAVEN-MCS R1L-v1.2 Final Gate Integration Report

## Executive verdict: THEORY_CLOSURE_PASS

## Formal definition

1. Gate_t unique definition: 1{C_LCB,t >= tau_cov} in CERTIFIED; OFF in WARMUP/RESET.
2. Design_t unique definition: Design_t := Gate_t.
3. Design_t = Gate_t? YES.
4. Dataset-level Design flag still in the formal method? NO.

## Algorithm integration

5. Window-close inputs include Gate_t? YES (alg:window_close).
6. Design decided by dataset name? NO.
7. WARMUP: Gate OFF, Design OFF, zeta fallback to 1.
8. RESET: Gate OFF, Design OFF, zeta fallback to 1.
9. CERTIFIED + C_LCB < tau: Gate OFF, Design OFF.
10. CERTIFIED + C_LCB >= tau: Gate ON, Design ON, Design-enabled zeta.

## Execution code

11. Actual runner reads Gate_t? YES (`gate_mode=aggregate_coverage` via `formal_decide_gate_and_design`).
12. Static legacy Gate can override Gate_t on the formal path? NO.
13. Oracle controls current Design? NO.
14. Current mask controls current Design? NO.
15. Source snapshot contains window_runner? YES.
16. Source snapshot contains window-close implementation? YES.

## Theory-to-operation

17. False-safe corollary = Design opened despite C_t < tau_cov, because Design_t = Gate_t.
18. Formal path Gate=OFF but Design=ON? NO.
19. Formal path Gate=ON but Design=OFF? NO.

## Paper consistency

20. Abstract still claims SensorScope ON / U-Air OFF as current method? NO.
21. Introduction still uses dataset Gate as current method? NO.
22. Conclusion still uses dataset Gate as current method? NO.
23. Section VII remains PRE-R1m legacy? YES.
24. New experimental numbers forged? NO.

## Execution boundary

25. New experiment run? NO.
26. R1m started? NO.
27. SAG? NO.
28. 5-seed? NO.
29. R1l-v1.2 tests: PASS passed=31 failed=0
30. Full tests: PASS passed=43 failed=0
31. Gates: n_pass=29 n_fail=0
32. Final verdict: THEORY_CLOSURE_PASS

STOP. Do not start R1m / SAG / 5-seed in this round.
