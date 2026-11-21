# Proposition 2 — Arbitrary-drift impossibility / applicability boundary

## Statement

Suppose two data-generating worlds have identical legal pre-window history
\(F_{t-}\) but different current aggregate coverage:
\[
  \text{World A: } C_t = c_{\mathrm{high}}, \qquad
  \text{World B: } C_t = c_{\mathrm{low}},
\]
with \(c_{\mathrm{low}} < \tau_{\mathrm{cov}} < c_{\mathrm{high}}\).

Any deterministic pre-window certificate must output the same \(C^{\mathrm{LCB}}_t\)
in both worlds. Therefore:
- if it outputs \(C^{\mathrm{LCB}}_t \ge \tau_{\mathrm{cov}}\) to be non-vacuous
  in World A, it is false-safe in World B;
- if it always outputs \(C^{\mathrm{LCB}}_t < \tau_{\mathrm{cov}}\) to protect
  World B, it cannot certify World A.

Hence, without additional assumptions linking the current window to observable
pre-window information, no method can simultaneously provide nontrivial
per-window certification and universal protection against arbitrary unannounced
regime shifts.

## Complete proof / construction

Let \(\mathcal{A}\) be any (possibly randomized, given extra bits independent of
the current world) map from \(F_{t-}\) to a real number \(C^{\mathrm{LCB}}_t\).
Because Worlds A and B share \(F_{t-}\), the law of \(C^{\mathrm{LCB}}_t\) is
identical in both worlds.

Write \(L\) for that common output. Exactly one of the following holds for each
realization: \(L \ge \tau_{\mathrm{cov}}\) or \(L < \tau_{\mathrm{cov}}\).

- If \(L \ge \tau_{\mathrm{cov}}\), then in World B one has \(L \ge \tau_{\mathrm{cov}} > c_{\mathrm{low}}=C_t\),
  so Gate ON is false-safe.
- If \(L < \tau_{\mathrm{cov}}\), then in World A the Gate is OFF even though
  \(C_t=c_{\mathrm{high}}>\tau_{\mathrm{cov}}\), so the window is not certified.

No choice of \(L=L(F_{t-})\) avoids both failures. This is an applicability
boundary, not a defect of a particular predictor.

A drift detector that uses only \(F_{t-}\) cannot protect the first unannounced
shift window if that window is indistinguishable from the certified regime in
\(F_{t-}\). After a detected change, the correct operational response is RESET
then WARMUP (Gate OFF) until \(n\ge 19\) in the new regime. The detector does
not restore Theorem 1 on the undetected first-shift window.

## What this does not claim

It does not say certification is impossible under Assumption A. It says
Assumption A (or a comparable link from \(F_{t-}\) to the current score law)
is necessary for a nontrivial per-window guarantee.
