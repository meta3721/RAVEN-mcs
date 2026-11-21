from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_r1k_input_freeze() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1k/R1K_INPUT_FREEZE_MANIFEST.csv")
    assert (frame["sha256"] != "MISSING").all()
    assert (ROOT / "results_sag_g1/round_r1k/R1K_INPUT_FREEZE_AUDIT.md").is_file()
