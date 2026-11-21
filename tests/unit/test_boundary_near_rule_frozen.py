from pathlib import Path
import json
from raven_mcs.sag.availability_stress import BOUNDARY_NEAR_MARGIN
ROOT = Path(__file__).resolve().parents[2]

def test_boundary_near_rule_frozen() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1i.py").read_text(encoding="utf-8")
    assert src.find("R1I_BOUNDARY_NEAR_RULE.md") < src.find("summarize_levels(")
    stored = json.loads((ROOT / "results_sag_g1/round_r1i/stress_spec/R1I_BOUNDARY_NEAR_RULE.json").read_text(encoding="utf-8"))
    assert stored["abs_C_oracle_safe_minus_tau_cov"] == BOUNDARY_NEAR_MARGIN == 0.01
