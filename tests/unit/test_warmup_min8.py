from pathlib import Path
import pandas as pd
from raven_mcs.sag.r1j_spec import LOOKBACK_MIN
ROOT = Path(__file__).resolve().parents[2]

def test_warmup_min8() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1j/certificate/R1J_JOINT_VALIDITY_BY_WINDOW.csv")
    elig = frame.loc[frame["eligible_after_warmup"].astype(str).str.lower().isin(["true", "1"])]
    assert (elig["calibration_history_size"] >= LOOKBACK_MIN).all()
