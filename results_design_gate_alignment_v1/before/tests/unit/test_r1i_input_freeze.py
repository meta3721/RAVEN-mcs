from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_r1i_input_freeze() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1i/R1I_INPUT_FREEZE_MANIFEST.csv")
    assert (frame["sha256"] != "MISSING").all()
    roles = set(frame["role"].astype(str))
    assert {"E3_V2", "TARGET_LAW", "PI_SAFE", "TAU", "BOUNDARY"} <= roles
