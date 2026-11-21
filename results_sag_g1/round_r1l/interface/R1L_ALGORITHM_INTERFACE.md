# Theory-to-algorithm interface (frozen)

## Input

- legal pre-window context \(z_t\) (public time/context only);
- scenario-level availability \(a_t\) (public); not the realized mask identity;
- historical certified-regime pairs \((\widehat C_j, C_j)\) for completed windows;
- current regime state / regime-rule output.

## Output

- certificate_state in {WARMUP, CERTIFIED, RESET};
- \(\widehat C_t\);
- n_cal;
- \(q_t\) if CERTIFIED, else undefined;
- \(C^{\mathrm{LCB}}_t\);
- Gate_t.

## Canonical logic

    if regime_not_certified:
        state = RESET if an active certified regime existed else WARMUP
        C_LCB = 0
        Gate = OFF
    elif n_cal < 19:
        state = WARMUP
        C_LCB = 0
        Gate = OFF
    else:
        state = CERTIFIED
        C_hat = predictor(F_{t-})
        q = finite_sample_conformal_quantile(scores, alpha=0.05)  # no clip
        C_LCB = max(0, C_hat - q)
        Gate = 1{C_LCB >= tau_cov}

No current mask is an input. Historical \(C_j\) is used only after window \(j\)
completes. Experimental oracle labels are not training inputs for the current
window. \(\widehat C_t\) is never reported as the certificate.

The predictor family is not frozen beyond: pre-register one measurable \(f_t\)
before the next experiment (R1m). Theorem 1 does not depend on the regression
class.
