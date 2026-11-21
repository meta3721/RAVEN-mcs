"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_formal_runner_no_static_gate_lookup() -> None:
    src = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    start = src.index("if mode == FORMAL_GATE_MODE:")
    end = src.index("LEGACY experiment / ablation path", start)
    formal = src[start:end]
    assert "uses_design_ratio" not in formal
    assert "always_on" not in formal
    assert "dataset_name" not in formal
    assert "legacy_decide_gate_and_design" in formal
    design = (ROOT / "src/raven_mcs/sag/r1l_design.py").read_text(encoding="utf-8")
    assert "dataset_name_controls_design" in design
    assert "Design_t := Gate_t" in design
