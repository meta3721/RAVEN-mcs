# Proposition 1 — Positive pairwise LCB barrier

## Statement

Let \(X_t \ge 0\) denote the realized opportunity of one target pair in window \(t\).
Let \(F_{t-}\) denote all information legally available before window \(t\).
Let \(L_t = L(F_{t-})\) be a deterministic pre-window lower bound (a measurable
function of \(F_{t-}\) only).

If
\[
  P(X_t = 0 \mid F_{t-}) > \alpha,
\]
then no strictly positive \(L_t > 0\) can satisfy
\[
  P(L_t \le X_t \mid F_{t-}) \ge 1-\alpha.
\]

## Scope (not a universal impossibility theorem)

The claim is restricted to:
- deterministic pre-window lower bounds;
- a zero-mass event that is possible given \(F_{t-}\);
- hidden current realization (current \(X_t\) not in \(F_{t-}\));
- a conditional validity claim given \(F_{t-}\).

The claim does not cover randomized certificates, Bayesian posterior intervals
under a correctly specified prior, or lower bounds that are allowed to depend on
the current hidden realization.

## Complete proof

Fix a version of the regular conditional probability given \(F_{t-}\).
On the event \(\{L_t > 0\}\), the inclusion
\[
  \{L_t \le X_t\} \subseteq \{X_t > 0\}
\]
holds pathwise: if \(X_t = 0\), then \(X_t < L_t\), so \(L_t \le X_t\) fails.
Therefore
\begin{align*}
P(L_t \le X_t \mid F_{t-})
&\le
P(X_t > 0 \mid F_{t-}) \\
&=
1 - P(X_t = 0 \mid F_{t-}) \\
&<
1-\alpha
\end{align*}
on the set where \(P(X_t=0\mid F_{t-})>\alpha\) and \(L_t>0\).

Hence no strictly positive deterministic \(L(F_{t-})\) can meet the \(1-\alpha\)
conditional coverage requirement on such \(F_{t-}\). Any deterministic lower
bound that does meet the requirement must satisfy \(L_t=0\) on that \(F_{t-}\),
or the coverage claim is false.

## Remark

This is a structural non-vacuity barrier, not a statement that pairwise
diagnostics are useless. A valid pairwise certificate may exist and be
identically zero.
