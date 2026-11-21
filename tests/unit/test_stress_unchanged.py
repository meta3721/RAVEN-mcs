from pathlib import Path
from raven_mcs.sag.availability_stress import A_GRID
from raven_mcs.sag.stress_mask import mask_rule_hash
ROOT = Path(__file__).resolve().parents[2]

def test_stress_unchanged() -> None:
    assert tuple(float(x) for x in A_GRID) == (1.00, 0.80, 0.60, 0.40, 0.20)
    stored = (ROOT / "results_sag_g1/round_r1i/stress_masks/R1I_AVAILABILITY_MASK_HASH.txt").read_text(encoding="utf-8").strip()
    assert stored == mask_rule_hash()
