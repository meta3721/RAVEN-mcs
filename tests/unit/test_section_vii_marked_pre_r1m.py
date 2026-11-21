from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_section_vii_marked_pre_r1m() -> None:
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    eval_idx = main.index("\\section{Evaluation}")
    chunk = main[eval_idx : eval_idx + 800]
    assert "R1l-v1.1" in chunk
    assert "PRE-R1m" in chunk or "LEGACY" in chunk
    assert "must not be treated as validation of Theorem" in chunk
