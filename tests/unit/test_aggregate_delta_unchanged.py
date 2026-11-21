from pathlib import Path
import json
from raven_mcs.sag.r1k_spec import DELTA_CAL
ROOT = Path(__file__).resolve().parents[2]

def test_aggregate_delta_unchanged() -> None:
    th = json.loads((ROOT / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    spec = json.loads((ROOT / "results_sag_g1/round_r1k/aggregate_certificate/R1K_AGGREGATE_CALIBRATION_SPEC.json").read_text(encoding="utf-8"))
    assert float(th["delta_cal"]) == 0.05 == DELTA_CAL == float(spec["delta_cal"])
