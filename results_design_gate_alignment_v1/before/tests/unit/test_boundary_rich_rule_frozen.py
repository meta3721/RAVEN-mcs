from pathlib import Path
import json
from raven_mcs.sag.availability_stress import routing_rule_payload
ROOT = Path(__file__).resolve().parents[2]

def test_boundary_rich_rule_frozen() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1i.py").read_text(encoding="utf-8")
    assert src.find("R1I_BOUNDARY_RICH_RULE.md") < src.find("summarize_levels(")
    stored = json.loads((ROOT / "results_sag_g1/round_r1i/stress_spec/R1I_ROUTING_RULE.json").read_text(encoding="utf-8"))
    assert stored["BOUNDARY_RICH"]["fraction_safe_lo"] == routing_rule_payload()["BOUNDARY_RICH"]["fraction_safe_lo"]
