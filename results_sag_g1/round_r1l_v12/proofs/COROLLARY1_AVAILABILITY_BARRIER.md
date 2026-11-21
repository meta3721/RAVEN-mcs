# Corollary 1 — Availability-induced pairwise barrier

## Statement

For a target pair \(i=(k,s)\) let the designated stressed entity be
\(e(i)=k\) (the pair's client; or the unique designated entity in the
paper's stress construction). Let \(A_{e(i),t}\in\{0,1\}\) be that entity's
availability in window \(t\).

Assume the necessary-condition
\[
  X_{i,t}>0 \;\Rightarrow\; A_{e(i),t}=1.
\]
Under the frozen availability stress,
\[
  P(A_{e(i),t}=1\mid F_{t-},a)\le a.
\]
Therefore
\[
  P(X_{i,t}>0\mid F_{t-},a)
  \le
  P(A_{e(i),t}=1\mid F_{t-},a)
  \le a,
\]
and \(P(X_{i,t}=0\mid F_{t-},a)\ge 1-a\). If \(a<1-\alpha\), then
\(1-a>\alpha\), and Proposition 1 implies that no strictly positive
deterministic \(1-\alpha\) pairwise LCB is guaranteed for that pair.

## Scope (do not overclaim)

The corollary applies only to pairs that satisfy
\(X_i>0\Rightarrow A_{e(i)}=1\).
It does NOT claim that "at least one entity in an arbitrary group is
unavailable implies \(P(\mathrm{active})\le a\)".

## Complete proof

The implication \(X_{i,t}>0\Rightarrow A_{e(i),t}=1\) yields the event
inclusion \(\{X_{i,t}>0\}\subseteq\{A_{e(i),t}=1\}\), hence the probability
bound above. Frozen independent (or nested) entity thinning gives
\(P(A_{e(i),t}=1\mid F_{t-},a)\le a\). If \(a<1-\alpha\), then
\(P(X_{i,t}=0\mid F_{t-},a)>\alpha\), so Proposition 1 applies to this pair.

## Frozen stress levels

For \(\alpha=0.05\), \(1-\alpha=0.95\). The frozen grid values
\(a\in\{0.80,0.60,0.40,0.20\}\) all satisfy \(a<0.95\) for pairs obeying the
designated-entity necessary condition.
