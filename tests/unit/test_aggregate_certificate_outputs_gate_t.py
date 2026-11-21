from pathlib import Path

from raven_mcs.sag.r1l_state import certificate_step

ROOT = Path(__file__).resolve().parents[2]


def test_aggregate_certificate_outputs_gate_t() -> None:
    src = (ROOT / "src/raven_mcs/sag/aggregate_certificate.py").read_text(encoding="utf-8")
    assert "certificate_step" in src
    step = certificate_step(
        regime_certified=False,
        had_active_certified_regime=False,
        scores=[],
        c_hat=0.0,
    )
    assert "Gate" in step
    assert step["Gate"] is False
    agg = (ROOT / "src/raven_mcs/sag/r1l_design.py").read_text(encoding="utf-8")
    assert "Gate_t" in agg
