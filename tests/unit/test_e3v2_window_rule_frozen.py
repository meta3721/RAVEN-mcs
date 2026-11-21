from pathlib import Path
from e3_v2_protocol import window_rule_hash, window_rule_payload

ROOT = Path(__file__).resolve().parents[2]


def test_e3v2_window_rule_frozen() -> None:
    stored = (ROOT / "results_sag_g1/round_r1g/e3v2_spec/E3V2_WINDOW_RULE_HASH.txt").read_text(encoding="utf-8").strip()
    assert stored == window_rule_hash()
    assert window_rule_payload()["chosen_from_r1f_oracle"] is False
    assert window_rule_payload()["window_duration_hours"] == 1
