from pathlib import Path
import json
from e3_v2_protocol import TAU_COV

ROOT = Path(__file__).resolve().parents[2]


def test_e3v2_tau_cov_unchanged() -> None:
    th = json.loads((ROOT / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    assert float(th["tau_cov"]) == 0.05
    assert TAU_COV == 0.05
