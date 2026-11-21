from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_no_stress_created() -> None:
    payload = json.loads((ROOT / "results_sag_g1/round_r1h/summary/R1H_VERDICT.json").read_text(encoding="utf-8"))
    assert payload.get("coverage_stress_created") is False
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1h.py").read_text(encoding="utf-8")
    assert "availability drop" not in src.lower()
