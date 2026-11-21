"""Clopper–Pearson LCB is nondecreasing in the pair count at fixed n."""

from __future__ import annotations

from raven_mcs.sag.certificates import clopper_pearson_lcb


def test_lcb_monotonicity() -> None:
    n = 200.0
    delta = 0.05 / 10.0
    prev = -1.0
    for x in range(0, 81, 5):
        lcb = clopper_pearson_lcb(float(x), n, delta)
        assert lcb >= prev - 1e-12
        prev = lcb
    assert clopper_pearson_lcb(0.0, n, delta) == 0.0
    assert clopper_pearson_lcb(80.0, n, delta) > clopper_pearson_lcb(10.0, n, delta)
