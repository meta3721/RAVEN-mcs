from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_r1j_input_freeze() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1j/R1J_INPUT_FREEZE_MANIFEST.csv")
    assert (frame["sha256"] != "MISSING").all()
