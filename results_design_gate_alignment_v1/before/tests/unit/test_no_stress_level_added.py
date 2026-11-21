from pathlib import Path

import pandas as pd

from raven_mcs.sag.availability_stress import A_GRID

CERT = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"


def test_no_stress_level_added() -> None:
    cert = pd.read_csv(CERT)
    extra = set(round(float(x), 2) for x in cert["availability_level"].unique()) - {round(float(a), 2) for a in A_GRID}
    assert not extra
    assert 0.50 not in set(round(float(x), 2) for x in cert["availability_level"].unique())
    assert 0.55 not in set(round(float(x), 2) for x in cert["availability_level"].unique())
    assert 0.65 not in set(round(float(x), 2) for x in cert["availability_level"].unique())
