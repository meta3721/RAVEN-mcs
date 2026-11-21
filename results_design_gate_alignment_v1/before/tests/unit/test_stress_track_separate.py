from pathlib import Path
import json
from raven_mcs.sag.availability_stress import PROTOCOL_VERSION
ROOT = Path(__file__).resolve().parents[2]

def test_stress_track_separate() -> None:
    assert PROTOCOL_VERSION == "E3V2_AVAIL_STRESS_V1"
    assert PROTOCOL_VERSION != "e3-v2-time-aligned-v1"
    payload = json.loads((ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json").read_text(encoding="utf-8"))
    assert payload["protocol_version"] == PROTOCOL_VERSION
    assert (ROOT / "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_BY_WINDOW.csv").is_file()
    assert not (ROOT / "results_sag_g1/round_r1g/oracle_stress").exists()
