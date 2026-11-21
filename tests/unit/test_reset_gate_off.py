from raven_mcs.sag.r1l_state import certificate_step

def test_reset_gate_off() -> None:
    out = certificate_step(regime_certified=False, had_active_certified_regime=True, scores=list(range(40)), c_hat=0.9)
    assert out["certificate_state"] == "RESET"
    assert out["Gate"] is False
    assert out["C_LCB"] == 0.0
