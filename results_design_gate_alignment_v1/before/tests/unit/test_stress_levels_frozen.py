from pathlib import Path
import json
from raven_mcs.sag.availability_stress import A_GRID, stress_level_payload
ROOT = Path(__file__).resolve().parents[2]

def test_stress_levels_frozen() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1i.py").read_text(encoding="utf-8")
    assert src.find("R1I_STRESS_LEVEL_FREEZE.md") < src.find("stressed_window(")
    stored = json.loads((ROOT / "results_sag_g1/round_r1i/stress_spec/R1I_STRESS_LEVEL.json").read_text(encoding="utf-8"))
    assert stored["A_GRID"] == list(A_GRID) == stress_level_payload()["A_GRID"]
