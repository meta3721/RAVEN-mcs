# Pairwise Positive LCB Barrier Derivation

## Setting (conditional, not an unconditional universal theorem)

Fix a target-positive pair \(i=(k,s)\), a window \(r\), and a public scenario-level
availability parameter \(a\). Let \(F=F_{r-}\) be pre-window public information.
The current-window realized availability **mask identity** is **not** in \(F\).

Let \(X=X_i(r,a)\ge 0\) be realized opportunity mass for the pair. Under exogenous
entity thinning, if a required entity is unavailable then \(X=0\).

A **deterministic pre-window lower bound** is a function \(L=L(F)\in\mathbb{R}\).
It does not depend on the current mask or on current \(X\).

**Conditional validity** at level \(1-\delta\) requires:

    P( L(F) <= X | F ) >= 1-delta

with \(\delta=0.05\) frozen.

## Zero-event barrier

Suppose \(P(X=0\mid F)>\delta\). Then for any strictly positive bound \(L(F)>0\):

    {L(F) <= X} subset {X > 0}

because \(X=0 < L(F)\). Therefore

    P(L(F) <= X | F)
    <=
    P(X > 0 | F)
    =
    1 - P(X=0 | F)
    <
    1-delta

So no strictly positive deterministic \(L(F)\) can satisfy \(1-\delta\) conditional
coverage. Any valid deterministic LCB must set \(L(F)=0\) (or give up the coverage
guarantee) on that \(F\).

## Availability upper bound used in this round

Pair presence requires at least one stressed entity to be available. Nested hash
thinning retains each entity independently at rate \(a\), so

    P(X > 0 | F, a) <= a
    =: p_active_upper

This is a conservative, simple, auditable upper bound. Multi-entity conjunction
would only lower the probability further. This round does **not** fit a tighter
pair-specific availability model.

Therefore a strictly positive 95% pairwise LCB is theoretically possible only if

    p_active_upper >= 1-delta = 0.95

i.e. only if \(a\ge 0.95\). Frozen stress levels \(0.80,0.60,0.40,0.20\) all fail
this necessary condition. \(a=1.00\) does not create an availability zero-event;
that case is audited separately via historical presence rates.

## Simultaneous multiplicity

R1j requires a **window-max residual** over many target-positive pairs, i.e.
simultaneous validity. If even a single pair cannot support a positive \(1-\delta\)
LCB, the simultaneous requirement is strictly harder, not easier. Independence
products \(\prod_i p_i\) are **diagnostics**, not theorems.

## Consistency with R1j

R1j produced \(C_{\mathrm{cov,dynamic}}=0\) on every eligible window, with joint
validity \(1.0\) (vacuous zeros never exceed realized mass). That outcome is
consistent with this barrier: valid pairwise LCBs collapse to 0 under hidden
availability at \(a<0.95\).
