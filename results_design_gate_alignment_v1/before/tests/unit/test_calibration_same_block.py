from pathlib import Path

import pandas as pd

BUF = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/audit/R1M_CALIBRATION_BUFFER_AUDIT.csv"


def test_calibration_same_block() -> None:
    buf = pd.read_csv(BUF)
    assert int(buf["cross_block_score_count"].astype(int).sum()) == 0
