"""E3-v2 public pre-window context. Current R/O/U are forbidden."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import pandas as pd

FORBIDDEN_CURRENT = frozenset(
    {
        "current_R",
        "current_O",
        "current_U",
        "current_realized_opportunity",
        "current_label",
        "current_gate_outcome",
        "current_post_window_aggregate",
        "risk_set_unit_ids",
        "observed_unit_ids",
    }
)

WHITELIST = (
    {
        "feature": "window_start_utc",
        "source": "atomic.absolute_time UTC hour floor",
        "available_time": "before_window_start",
        "public_or_private": "public",
        "lag": 0,
        "allowed": True,
        "reason": "calendar clock known before any current-window event",
    },
    {
        "feature": "window_end_utc",
        "source": "window_start_utc + 1h",
        "available_time": "before_window_start",
        "public_or_private": "public",
        "lag": 0,
        "allowed": True,
        "reason": "deterministic from public start",
    },
    {
        "feature": "hour_of_day",
        "source": "window_start_utc.hour",
        "available_time": "before_window_start",
        "public_or_private": "public",
        "lag": 0,
        "allowed": True,
        "reason": "TOD from public UTC, RepeatableTimeOfDayMapper-compatible",
    },
    {
        "feature": "weekday",
        "source": "window_start_utc.weekday",
        "available_time": "before_window_start",
        "public_or_private": "public",
        "lag": 0,
        "allowed": True,
        "reason": "calendar, not event presence",
    },
    {
        "feature": "weekend_flag",
        "source": "weekday in {5,6}",
        "available_time": "before_window_start",
        "public_or_private": "public",
        "lag": 0,
        "allowed": True,
        "reason": "calendar, not event presence",
    },
    {
        "feature": "lagged_public_event_count",
        "source": "completed prior windows only",
        "available_time": "F_r_minus",
        "public_or_private": "public",
        "lag": 1,
        "allowed": True,
        "reason": "history of completed windows; not current R/O/U",
    },
    {
        "feature": "current_R",
        "source": "current EventTrace risk set",
        "available_time": "current_window",
        "public_or_private": "private",
        "lag": 0,
        "allowed": False,
        "reason": "current-window leakage",
    },
    {
        "feature": "current_O",
        "source": "current observations",
        "available_time": "current_window",
        "public_or_private": "private",
        "lag": 0,
        "allowed": False,
        "reason": "current-window leakage",
    },
    {
        "feature": "current_U",
        "source": "current usable mark",
        "available_time": "current_window",
        "public_or_private": "private",
        "lag": 0,
        "allowed": False,
        "reason": "current-window leakage",
    },
    {
        "feature": "current_realized_opportunity",
        "source": "current risk-set occupancy",
        "available_time": "current_window",
        "public_or_private": "private",
        "lag": 0,
        "allowed": False,
        "reason": "oracle diagnostic only; not a Gate feature",
    },
    {
        "feature": "current_label",
        "source": "current target_value",
        "available_time": "current_window",
        "public_or_private": "private",
        "lag": 0,
        "allowed": False,
        "reason": "outcome leakage",
    },
    {
        "feature": "current_gate_outcome",
        "source": "Gate ON/OFF",
        "available_time": "post_window",
        "public_or_private": "private",
        "lag": 0,
        "allowed": False,
        "reason": "post-hoc",
    },
    {
        "feature": "dataset_name",
        "source": "dataset identifier",
        "available_time": "any",
        "public_or_private": "public",
        "lag": 0,
        "allowed": False,
        "reason": "dataset-name hard-coded Gate is forbidden",
    },
)


class ContextLeakageError(ValueError):
    pass


def forbid_current_window_features(features: Mapping[str, Any] | None) -> None:
    keys = {str(k) for k in (features or {})}
    hit = keys & FORBIDDEN_CURRENT
    if hit:
        raise ContextLeakageError(f"current-window features forbidden in E3-v2 context: {sorted(hit)}")


def public_context_from_start(window_start_utc: Any) -> dict[str, Any]:
    ts = pd.Timestamp(window_start_utc)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    start = ts.floor("h")
    end = start + pd.Timedelta(hours=1)
    weekday = int(start.weekday())
    ctx = {
        "window_start_utc": start.isoformat(),
        "window_end_utc": end.isoformat(),
        "hour_of_day": int(start.hour),
        "weekday": weekday,
        "weekend_flag": bool(weekday >= 5),
        "timezone": "UTC",
    }
    forbid_current_window_features(ctx)
    return ctx


def is_allowed_feature(name: str) -> bool:
    rec = next((r for r in WHITELIST if r["feature"] == name), None)
    return bool(rec and rec["allowed"])
