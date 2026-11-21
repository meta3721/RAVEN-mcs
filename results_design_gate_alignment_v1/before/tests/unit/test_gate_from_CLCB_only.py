from pathlib import Path

import pandas as pd

from raven_mcs.sag.r1l_conformal import gate_on
from raven_mcs.sag.r1l_spec import TAU_COV

CERT = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"


def test_gate_from_CLCB_only() -> None:
    assert gate_on(0.049, TAU_COV) is False
    assert gate_on(0.05, TAU_COV) is True
    cert = pd.read_csv(CERT)
    certified = cert.loc[cert["state_before_decision"] == "CERTIFIED"]
    expect = (certified["C_LCB"].astype(float) >= TAU_COV).astype(int)
    assert (certified["Gate_t"].astype(int).to_numpy() == expect.to_numpy()).all()
    warm = cert.loc[cert["state_before_decision"].isin(["WARMUP", "RESET"])]
    if len(warm):
        assert int(warm["Gate_t"].astype(int).sum()) == 0
