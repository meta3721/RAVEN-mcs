# Certificate state machine (frozen)

Exclusive states: WARMUP, CERTIFIED, RESET.

## WARMUP

Triggered when the current regime is certified as stable but \(n < 19\), or when
no certified regime is active and no RESET is required.
- \(C^{\mathrm{LCB}}_t = 0\)
- \(\mathrm{Gate}_t = \mathrm{OFF}\)
- Do not claim Theorem 1.

## CERTIFIED

Triggered only if:
- the frozen operational regime rule says window \(t\) belongs to a currently
  active candidate regime \(g\) (this operationalizes the scope in which
  Assumption A is invoked; it does not prove exchangeability);
- \(n \ge 19\);
- \(k_n \le n\) (equivalent under \(\alpha=0.05\));
- the predictor snapshot \(f_b\) of the current block is frozen.

Then compute \(\widehat C_t=f_b(F_{t-})\), \(q_t=S_{(k_n)}^{\mathrm{cal}}\),
\(C^{\mathrm{LCB}}_t=\max\{0,\widehat C_t-q_t\}\),
\(\mathrm{Gate}_t=1\{C^{\mathrm{LCB}}_t\ge\tau_{\mathrm{cov}}\}\).
Theorem 1 remains conditional on Assumption A even when the algorithmic
state is CERTIFIED.

Forbidden: "the detector certifies exchangeability";
"CERTIFIED implies Assumption A holds";
"passing the stability test proves the conformal assumption".

## RESET

Triggered when the frozen regime rule says the current regime is no longer
certified (detected change using only legal pre-window public information and
past completed outcomes).
- \(\mathrm{Gate}_t=\mathrm{OFF}\);
- \(C^{\mathrm{LCB}}_t=0\);
- finalize the current block;
- refit a new predictor snapshot \(f_{b+1}\) using only completed past data;
- freeze \(f_{b+1}\);
- clear the calibration buffer;
- transition to WARMUP for the new block and re-accumulate \(n_{\min}=19\).

Refit is forbidden during WARMUP and CERTIFIED of the same block.

Both RESET and WARMUP force Gate OFF. The machine is deterministic given the
regime rule, \(n\), and the frozen quantile.

## Regime rule (semantic freeze, detector not chosen)

R1l freezes the semantic requirement, not one detector. The next
implementation (R1m) must pre-register one rule \(R_t\) that:
1. is frozen before formal experiments;
2. does not use current \(C_t\);
3. does not use current oracle-safe labels;
4. does not use future observations;
5. states the exchangeability claim inside each certified regime;
6. on detected change, issues RESET and Gate OFF.

Paper sentence (required):
"The finite-sample guarantee applies only within certified stable regimes.
Unannounced regime shifts outside this condition are an applicability boundary.
After a detected regime change, the certificate abstains until sufficient
calibration evidence is re-established."
