from pathlib import Path
import json
from raven_mcs.sag.availability_stress import TAU_COV
ROOT = Path(__file__).resolve().parents[2]

def test_tau_cov_unchanged() -> None:
    th = json.loads((ROOT / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    assert float(th["tau_cov"]) == 0.05 == TAU_COV
