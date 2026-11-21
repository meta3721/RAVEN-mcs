from pathlib import Path
import json
from raven_mcs.sag.r1j_spec import LOGISTIC_C, LOOKBACK_L
ROOT = Path(__file__).resolve().parents[2]

def test_no_predictor_retuning_after_results() -> None:
    payload = json.loads((ROOT / "results_sag_g1/round_r1j/summary/R1J_VERDICT.json").read_text(encoding="utf-8"))
    assert payload.get("predictor_retuned") is False
    spec = json.loads((ROOT / "results_sag_g1/round_r1j/predictor/R1J_PREDICTOR_SPEC.json").read_text(encoding="utf-8"))
    assert spec["C"] == LOGISTIC_C and spec["lookback_L"] == LOOKBACK_L
