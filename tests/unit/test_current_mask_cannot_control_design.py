"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
from raven_mcs.sag.r1l_design import legacy_decide_gate_and_design


def test_legacy_current_mask_cannot_control_design() -> None:
    rec = legacy_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.04, "tau_cov": 0.05},
        current_mask=1,
    )
    assert rec["Design_t"] == 0
    assert rec["current_mask_controls_design"] is False
