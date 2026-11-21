from pathlib import Path

def test_no_future_calibration() -> None:
    src = (Path(__file__).resolve().parents[2] / "src/raven_mcs/experiments/run_sag_g1_r1j.py").read_text(encoding="utf-8")
    assert "same_a_q(residuals_a[af])" in src
    assert src.find("same_a_q(residuals_a[af])") < src.find("residuals_a[af].append")
