from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _texts() -> str:
    files = [
        ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex",
        ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex",
        ROOT / "results_sag_g1/round_r1l_v11/proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md",
    ]
    return "\n".join(p.read_text(encoding="utf-8") for p in files if p.is_file())


def test_certified_does_not_imply_exchangeability() -> None:
    text = _texts()
    assert "does not prove" in text.lower()
    assert "CERTIFIED implies Assumption A" not in text
    assert "detector certifies exchangeability" not in text.lower()
    assert "passing the stability test proves" not in text.lower()


def test_theorem_conditional_on_assumption_A() -> None:
    text = _texts()
    assert "conditional on Assumption A" in text or "conditional on Assumption~" in text or "remains conditional" in text
