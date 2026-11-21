from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_section_vii_remains_pre_r1m_legacy() -> None:
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    eval_idx = main.index(r"\section{Evaluation}")
    chunk = main[eval_idx : eval_idx + 1200]
    assert "PRE-R1m" in chunk or "LEGACY" in chunk
    assert "R1l-v1.2" in chunk
    assert "do not validate the R1l aggregate certificate" in chunk
    assert "must not be treated as validation of Theorem" in chunk
