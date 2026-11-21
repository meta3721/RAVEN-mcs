from raven_mcs.sag.r1l_state import next_state

def test_certified_requires_nmin() -> None:
    assert next_state(regime_certified=True, n_cal=18, had_active_certified_regime=True) == "WARMUP"
    assert next_state(regime_certified=True, n_cal=19, had_active_certified_regime=True) == "CERTIFIED"
