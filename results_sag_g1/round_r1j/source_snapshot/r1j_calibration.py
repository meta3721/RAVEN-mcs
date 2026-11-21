"""Same-a window-max conformal calibration. Reuses R1d residual quantile."""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np

from raven_mcs.sag.dynamic_cov import conformal_upper_residual, window_max_residual
from raven_mcs.sag.r1j_spec import DELTA_CAL, LOOKBACK_MIN, NUM_TOL


def max_residual(
    hat: Mapping[tuple[str, str], float],
    realized: Mapping[tuple[str, str], float],
    pairs: Sequence[tuple[str, str]],
) -> float:
    return window_max_residual(hat, realized, pairs)


def same_a_q(residuals: Sequence[float], *, delta: float = DELTA_CAL, min_calib: int = LOOKBACK_MIN) -> tuple[float, int, bool]:
    xs = [float(x) for x in residuals if np.isfinite(float(x))]
    n = len(xs)
    if n < int(min_calib):
        return float("nan"), n, True
    return float(conformal_upper_residual(xs, float(delta))), n, False


def lower_pi(hat: float, q: float) -> float:
    if not np.isfinite(float(hat)) or not np.isfinite(float(q)):
        return float("nan")
    return float(max(0.0, float(hat) - float(q)))


def joint_valid(
    lowers: Mapping[tuple[str, str], float],
    realized: Mapping[tuple[str, str], float],
    pairs: Sequence[tuple[str, str]],
    *,
    tol: float = NUM_TOL,
) -> tuple[bool, float]:
    diffs: list[float] = []
    ok = True
    for key in pairs:
        lo = float(lowers.get(key, float("nan")))
        ref = float(realized.get(key, 0.0))
        if not np.isfinite(lo):
            ok = False
            diffs.append(float("nan"))
            continue
        d = lo - ref
        diffs.append(d)
        if lo > ref + float(tol):
            ok = False
    finite = [d for d in diffs if np.isfinite(d)]
    return ok, (max(finite) if finite else float("nan"))
