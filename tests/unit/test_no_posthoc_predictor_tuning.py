from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_posthoc_predictor_tuning() -> None:
    spec = (ROOT / "src/raven_mcs/sag/r1m_spec.py").read_text(encoding="utf-8")
    pred = (ROOT / "src/raven_mcs/sag/r1m_predictor.py").read_text(encoding="utf-8")
    assert "RIDGE_ALPHA = 1.0" in spec
    assert "if abs(float(ridge_alpha) - RIDGE_ALPHA)" in pred
    runner = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1m.py").read_text(encoding="utf-8")
    assert "GridSearch" not in runner
    assert "ridge_alpha = 10" not in pred
