from pathlib import Path
import json
from raven_mcs.sag.target_law import PI_SAFE_RULE_V1, pi_safe_rule_hash

ROOT = Path(__file__).resolve().parents[2]


def test_e3v2_pi_safe_unchanged() -> None:
    assert PI_SAFE_RULE_V1["quantile"] == 0.10
    r1e = json.loads((ROOT / "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json").read_text(encoding="utf-8"))
    assert r1e["hash"] == pi_safe_rule_hash()
