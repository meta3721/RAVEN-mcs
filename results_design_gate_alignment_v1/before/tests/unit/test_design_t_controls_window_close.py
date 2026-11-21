from pathlib import Path

import numpy as np

from raven_mcs.sag.r1l_design import DESIGN_OFF, DESIGN_ON, apply_formal_design_zeta

ROOT = Path(__file__).resolve().parents[2]


def test_design_t_controls_window_close() -> None:
    src = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    assert "apply_formal_design_zeta" in src
    zeta_on = apply_formal_design_zeta(np.array([2.0, 4.0]), 1)
    zeta_off = apply_formal_design_zeta(np.array([2.0, 4.0]), 0)
    assert np.allclose(zeta_on, [2.0, 4.0])
    assert np.allclose(zeta_off, [1.0, 1.0])
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    i = main.index(r"\label{alg:window_close}")
    j = main.index(r"\end{algorithm}", i)
    alg = main[i:j]
    assert r"\mathrm{Gate}_t=1" in alg
    assert "DESIGN" in DESIGN_ON and "OFF" in DESIGN_OFF
