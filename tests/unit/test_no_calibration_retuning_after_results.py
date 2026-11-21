from pathlib import Path
import json
from raven_mcs.sag.r1j_spec import DELTA_CAL, LOOKBACK_MIN
ROOT = Path(__file__).resolve().parents[2]

def test_no_calibration_retuning_after_results() -> None:
    payload = json.loads((ROOT / "results_sag_g1/round_r1j/summary/R1J_VERDICT.json").read_text(encoding="utf-8"))
    assert payload.get("calibration_retuned") is False
    spec = json.loads((ROOT / "results_sag_g1/round_r1j/calibration/R1J_CALIBRATION_SPEC.json").read_text(encoding="utf-8"))
    assert spec["delta_cal"] == DELTA_CAL and spec["lookback_min"] == LOOKBACK_MIN
