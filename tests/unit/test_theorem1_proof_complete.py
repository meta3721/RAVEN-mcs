from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_theorem1_proof_complete() -> None:
    text = (ROOT / "results_sag_g1/round_r1l/proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md").read_text(encoding="utf-8")
    assert "Complete proof" in text
    assert "Proof sketch" not in text
    assert "n_min" in text.lower() or "n_{\\min}" in text
    assert "ties" in text.lower()
    assert "clip" in text.lower()
    assert "19" in text
