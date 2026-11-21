from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_no_calibration_run() -> None:
    payload = json.loads((ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json").read_text(encoding="utf-8"))
    assert payload.get("calibration_run") is False
    assert payload.get("calibration_repair_executed") is False
