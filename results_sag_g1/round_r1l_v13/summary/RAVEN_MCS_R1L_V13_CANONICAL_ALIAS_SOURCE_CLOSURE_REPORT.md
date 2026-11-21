# RAVEN-MCS R1L-v1.3 Canonical Alias + Source Closure Report

## Executive verdict: THEORY_CLOSURE_PASS

## Canonical method

1. Paper method key: **raven_mcs**
2. resolve_method('raven_mcs') -> `raven_mcs`
3. gate_mode: `aggregate_coverage`
4. raven_mcs can still enter always_on? NO
5. raven_mcs_formal: internal alias of raven_mcs (not paper-facing unique name)
6. Legacy always-on explicit key: **raven_legacy_always_on** (historical `raven` remains legacy_only)

## Execution chain

7. window runner: `src/raven_mcs/training/window_runner.py` `FullWindowRunner._decide_g_r` / `_apply_zeta`
8. compute_certificates: `src/raven_mcs/sag/certificates.py`
9. aggregate routing: `compute_certificates` when cov_mode=aggregate_stable_regime
10. aggregate certificate: `src/raven_mcs/sag/aggregate_certificate.py` `formal_aggregate_coverage`
11. Gate_t: `r1l_state.certificate_step` then `r1l_design.gate_from_certificate`
12. Design_t: `r1l_design.design_from_gate` / `formal_decide_gate_and_design`
13. window-close branch: `apply_formal_design_zeta` in `_apply_zeta` when gate_mode=aggregate_coverage

## Source closure

14. certificates.py in snapshot? YES
15. routing dependencies included? YES (see R1L_V13_TRANSITIVE_SOURCE_CLOSURE.csv)
16. source closure manifest all PASS? True
17. ZIP independently traces the chain? YES

## Legacy isolation

18. dataset-level static Gate can control formal raven_mcs? NO
19. always-on legacy can override Gate_t on formal path? NO
20. alias cycle? NO

## R1m readiness

21. R1m formal method frozen as raven_mcs? YES
22. R1m already run? NO
23. Section VII PRE-R1m legacy? YES
24. New experiment? NO
25. SAG? NO
26. 5-seed? NO

## Verification

27. R1l-v1.3 tests: PASS passed=38 failed=0
28. Full tests: PASS passed=47 failed=0
29. Gates: n_pass=27 n_fail=0
30. Final verdict: THEORY_CLOSURE_PASS

R1l series stops here. Next round is R1m — do not auto-start.
