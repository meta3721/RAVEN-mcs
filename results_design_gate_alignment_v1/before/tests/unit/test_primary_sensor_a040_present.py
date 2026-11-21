from pathlib import Path

import pandas as pd

CERT = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"
PRIMARY = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/primary/R1M_SENSORSCOPE_A040_PRIMARY_AUDIT.csv"


def test_primary_sensor_a040_present() -> None:
    cert = pd.read_csv(CERT)
    hit = cert.loc[(cert["dataset"] == "sensorscope") & (abs(cert["availability_level"] - 0.40) < 1e-9)]
    assert len(hit) == 62
    primary = pd.read_csv(PRIMARY)
    assert len(primary) == 62
