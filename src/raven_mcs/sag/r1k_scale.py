"""Two frozen presence->mass maps. Attribution only; no new certificate."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from raven_mcs.sag.r1k_spec import NUM_TOL


def mean_mass_all(hist: Sequence[float]) -> float:
    xs = [float(x) for x in hist if np.isfinite(float(x))]
    if not xs:
        return 0.0
    return float(np.mean(xs))


def mean_mass_positive(hist: Sequence[float], *, tol: float = NUM_TOL) -> float:
    xs = [float(x) for x in hist if np.isfinite(float(x)) and float(x) > float(tol)]
    if not xs:
        return 0.0
    return float(np.mean(xs))


def hat_pi_old(p_hat_active: float, *, pi_safe: float, mean_all: float) -> float:
    """R1j map: p * max(pi_safe, mean_mass_all inclusive of zeros)."""
    scale = max(float(pi_safe), float(mean_all) if np.isfinite(mean_all) else 0.0)
    return float(np.clip(p_hat_active, 0.0, 1.0) * scale)


def hat_pi_cond(p_hat_active: float, *, pi_safe: float, mean_pos: float) -> float:
    """Conditional-positive map: p * max(pi_safe, mean_mass | mass>0)."""
    scale = max(float(pi_safe), float(mean_pos) if np.isfinite(mean_pos) else 0.0)
    return float(np.clip(p_hat_active, 0.0, 1.0) * scale)
