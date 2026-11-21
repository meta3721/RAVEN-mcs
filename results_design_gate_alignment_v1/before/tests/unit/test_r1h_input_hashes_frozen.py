from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_r1h_input_hashes_frozen() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1h/R1H_INPUT_FREEZE_MANIFEST.csv")
    assert (frame["sha256"] != "MISSING").all()
    assert (frame["frozen"] == True).all() or frame["frozen"].astype(str).str.lower().isin(["true", "1"]).all()
