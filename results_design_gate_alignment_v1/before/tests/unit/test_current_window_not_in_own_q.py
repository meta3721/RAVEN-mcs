from pathlib import Path

import pandas as pd

BUF = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/audit/R1M_CALIBRATION_BUFFER_AUDIT.csv"


def test_current_window_not_in_own_q() -> None:
    buf = pd.read_csv(BUF)
    assert not bool(buf["current_window_in_buffer"].astype(bool).any())
