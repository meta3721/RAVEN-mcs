from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.sag.r1l_design import formal_decide_gate_and_design


def test_no_dataset_gate_override() -> None:
    rec = formal_decide_gate_and_design(
        {"certificate_state": "WARMUP", "C_LCB": 0.0},
        dataset="sensorscope",
    )
    assert rec["Design_t"] == 0
    assert rec["dataset_name_controls_design"] is False
    assert get_method_policy("raven_mcs").gate_mode == "aggregate_coverage"
