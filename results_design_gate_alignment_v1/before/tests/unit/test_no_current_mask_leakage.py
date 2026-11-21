from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_current_mask_leakage() -> None:
    feat = (ROOT / "src/raven_mcs/sag/r1m_features.py").read_text(encoding="utf-8")
    pred = (ROOT / "src/raven_mcs/sag/r1m_predictor.py").read_text(encoding="utf-8")
    assert "available_entities" not in feat
    assert "current_mask" not in feat
    assert "availability_mask" not in feat
    assert "current_mask" not in pred
