from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_r1m_restart_defined() -> None:
    text = (ROOT / "results_sag_g1/round_r1l/interface/R1L_POST_THEORY_RESTART_PROTOCOL.md").read_text(encoding="utf-8")
    assert "R1m" in text
    assert "n_min = 19" in text
    assert "STOP before SAG" in text
    assert "5-seed" in text
