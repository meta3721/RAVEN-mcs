from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_prop1_proof_complete() -> None:
    text = (ROOT / "results_sag_g1/round_r1l/proofs/PROP1_POSITIVE_PAIRWISE_LCB_BARRIER.md").read_text(encoding="utf-8")
    assert "Complete proof" in text
    assert "Proof sketch" not in text
    assert "deterministic pre-window" in text
