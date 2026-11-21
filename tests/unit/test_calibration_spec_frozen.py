from pathlib import Path
from raven_mcs.sag.r1j_spec import CALIBRATION_ID, calibration_spec_hash
ROOT = Path(__file__).resolve().parents[2]

def test_calibration_spec_frozen() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1j.py").read_text(encoding="utf-8")
    assert src.find("R1J_CALIBRATION_SPEC.md") < src.find("same_a_q(")
    text = (ROOT / "results_sag_g1/round_r1j/calibration/R1J_CALIBRATION_SPEC.md").read_text(encoding="utf-8")
    assert CALIBRATION_ID in text
    assert calibration_spec_hash() in text
