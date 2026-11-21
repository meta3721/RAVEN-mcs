"""Unit checks for E2 formal results analysis helpers (no training)."""
from __future__ import annotations

import numpy as np

from raven_mcs.e2.traffic_formal_analysis.stats import holm_adjust, wilcoxon_two_sided


def test_holm_adjust_monotonic_and_bounds():
    raw = [0.01, 0.04, 0.03, 0.20, 0.02]
    adj = holm_adjust(raw)
    assert len(adj) == 5
    assert all(0.0 <= p <= 1.0 for p in adj if np.isfinite(p))
    # Smallest raw should remain among the smallest adjusted.
    assert adj[0] <= adj[3]


def test_wilcoxon_handles_zeros():
    p = wilcoxon_two_sided(np.zeros(10))
    assert np.isnan(p)
