from raven_mcs.sag.r1m_predictor import RIDGE_ALPHA as PRED_ALPHA
from raven_mcs.sag.r1m_spec import RIDGE_ALPHA


def test_ridge_alpha_fixed() -> None:
    assert RIDGE_ALPHA == 1.0
    assert PRED_ALPHA == 1.0
    text = __import__("pathlib").Path("src/raven_mcs/sag/r1m_predictor.py").read_text(encoding="utf-8")
    assert "ridge_alpha = 0.01" not in text
    assert "scan" not in text.lower() or "scan_alphas" in __import__("pathlib").Path("src/raven_mcs/sag/r1m_spec.py").read_text(encoding="utf-8")
