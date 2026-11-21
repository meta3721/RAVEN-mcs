from pathlib import Path

import pandas as pd

BUF = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/audit/R1M_CALIBRATION_BUFFER_AUDIT.csv"


def test_no_future_score() -> None:
    buf = pd.read_csv(BUF)
    assert int(buf["future_score_count"].astype(int).sum()) == 0
