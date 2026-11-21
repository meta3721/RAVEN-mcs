from pathlib import Path

def test_aggregate_no_future_calibration() -> None:
    src = (Path(__file__).resolve().parents[2] / "src/raven_mcs/experiments/run_sag_g1_r1k.py").read_text(encoding="utf-8")
    assert src.find("same_a_q(residuals[af])") < src.find("residuals[af].append")
