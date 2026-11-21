from pathlib import Path
from raven_mcs.sag.stress_mask import mask_rule_hash
ROOT = Path(__file__).resolve().parents[2]

def test_r1j_mask_unchanged() -> None:
    stored = (ROOT / "results_sag_g1/round_r1i/stress_masks/R1I_AVAILABILITY_MASK_HASH.txt").read_text(encoding="utf-8").strip()
    assert stored == mask_rule_hash()
