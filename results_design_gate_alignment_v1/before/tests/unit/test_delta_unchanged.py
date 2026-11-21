from pathlib import Path
import json
from raven_mcs.sag.r1j_spec import DELTA_CAL
ROOT = Path(__file__).resolve().parents[2]

def test_delta_unchanged() -> None:
    th = json.loads((ROOT / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    assert float(th["delta_cal"]) == 0.05 == DELTA_CAL
