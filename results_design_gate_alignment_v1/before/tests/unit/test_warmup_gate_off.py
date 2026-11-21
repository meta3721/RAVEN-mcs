from raven_mcs.sag.r1l_state import certificate_step

def test_warmup_gate_off() -> None:
    out = certificate_step(regime_certified=True, had_active_certified_regime=True, scores=list(range(8)), c_hat=0.9)
    assert out["certificate_state"] == "WARMUP"
    assert out["Gate"] is False
    assert out["C_LCB"] == 0.0
