from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_theorem_conditional_on_assumption_A() -> None:
    blob = "\n".join(
        [
            (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8"),
            (ROOT / "src/raven_mcs/sag/r1l_theory.py").read_text(encoding="utf-8"),
        ]
    )
    assert "conditional on Assumption" in blob
