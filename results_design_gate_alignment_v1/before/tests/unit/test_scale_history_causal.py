from pathlib import Path

def test_scale_history_causal() -> None:
    src = (Path(__file__).resolve().parents[2] / "src/raven_mcs/experiments/run_sag_g1_r1k.py").read_text(encoding="utf-8")
    assert src.find("mean_mass_all(past)") < src.find("hist_mass[af][key].append")
    assert src.find("hat_pi_old(") < src.find("hist_mass[af][key].append")
