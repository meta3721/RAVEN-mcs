from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_r1m_method_freeze_uses_raven_mcs() -> None:
    md = (ROOT / "results_sag_g1/round_r1l_v13/interface/R1L_V13_R1M_METHOD_FREEZE.md").read_text(
        encoding="utf-8"
    )
    assert "Formal paper method" in md or "formal paper method" in md.lower()
    assert "raven_mcs" in md
    assert "aggregate_coverage" in md
    assert "raven_mcs_formal" in md
    assert "not" in md.lower() or "alias" in md.lower()
