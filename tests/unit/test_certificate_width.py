"""One-sided UCB width = UCB − actual; must not be all-NaN."""

from __future__ import annotations

import numpy as np
import pytest

from raven_mcs.sag.certificates import conformal_upper_quantile


def certificate_widths(actuals: list[float], ucbs: list[float]) -> list[float]:
    out = []
    for a, u in zip(actuals, ucbs):
        if np.isfinite(a) and np.isfinite(u):
            out.append(float(u) - float(a))
    return out


def test_width_not_all_nan() -> None:
    actuals = [0.1, 0.0, 0.2]
    ucb = conformal_upper_quantile(actuals, 0.95)
    widths = certificate_widths(actuals, [ucb, ucb, ucb])
    assert widths
    assert all(np.isfinite(w) for w in widths)
    assert max(widths) >= 0
    assert conformal_upper_quantile([0.1, 0.2, 0.3, 0.4], 0.95) == pytest.approx(0.4)
