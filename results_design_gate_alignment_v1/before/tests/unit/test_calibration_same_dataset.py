from pathlib import Path

import pandas as pd

BUF = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/audit/R1M_CALIBRATION_BUFFER_AUDIT.csv"
CERT = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"


def test_calibration_same_dataset() -> None:
    cert = pd.read_csv(CERT)
    buf = pd.read_csv(BUF)
    assert buf["cross_a_score_count"].astype(int).sum() == 0
    tracks = cert.groupby(["dataset", "availability_level", "block_id"])
    for _, chunk in tracks:
        ids = set(zip(chunk["dataset"], chunk["availability_level"]))
        assert len(ids) == 1
