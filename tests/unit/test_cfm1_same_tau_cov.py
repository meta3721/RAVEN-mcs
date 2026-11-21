from pathlib import Path
import json
from raven_mcs.sag.cfm1 import TAU_COV
ROOT = Path(__file__).resolve().parents[2]

def test_cfm1_same_tau_cov() -> None:
    th = json.loads((ROOT / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    assert float(th["tau_cov"]) == 0.05 == TAU_COV
