from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_prop2_proof_complete() -> None:
    text = (ROOT / "results_sag_g1/round_r1l/proofs/PROP2_ARBITRARY_DRIFT_BOUNDARY.md").read_text(encoding="utf-8")
    assert "Complete proof" in text
    assert "World A" in text and "World B" in text
    assert "Proof sketch" not in text
