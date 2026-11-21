# Corollary 1 — Availability-induced pairwise barrier

## Statement

Suppose pair opportunity requires availability of at least one hidden stressed
entity, and only the scenario-level retention \(a\) is known pre-window.
A simple, auditable upper bound is
\[
  P(X_t > 0 \mid F_{t-}, a) \le a.
\]
Therefore, if \(a < 1-\alpha\), a strictly positive deterministic \(1-\alpha\)
pairwise LCB cannot be guaranteed under Proposition 1.

## Complete proof

Entity thinning retains each entity with probability at most \(a\) from the
certificate's pre-window information. Presence of the pair requires at least one
required entity to be available, hence
\[
  P(X_t > 0 \mid F_{t-}, a) \le a,
\]
and
\[
  P(X_t = 0 \mid F_{t-}, a) \ge 1-a.
\]
If \(a < 1-\alpha\), then \(P(X_t=0\mid F_{t-},a) > \alpha\). Proposition 1 applies.

A multi-entity conjunction would only decrease \(P(X_t>0)\). This round uses the
weakest (largest) simple upper bound \(a\).

## Frozen stress levels

For \(\alpha=0.05\), \(1-\alpha=0.95\). The frozen grid values
\(a\in\{0.80,0.60,0.40,0.20\}\) all satisfy \(a<0.95\), so they lie in the
barrier region. The value \(a=1.00\) does not create an availability zero-event;
any remaining barrier there comes from sparse natural presence, which is an
empirical fact (R1k: no target pair has historical presence \(\ge 0.95\)) and is
not required for Corollary 1.

This explains how a pairwise simultaneous certificate can be jointly valid and
identically vacuous.
