"""Pairwise positive-LCB barrier under hidden current availability.

Deterministic pre-window lower bounds only. Current mask is not F_{r-}-measurable.
"""

from __future__ import annotations

from raven_mcs.sag.r1k_spec import DELTA_CAL, NUM_TOL, ONE_MINUS_DELTA


DERIVATION_MD = """# Pairwise Positive LCB Barrier Derivation

## Setting (conditional, not an unconditional universal theorem)

Fix a target-positive pair \(i=(k,s)\), a window \(r\), and a public scenario-level
availability parameter \(a\). Let \(F=F_{r-}\) be pre-window public information.
The current-window realized availability **mask identity** is **not** in \(F\).

Let \(X=X_i(r,a)\\ge 0\) be realized opportunity mass for the pair. Under exogenous
entity thinning, if a required entity is unavailable then \(X=0\).

A **deterministic pre-window lower bound** is a function \(L=L(F)\\in\\mathbb{R}\).
It does not depend on the current mask or on current \(X\).

**Conditional validity** at level \(1-\\delta\) requires:

    P( L(F) <= X | F ) >= 1-delta

with \(\\delta=0.05\) frozen.

## Zero-event barrier

Suppose \(P(X=0\\mid F)>\\delta\). Then for any strictly positive bound \(L(F)>0\):

    {L(F) <= X} subset {X > 0}

because \(X=0 < L(F)\). Therefore

    P(L(F) <= X | F)
    <=
    P(X > 0 | F)
    =
    1 - P(X=0 | F)
    <
    1-delta

So no strictly positive deterministic \(L(F)\) can satisfy \(1-\\delta\) conditional
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

i.e. only if \(a\\ge 0.95\). Frozen stress levels \(0.80,0.60,0.40,0.20\) all fail
this necessary condition. \(a=1.00\) does not create an availability zero-event;
that case is audited separately via historical presence rates.

## Simultaneous multiplicity

R1j requires a **window-max residual** over many target-positive pairs, i.e.
simultaneous validity. If even a single pair cannot support a positive \(1-\\delta\)
LCB, the simultaneous requirement is strictly harder, not easier. Independence
products \(\\prod_i p_i\) are **diagnostics**, not theorems.

## Consistency with R1j

R1j produced \(C_{\\mathrm{cov,dynamic}}=0\) on every eligible window, with joint
validity \(1.0\) (vacuous zeros never exceed realized mass). That outcome is
consistent with this barrier: valid pairwise LCBs collapse to 0 under hidden
availability at \(a<0.95\).
"""


def p_active_upper_from_a(availability_level: float) -> float:
    return float(availability_level)


def strict_positive_lcb_possible(p_active_upper: float, *, delta: float = DELTA_CAL) -> bool:
    return float(p_active_upper) + NUM_TOL >= (1.0 - float(delta))


def coverage_upper_if_positive_lcb(p_zero: float) -> float:
    """P(L<=X | F) <= P(X>0 | F) = 1 - P(X=0 | F) when L(F)>0."""
    return float(max(0.0, min(1.0, 1.0 - float(p_zero))))


def barrier_reason(availability_level: float, *, delta: float = DELTA_CAL) -> str:
    a = float(availability_level)
    if a + NUM_TOL >= (1.0 - float(delta)):
        return "a_ge_1_minus_delta_availability_zero_event_not_forced"
    return (
        f"p_active_upper<=a={a:.2f}<{1.0 - float(delta):.2f}=1-delta; "
        "hidden current mask can force X=0 with probability > delta"
    )


def one_minus_delta(delta: float = DELTA_CAL) -> float:
    return 1.0 - float(delta)


assert abs(one_minus_delta() - ONE_MINUS_DELTA) < NUM_TOL
