from pathlib import Path
from raven_mcs.sag.r1j_spec import MODEL_ID, predictor_spec_hash
ROOT = Path(__file__).resolve().parents[2]

def test_predictor_spec_frozen() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1j.py").read_text(encoding="utf-8")
    assert src.find("R1J_PREDICTOR_SPEC_FREEZE.md") < src.find("_fit_logistic(")
    text = (ROOT / "results_sag_g1/round_r1j/predictor/R1J_PREDICTOR_SPEC_FREEZE.md").read_text(encoding="utf-8")
    assert MODEL_ID in text
    assert predictor_spec_hash() in text
