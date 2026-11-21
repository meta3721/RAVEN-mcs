from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv"
SNAP = ROOT / "results_sag_g1/round_r1m/audit/R1M_PREDICTOR_SNAPSHOT_AUDIT.csv"


def test_predictor_refit_only_after_reset() -> None:
    cert = pd.read_csv(CERT)
    snap = pd.read_csv(SNAP)
    for (ds, a), chunk in cert.groupby(["dataset", "availability_level"]):
        hashes = chunk["snapshot_hash"].astype(str).tolist()
        blocks = chunk["block_id"].astype(int).tolist()
        for i in range(1, len(hashes)):
            if hashes[i] != hashes[i - 1]:
                assert blocks[i] == blocks[i - 1] + 1
                assert int(chunk["reset_trigger_after_window"].iloc[i - 1]) == 1
    assert set(snap["ridge_alpha"].astype(float).unique()) == {1.0}
