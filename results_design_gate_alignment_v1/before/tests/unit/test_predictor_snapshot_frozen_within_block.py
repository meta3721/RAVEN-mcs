from pathlib import Path

import pandas as pd

ART = Path(__file__).resolve().parents[2] / "results_sag_g1/round_r1m/audit/R1M_PREDICTOR_SNAPSHOT_AUDIT.csv"


def test_predictor_snapshot_frozen_within_block() -> None:
    frame = pd.read_csv(ART)
    assert not frame.empty
    assert bool(frame["frozen_within_block"].astype(bool).all())
    assert bool((frame["n_distinct_snapshot_hash"].astype(int) == 1).all())
