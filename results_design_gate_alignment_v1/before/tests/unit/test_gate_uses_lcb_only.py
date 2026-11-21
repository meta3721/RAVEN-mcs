from pathlib import Path
from raven_mcs.sag.r1l_conformal import gate_on
from raven_mcs.sag.r1l_spec import TAU_COV

def test_gate_uses_lcb_only() -> None:
    assert gate_on(0.05, TAU_COV) is True
    assert gate_on(0.049, TAU_COV) is False
    iface = (Path(__file__).resolve().parents[2] / "src/raven_mcs/sag/r1l_theory.py").read_text(encoding="utf-8")
    assert "Gate = 1{C_LCB >= tau_cov}" in iface
    assert "Gate = 1{C_hat" not in iface
