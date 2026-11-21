# Theory-to-algorithm interface (frozen)

## Input

- legal pre-window context \(z_t\) (public time/context only);
- scenario-level availability \(a_t\) (public); not the realized mask identity;
- historical same-block completed pairs;
- current regime-rule output.

## Maintained state

- block_id
- predictor_snapshot_id
- state in {WARMUP, CERTIFIED, RESET}
- regime_id
- n_cal
- calibration_buffer

## Output

- certificate_state;
- \(\widehat C_t=f_b(F_{t-})\);
- n_cal;
- \(q_t\) if CERTIFIED, else undefined;
- \(C^{\mathrm{LCB}}_t\);
- Gate_t.

## Canonical logic

    if regime_change_detected:
        state = RESET
        Gate = OFF
        finalize current block
        fit new predictor f_{b+1} using only completed past data
        freeze f_{b+1}
        clear calibration buffer
        state = WARMUP
    elif state == WARMUP:
        use frozen f_b
        if n_cal < 19:
            C_LCB = 0
            Gate = OFF
        once n_cal >= 19 and operational regime rule remains active:
            state = CERTIFIED
    elif state == CERTIFIED:
        use same frozen f_b
        q_t = finite_sample_quantile(historical same-block scores, alpha=0.05)
        C_hat_t = f_b(F_{t-})
        C_LCB,t = max(0, C_hat_t - q_t)
        Gate_t = 1{C_LCB >= tau_cov}

No current mask is an input. Historical \(C_j\) is used only after window \(j\)
completes. The current window is never in its own \(q_t\). Experimental oracle
labels are not training inputs for the current window. \(\widehat C_t\) is
never reported as the certificate.

The scoring rule is frozen per certified block so that Theorem 1's ordinary
finite-sample exchangeable rank argument applies. Per-window refit would take
the construction outside that theorem.
