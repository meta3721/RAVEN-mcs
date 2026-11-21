"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
from pathlib import Path

from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.sag.r1l_design import legacy_decide_gate_and_design

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_no_static_gate_override() -> None:
    rec = legacy_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.04, "tau_cov": 0.05},
        design_enabled=True,
        dataset_design_flag=1,
    )
    assert rec["Design_t"] == 0
    assert rec["static_flag_controls_design"] is False
    src = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    start = src.index("if mode == FORMAL_GATE_MODE:")
    end = src.index("LEGACY experiment / ablation path", start)
    assert "always_on" not in src[start:end]
    assert get_method_policy("raven_coverage_legacy").gate_mode != "always_on"
