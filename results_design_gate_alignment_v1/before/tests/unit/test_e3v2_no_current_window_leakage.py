import pytest
from e3_v2_context import ContextLeakageError, forbid_current_window_features, public_context_from_start


def test_e3v2_no_current_window_leakage() -> None:
    public_context_from_start("2007-01-01T00:00:00+00:00")
    with pytest.raises(ContextLeakageError):
        forbid_current_window_features({"current_R": 1})
    with pytest.raises(ContextLeakageError):
        forbid_current_window_features({"current_O": 1, "hour_of_day": 3})
