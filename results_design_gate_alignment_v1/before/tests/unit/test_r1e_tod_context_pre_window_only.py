"""Legal TOD context comes only from a public UTC schedule."""

from __future__ import annotations

import pandas as pd
import pytest

from raven_mcs.sag.window_context import (
    PublicWindowSchedule,
    WindowContextError,
    public_window_tod_block,
)


def test_r1e_tod_context_pre_window_only() -> None:
    schedule = PublicWindowSchedule(
        window_start_utc={
            0: pd.Timestamp("2020-01-01T00:00:00Z"),
            1: pd.Timestamp("2020-01-01T07:00:00Z"),
        },
        source="unit-test-public-clock",
    )
    assert public_window_tod_block(0, schedule) == 0
    assert public_window_tod_block(1, schedule) == 1
    with pytest.raises(WindowContextError):
        PublicWindowSchedule(
            window_start_utc={0: pd.Timestamp("2020-01-01T00:00:00Z")},
            source="leak",
            uses_current_event_presence=True,
        )
