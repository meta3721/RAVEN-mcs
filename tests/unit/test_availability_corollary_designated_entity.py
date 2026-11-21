from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _texts() -> str:
    parts = [
        ROOT / "results_sag_g1/round_r1l_v11/proofs/COROLLARY1_AVAILABILITY_BARRIER.md",
        ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex",
        ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex",
    ]
    return "\n".join(p.read_text(encoding="utf-8") for p in parts if p.is_file())


def test_availability_corollary_designated_entity() -> None:
    text = _texts()
    assert "designated" in text.lower()
    assert "e(i)" in text or r"e(i)" in text
    assert r"X_{i,t}>0" in text or "X_{i,t}>0" in text
    assert "A_{e(i)" in text


def test_availability_corollary_no_atleast_one_overclaim() -> None:
    text = _texts()
    assert "at least one hidden" not in text.lower()
    assert "does not claim" in text.lower() or "do not claim" in text.lower() or "does NOT claim" in text
