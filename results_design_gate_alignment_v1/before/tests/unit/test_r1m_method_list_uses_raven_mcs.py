from pathlib import Path

from raven_mcs.experiments.r1m_method_freeze import (
    DEFAULT_METHOD,
    PAPER_METHOD,
    R1M_METHODS,
    formal_cli_parser,
)

ROOT = Path(__file__).resolve().parents[2]


def test_r1m_method_list_uses_raven_mcs() -> None:
    assert PAPER_METHOD == "raven_mcs"
    assert R1M_METHODS[0] == "raven_mcs"
    freeze = (ROOT / "configs/sag_g1/r1m_method_freeze.json").read_text(encoding="utf-8")
    assert '"raven_mcs"' in freeze
    md = (ROOT / "results_sag_g1/round_r1l_v13/interface/R1L_V13_R1M_METHOD_FREEZE.md").read_text(
        encoding="utf-8"
    )
    assert "raven_mcs" in md
    assert "aggregate_coverage" in md
