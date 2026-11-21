"""G4 elementary inequalities. Not an estimator test."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

G4 = Path(__file__).resolve().parents[2] / "post_review" / "G4_practical_estimator"
sys.path.insert(0, str(G4))

from lemmas import a5_holds, clip_residual, hajek_l1_gap, structured_c1  # noqa: E402


def test_clip_residual_identity():
    x = np.array([0.0, 10.0, 20.0, 25.0, 100.0])
    assert np.allclose(np.abs(np.minimum(20.0, x) - x), clip_residual(x, 20.0))


def test_hajek_l1_bound():
    rng = np.random.default_rng(30001)
    for _ in range(50):
        b = rng.random(8)
        b_star = rng.random(8)
        gap, bound, _ = hajek_l1_gap(b, b_star)
        assert gap <= bound + 1e-12


def test_c1_undefined_without_positivity():
    bad = structured_c1(k_r=8, n_r=4, b_min=1.0, pi_min=0.0)
    assert bad["defined"] == 0.0
    assert bad["C1"] == float("inf")
    good = structured_c1(k_r=8, n_r=4, b_min=1.0, pi_min=0.2)
    assert good["defined"] == 1.0
    assert np.isfinite(good["C1"])


def test_a5_rejects_uair_zero_target():
    assert a5_holds(0.0)
    assert not a5_holds(0.2546875)
