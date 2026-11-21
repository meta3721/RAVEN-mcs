from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_counterfactual_sweep() -> None:
    text = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1g.py").read_text(encoding="utf-8")
    assert "CF3" not in text
    assert "for duration in" not in text
    assert "E3V1_K_RISK" in text
