"""C_real_support definition matches R1e attribution."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from raven_mcs.sag.oracle_ceiling import c_real_support_from_pairs

ROOT = Path(__file__).resolve().parents[2]


def test_oracle_real_support_definition() -> None:
    r1e = pd.read_csv(ROOT / "outputs/sag_g1_r1e/diagnostic/R1D_NONVACUITY_ATTRIBUTION_BY_WINDOW.csv")
    pred = pd.read_csv(ROOT / "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_PREDICTION.csv")
    row = r1e.loc[r1e["dataset"] == "sensorscope"].iloc[0]
    wid = int(row["window_id"])
    chunk = pred.loc[(pred["dataset"] == "sensorscope") & (pred["window_id"] == wid)]
    pos = chunk.loc[pd.to_numeric(chunk["pi_tar"], errors="coerce") > 0]
    c_real, _, _, _ = c_real_support_from_pairs(
        pos["pi_tar"].tolist(),
        pd.to_numeric(pos["pi_opp_realized"], errors="coerce").fillna(0).tolist(),
    )
    assert abs(c_real - float(row["C_real_support"])) < 1e-9
