from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_source_snapshot_contains_window_close() -> None:
    frame = pd.read_csv(
        ROOT / "results_sag_g1/round_r1l_v12/source_snapshot/R1L_V12_SOURCE_SNAPSHOT_MANIFEST.csv"
    )
    names = " ".join(frame["component"].astype(str).tolist() + frame["source_path"].astype(str).tolist())
    assert "window_runner" in names
    assert "main.tex" in names or "main_tex" in names
    main = (ROOT / "results_sag_g1/round_r1l_v12/source_snapshot/main.tex").read_text(encoding="utf-8")
    assert r"\label{alg:window_close}" in main
    assert r"\mathrm{Gate}_t" in main
    runner = (ROOT / "results_sag_g1/round_r1l_v12/source_snapshot/window_runner.py").read_text(
        encoding="utf-8"
    )
    assert "apply_formal_design_zeta" in runner
