# RAVEN-MCS R1L-v1.1 Final Theory Patch Report

## Executive verdict: THEORY_CLOSURE_PASS

## Ties proof

1. Old proof treated a smaller event as still having probability >= 1-alpha (invalid: A subset B and P(B)>=1-alpha does not give P(A)>=1-alpha).
2. Auxiliary continuous tie-break variables U_j, U_t: YES.
3. Randomized rank R_t^* is uniform on {1,...,n+1}: YES.
4. Proved {R^* <= k} subseteq {S_t <= S_(k)^cal}: YES.
5. Event direction is the inclusion that raises probability, not shrinks it: YES.
6. Theorem 1 statement (P(C_LCB <= C_t | g) >= 1-alpha) is unchanged: YES.

## Availability corollary

7. Designated entity e(i)=k for pair i=(k,s).
8. Explicit X_i>0 => A_{e(i)}=1: YES.
9. Hence P(X_i>0)<=a: YES.
10. Overbroad 'at least one entity' claim deleted: YES.

## CERTIFIED semantics

11. CERTIFIED described as proving exchangeability? NO.
12. Theorem 1 still conditional on Assumption A? YES.
13. Regime rule operationalizes the scope in which Assumption A is invoked.

## Predictor block

14. Predictor frozen within certified block: YES.
15. Refit only after RESET: YES.
16. Calibration buffer cleared after RESET: YES.
17. Re-WARMUP to n>=19: YES.
18. Current window never in its own calibration: YES.

## Evidence / Section VII

19. Gate evidence paths package-local: YES (round_r1l_v11/...).
20. Section VII marked PRE-R1m legacy: YES.
21. Old experimental numbers forged/replaced? NO.

## Execution

22. New experiment? NO.
23. R1m started? NO.
24. SAG? NO.
25. 5-seed? NO.
26. R1l-v1.1 tests: PASS passed=26 failed=0
27. Full tests: PASS passed=32 failed=0
28. Gates: n_pass=23 n_fail=0
29. Final verdict: THEORY_CLOSURE_PASS

STOP. Do not start R1m/SAG/5-seed in this round.
