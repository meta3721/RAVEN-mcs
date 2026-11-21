from pathlib import Path

import pandas as pd

from raven_mcs.sag.r1l_design import design_from_gate

CERT = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"


def test_design_equals_gate() -> None:
    assert design_from_gate(1) == 1
    assert design_from_gate(0) == 0
    cert = pd.read_csv(CERT)
    assert (cert["Gate_t"].astype(int).to_numpy() == cert["Design_t"].astype(int).to_numpy()).all()
