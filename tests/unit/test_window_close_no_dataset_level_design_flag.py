from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_window_close_no_dataset_level_design_flag() -> None:
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    i = main.index(r"\label{alg:window_close}")
    j = main.index(r"\end{algorithm}", i)
    alg = main[i:j]
    assert "dataset-level Design flag" not in alg
    assert "Design is enabled for this dataset" not in alg
    assert "dataset_name" not in alg
