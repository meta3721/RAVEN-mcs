# R1L-v1.3 formal execution chain

STEP 1
    input method = raven_mcs
    source: `C:/Cursor/raven.mcs/src/raven_mcs/aggregation/method_policy.py` PAPER_METHOD_KEY line 36

STEP 2
    resolved policy = resolve_method('raven_mcs') -> raven_mcs
    function: `resolve_method` / `get_method_policy` line 200

STEP 3
    gate_mode = aggregate_coverage
    config key: MethodPolicy.gate_mode

STEP 4
    runner function = FullWindowRunner._decide_g_r
    source: `C:/Cursor/raven.mcs/src/raven_mcs/training/window_runner.py` line 359

STEP 5
    certificate routing function = compute_certificates
    source: `C:/Cursor/raven.mcs/src/raven_mcs/sag/certificates.py` line 490
    config key: CertificateContext.cov_mode = aggregate_stable_regime

STEP 6
    aggregate certificate function = formal_aggregate_coverage
    source: `C:/Cursor/raven.mcs/src/raven_mcs/sag/aggregate_certificate.py` line 98

STEP 7
    output: C_LCB,t and Gate_t via certificate_step / r1l_design.gate_from_certificate
    source: `C:/Cursor/raven.mcs/src/raven_mcs/sag/r1l_design.py` line 66

STEP 8
    Design_t := Gate_t
    source: `C:/Cursor/raven.mcs/src/raven_mcs/sag/r1l_design.py` `design_from_gate` line 57

STEP 9
    window-close branch selected by apply_formal_design_zeta / _apply_zeta
    source: `C:/Cursor/raven.mcs/src/raven_mcs/training/window_runner.py` line 404
