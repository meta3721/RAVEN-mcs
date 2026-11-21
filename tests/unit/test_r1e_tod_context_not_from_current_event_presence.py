"""Current EventTrace event presence cannot define the TOD block."""

from __future__ import annotations

from pathlib import Path

import pytest

from raven_mcs.sag.window_context import (
    audit_e3_prewindow_public_schedule,
    forbid_tod_from_current_event_presence,
    WindowContextError,
)

ROOT = Path(__file__).resolve().parents[2]


def test_r1e_tod_context_not_from_current_event_presence() -> None:
    with pytest.raises(WindowContextError):
        forbid_tod_from_current_event_presence(events=[{"window_id": 3}], window_id=3)
    audit = audit_e3_prewindow_public_schedule(ROOT)
    assert audit["legal"] is False
    assert audit["verdict"] == "NO_LEGAL_PREWINDOW_CONTEXT_FOR_R1E"
