from pathlib import Path

import pandas as pd

CERT = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"
SECONDARY = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/secondary/R1M_UAIR_A020_SECONDARY_AUDIT.csv"


def test_secondary_uair_a020_present() -> None:
    cert = pd.read_csv(CERT)
    hit = cert.loc[(cert["dataset"] == "uair") & (abs(cert["availability_level"] - 0.20) < 1e-9)]
    assert len(hit) == 53
    secondary = pd.read_csv(SECONDARY)
    assert len(secondary) == 53
