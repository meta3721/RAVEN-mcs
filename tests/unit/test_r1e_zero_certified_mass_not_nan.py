"""0.0 certified mass must not become NaN."""

from __future__ import annotations

import math

from raven_mcs.sag.evidence import optional_float


def test_r1e_zero_certified_mass_not_nan() -> None:
    assert optional_float(0.0) == 0.0
    assert optional_float(0) == 0.0
    assert math.isnan(optional_float(None))
    assert optional_float(0.25) == 0.25
    assert optional_float("0.0") == 0.0
    # The old `x or nan` pattern is the bug this helper replaces.
    assert not (0.0 or False)
