from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_availability_corollary_no_atleast_one_overclaim() -> None:
    texts = []
    for rel in (
        "results_sag_g1/round_r1l_v11/proofs/COROLLARY1_AVAILABILITY_BARRIER.md",
        "TO_OVERLEAF_paper_tmc_r1_clean/main.tex",
        "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex",
    ):
        texts.append((ROOT / rel).read_text(encoding="utf-8"))
    blob = "\n".join(texts)
    assert "at least one hidden" not in blob.lower()
