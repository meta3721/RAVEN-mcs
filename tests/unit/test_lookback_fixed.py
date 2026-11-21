from raven_mcs.sag.r1j_spec import LOOKBACK_L, LOOKBACK_MIN

def test_lookback_fixed() -> None:
    assert LOOKBACK_L == 8
    assert LOOKBACK_MIN == 8
