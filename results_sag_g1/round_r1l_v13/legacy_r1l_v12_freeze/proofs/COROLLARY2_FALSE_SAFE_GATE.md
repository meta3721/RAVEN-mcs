# Corollary 2 — False-safe Gate bound

## Statement

Define \(\mathrm{Gate}_t = 1\{C^{\mathrm{LCB}}_t \ge \tau_{\mathrm{cov}}\}\).
Under the conditions of Theorem 1,
\[
  P\bigl(\mathrm{Gate}_t=1 \text{ and } C_t < \tau_{\mathrm{cov}} \mid g\bigr)
  \le \alpha.
\]

## Complete proof

On the event \(\{\mathrm{Gate}_t=1,\, C_t < \tau_{\mathrm{cov}}\}\) one has
\[
  C^{\mathrm{LCB}}_t \ge \tau_{\mathrm{cov}} > C_t,
\]
hence \(C^{\mathrm{LCB}}_t > C_t\). Therefore
\[
  \{\mathrm{Gate}_t=1,\, C_t < \tau_{\mathrm{cov}}\}
  \subseteq
  \{C^{\mathrm{LCB}}_t > C_t\}.
\]
Theorem 1 gives \(P(C^{\mathrm{LCB}}_t \le C_t \mid g)\ge 1-\alpha\), so
\[
  P(C^{\mathrm{LCB}}_t > C_t \mid g) \le \alpha.
\]
The false-safe probability is at most \(\alpha\).

This is the primary safety interpretation of the aggregate certificate.
The paper must emphasize false-safe control, not pairwise simultaneous coverage.

In WARMUP and RESET, \(\mathrm{Gate}_t=\mathrm{OFF}\) by definition, so the
false-safe event is empty on those windows. The bound is asserted only on
CERTIFIED windows, which is the scope of Theorem 1.
