from pathlib import Path
import json
from raven_mcs.sag.target_law import pi_safe_rule_hash
ROOT = Path(__file__).resolve().parents[2]

def test_pi_safe_unchanged() -> None:
    frozen = json.loads((ROOT / "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json").read_text(encoding="utf-8"))
    assert frozen["hash"] == pi_safe_rule_hash()
    assert abs(float(frozen["quantile"]) - 0.10) < 1e-12
