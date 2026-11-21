from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_r1l_v11_randomized_rank_ties() -> None:
    text = (ROOT / "results_sag_g1/round_r1l_v11/proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md").read_text(encoding="utf-8")
    app = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex").read_text(encoding="utf-8")
    blob = text + app
    assert "Continuous" in blob
    assert "uniform" in blob.lower()
    assert "R_t" in blob
