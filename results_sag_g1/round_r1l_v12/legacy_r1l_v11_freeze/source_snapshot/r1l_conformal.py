"""Finite-sample one-sided conformal quantile. No k_n clipping. Theory object for R1m."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, k_n, n_min


def finite_sample_conformal_quantile(
    scores: Sequence[float],
    *,
    alpha: float = ALPHA,
) -> tuple[float, int, bool]:
    """Return (q, n, warmup).

    If n < n_min or k_n > n, warmup=True and q=nan.
    MUST NOT clip k_n to n and still call the result a nominal 95% certificate.
    """
    xs = sorted(float(x) for x in scores if np.isfinite(float(x)))
    n = len(xs)
    k = k_n(n, alpha)
    if n < n_min(alpha) or k > n:
        return float("nan"), n, True
    return float(xs[k - 1]), n, False


def c_lcb(c_hat: float, q: float) -> float:
    if not np.isfinite(float(c_hat)) or not np.isfinite(float(q)):
        return float("nan")
    return float(max(0.0, float(c_hat) - float(q)))


def gate_on(c_lcb_val: float, tau_cov: float) -> bool:
    if not np.isfinite(float(c_lcb_val)):
        return False
    return float(c_lcb_val) >= float(tau_cov)


assert N_MIN == 19
assert finite_sample_conformal_quantile(list(range(8)))[2] is True
assert finite_sample_conformal_quantile(list(range(18)))[2] is True
assert finite_sample_conformal_quantile(list(range(19)))[2] is False
