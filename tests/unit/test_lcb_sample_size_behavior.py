"""LCB must tighten with more completed events, not stay at 0."""

from __future__ import annotations

from raven_mcs.sag.certificates import clopper_pearson_lcb


def test_lcb_sample_size_behavior() -> None:
    p = 0.125
    delta = 0.05 / 20.0
    lcbs = []
    for n in (8, 32, 128, 512, 2048):
        x = p * n
        lcbs.append(clopper_pearson_lcb(x, float(n), delta))
    assert lcbs[0] == 0.0 or lcbs[0] < lcbs[-1]
    assert lcbs[-1] > 0.05
    for a, b in zip(lcbs, lcbs[1:]):
        assert b + 1e-12 >= a
    assert lcbs[-1] < p
