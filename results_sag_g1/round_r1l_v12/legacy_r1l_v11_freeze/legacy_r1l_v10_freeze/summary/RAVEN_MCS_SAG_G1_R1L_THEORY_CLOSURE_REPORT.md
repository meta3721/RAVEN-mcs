# RAVEN-MCS SAG G1 R1L Theory Closure

## Executive verdict: THEORY_CLOSURE_PASS

Theory-closure round. No experiment, no SAG, no 5-seed, no predictor/calibration tuning, no stress/tau/pi_safe/target change. Paper Sections III--VI, the aggregate-certificate algorithm, and appendix proofs are sealed. Formal Gate path is aggregate_stable_regime.

## Frozen certification object

Formal Gate mode: `aggregate_stable_regime`. Pairwise simultaneous positive LCB is retired from the formal core (motivation/appendix/diagnostic only).

## Finite-sample rule: alpha=0.05, n_min=19. Clipping k_n to n is forbidden.

## Stack

Proposition 1, Corollary 1, Assumption A, Theorem 1, Corollary 2, Proposition 2, WARMUP/CERTIFIED/RESET.
Optional bounded-drift extension: omitted.

## Restart

Next formal experiment is R1m (implement this theory, n_min=19, freeze one predictor and one regime rule, STOP before SAG).

## Gates: n_pass=21 n_fail=0
## pytest R1l: PASS passed=31 failed=0
## pytest full: PASS passed=33 failed=0

STOP.
