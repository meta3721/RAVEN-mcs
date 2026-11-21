"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_window_runner_calls_compute_certificates() -> None:
    src = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    assert "compute_certificates(" in src
    assert "legacy_decide_gate_and_design" in src
    assert "FORMAL_GATE_MODE" in src
