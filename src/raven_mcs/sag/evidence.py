"""Evidence serialization helpers. Do not change certificate algorithms."""

from __future__ import annotations

from typing import Any


def optional_float(value: Any) -> float:
    """Preserve 0.0; only missing/non-numeric values become NaN.

    R1d used ``float(x or nan)``, which maps a true 0.0 to NaN.
    """
    if value is None:
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")
