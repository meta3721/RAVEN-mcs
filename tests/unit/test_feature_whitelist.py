from pathlib import Path
import pandas as pd
from raven_mcs.sag.r1j_spec import FEATURE_NAMES
ROOT = Path(__file__).resolve().parents[2]

def test_feature_whitelist() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1j/predictor/R1J_FEATURE_WHITELIST.csv")
    allowed = set(frame.loc[frame["allowed"].astype(str).str.lower().isin(["true", "1"]), "feature"])
    assert set(FEATURE_NAMES) <= allowed
    assert "current_mask" in set(frame["feature"])
