from raven_mcs.sag.r1l_spec import k_n
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_r1l_v11_k_orderstat_valid() -> None:
    assert k_n(19) == 19
    assert k_n(18) == 19
    text = (ROOT / "results_sag_g1/round_r1l_v11/proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md").read_text(encoding="utf-8")
    assert "S_{(k_n)}" in text or "S_{(k_n)}^{\\mathrm{cal}}" in text
