from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_no_proof_sketch() -> None:
    proofs = ROOT / "results_sag_g1/round_r1l/proofs"
    for p in proofs.glob("*.md"):
        assert "Proof sketch" not in p.read_text(encoding="utf-8")
