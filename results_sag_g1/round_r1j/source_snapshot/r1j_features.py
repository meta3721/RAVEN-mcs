"""Causal F_{r-} features for CONTEXT_AVAILABILITY_PRESENCE_V1. No current mask/R/O/U."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from raven_mcs.sag.r1j_spec import FEATURE_NAMES, LOOKBACK_L


def _rate(xs: Sequence[float]) -> float:
    if not xs:
        return 0.0
    return float(np.mean(xs))


def pair_features(
    *,
    hist_active: Sequence[int],
    hist_mass: Sequence[float],
    hour_of_day: int,
    weekend_flag: int,
    availability_level: float,
) -> dict[str, float]:
    """Build features from completed same-a history only (windows < r)."""
    L = int(LOOKBACK_L)
    act = [int(x) for x in hist_active]
    mass = [float(x) for x in hist_mass]
    recent_a = act[-L:]
    recent_m = mass[-L:]
    lag1 = float(act[-1]) if act else 0.0
    lag2 = float(act[-2]) if len(act) >= 2 else 0.0
    roll = _rate(recent_a)
    roll_m = _rate(recent_m)
    if len(recent_m) >= 2:
        mid = max(1, len(recent_m) // 2)
        trend = float(np.mean(recent_m[-mid:]) - np.mean(recent_m[:mid]))
    else:
        trend = 0.0
    a = float(availability_level)
    return {
        "log1p_hist_active_count": float(np.log1p(sum(act))),
        "lag1_active": lag1,
        "lag2_active": lag2,
        "rolling_active_rate_L8": roll,
        "rolling_pi_opp_mean_L8": roll_m,
        "rolling_pi_opp_trend_L8": trend,
        "hour_of_day_unit": float(int(hour_of_day) % 24) / 23.0 if 23 else 0.0,
        "weekend_flag": float(weekend_flag),
        "availability_level": a,
        "rolling_active_rate_times_a": roll * a,
    }


def feature_vector(feat: dict[str, float]) -> np.ndarray:
    return np.asarray([float(feat[name]) for name in FEATURE_NAMES], dtype=np.float64)


FORBIDDEN_FEATURE_KEYS = frozenset(
    {
        "current_mask",
        "available_entities",
        "current_R",
        "current_O",
        "current_U",
        "current_pi_opp_realized",
        "C_oracle_safe",
        "oracle_safe",
        "Y_oracle",
    }
)
