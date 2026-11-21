from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_forbidden_claims_listed() -> None:
    text = (ROOT / "results_sag_g1/round_r1l/theory/R1L_FORBIDDEN_CLAIMS.md").read_text(encoding="utf-8")
    assert "n=8 is sufficient" in text
    assert "pairwise certificate remains the formal core" in text.lower() or "The pairwise certificate remains the formal core" in text
    assert "92.2%" in text
