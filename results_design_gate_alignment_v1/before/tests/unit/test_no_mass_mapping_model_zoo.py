from pathlib import Path

def test_no_mass_mapping_model_zoo() -> None:
    src = (Path(__file__).resolve().parents[2] / "src/raven_mcs/sag/r1k_scale.py").read_text(encoding="utf-8")
    for banned in ("median_positive", "quantile-positive", "lognormal", "Ridge", "RandomForest"):
        assert banned not in src
    assert "hat_pi_old" in src and "hat_pi_cond" in src
