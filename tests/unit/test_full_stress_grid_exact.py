from pathlib import Path

import pandas as pd

from raven_mcs.sag.availability_stress import A_GRID

CERT = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"


def test_full_stress_grid_exact() -> None:
    cert = pd.read_csv(CERT)
    levels = sorted({round(float(x), 2) for x in cert["availability_level"].unique()})
    assert levels == [0.2, 0.4, 0.6, 0.8, 1.0]
    assert list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]
    assert set(cert["dataset"].unique()) == {"sensorscope", "uair"}
    for ds in ("sensorscope", "uair"):
        for a in A_GRID:
            n = int(((cert["dataset"] == ds) & (abs(cert["availability_level"] - a) < 1e-9)).sum())
            assert n > 0
