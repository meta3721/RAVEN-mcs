from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_window_close_receives_gate_t() -> None:
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    i = main.index(r"\label{alg:window_close}")
    j = main.index(r"\end{algorithm}", i)
    alg = main[i:j]
    assert r"\mathrm{Gate}_t" in alg
    assert "aggregate coverage certificate" in alg
    runner = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    assert "formal_decide_gate_and_design" in runner
    assert "FORMAL_GATE_MODE" in runner
