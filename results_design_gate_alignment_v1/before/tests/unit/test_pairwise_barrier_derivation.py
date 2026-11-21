from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_pairwise_barrier_derivation() -> None:
    text = (ROOT / "results_sag_g1/round_r1k/pairwise_barrier/PAIRWISE_POSITIVE_LCB_BARRIER_DERIVATION.md").read_text(encoding="utf-8")
    assert "deterministic pre-window" in text.lower() or "Deterministic pre-window" in text
    assert "1-delta" in text or "1-\\delta" in text
    assert "current mask" in text.lower() or "mask identity" in text
