"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
from raven_mcs.sag.r1l_design import legacy_decide_gate_and_design


def test_legacy_dataset_name_cannot_control_design() -> None:
    off = legacy_decide_gate_and_design(
        {"certificate_state": "WARMUP", "C_LCB": 0.0, "tau_cov": 0.05},
        dataset="sensorscope",
    )
    on = legacy_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.06, "tau_cov": 0.05},
        dataset="uair",
    )
    assert off["Design_t"] == 0
    assert on["Design_t"] == 1
    assert off["dataset_name_controls_design"] is False
    assert on["dataset_name_controls_design"] is False
