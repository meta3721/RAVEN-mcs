from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_no_dynamic_cov_run() -> None:
    payload = json.loads((ROOT / "results_sag_g1/round_r1h/summary/R1H_VERDICT.json").read_text(encoding="utf-8"))
    assert payload.get("dynamic_cov_run") is False
    r1i = ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json"
    if r1i.is_file():
        payload = json.loads(r1i.read_text(encoding="utf-8"))
        assert payload.get("dynamic_cov_run") is False
