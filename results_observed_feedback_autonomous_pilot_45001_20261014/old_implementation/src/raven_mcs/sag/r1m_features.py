"""Frozen R1m legal pre-window features. No current C, oracle, or mask."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from raven_mcs.sag.r1m_spec import FEATURE_NAMES, LOOKBACK_L

_2PI = 2.0 * math.pi


def last_available(history: Sequence[float], fallback: float) -> float:
    if not history:
        return float(fallback)
    return float(history[-1])


def rolling_mean(history: Sequence[float], *, L: int = LOOKBACK_L, fallback: float) -> float:
    if not history:
        return float(fallback)
    tail = list(history)[-int(L) :]
    return float(np.mean(np.asarray(tail, dtype=np.float64)))


def rolling_linear_trend(history: Sequence[float], *, L: int = LOOKBACK_L) -> float:
    """OLS slope of C vs integer time on the last L completed windows."""
    tail = list(history)[-int(L) :]
    if len(tail) < 2:
        return 0.0
    y = np.asarray(tail, dtype=np.float64)
    t = np.arange(len(y), dtype=np.float64)
    t_c = t - t.mean()
    y_c = y - y.mean()
    denom = float(np.dot(t_c, t_c))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(t_c, y_c) / denom)


def hour_sin_cos(hour: int) -> tuple[float, float]:
    h = int(hour) % 24
    return math.sin(_2PI * h / 24.0), math.cos(_2PI * h / 24.0)


def feature_vector(
    *,
    availability_level: float,
    history_c: Sequence[float],
    hour: int,
    weekend: bool,
    pretest_mean: float,
) -> np.ndarray:
    hist = [float(x) for x in history_c]
    mean_fb = float(pretest_mean)
    lag1 = last_available(hist, mean_fb)
    lag2 = last_available(hist[:-1], lag1) if hist else last_available(hist, mean_fb)
    hs, hc = hour_sin_cos(hour)
    vec = np.asarray(
        [
            1.0,
            float(availability_level),
            lag1,
            lag2,
            rolling_mean(hist, fallback=mean_fb),
            rolling_linear_trend(hist),
            hs,
            hc,
            1.0 if weekend else 0.0,
        ],
        dtype=np.float64,
    )
    if vec.shape != (len(FEATURE_NAMES),):
        raise RuntimeError("feature vector length mismatch")
    return vec


def design_matrix(
    records: Sequence[tuple[float, Sequence[float], int, bool]],
    *,
    pretest_mean: float,
) -> np.ndarray:
    rows = [
        feature_vector(
            availability_level=a,
            history_c=hist,
            hour=hour,
            weekend=weekend,
            pretest_mean=pretest_mean,
        )
        for a, hist, hour, weekend in records
    ]
    return np.vstack(rows) if rows else np.zeros((0, len(FEATURE_NAMES)), dtype=np.float64)
