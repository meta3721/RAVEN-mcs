"""C_oracle_safe uses pi_safe threshold on realized opportunity."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from raven_mcs.sag.oracle_ceiling import c_oracle_safe_from_pairs

ROOT = Path(__file__).resolve().parents[2]


def test_oracle_safe_definition() -> None:
    pred = pd.read_csv(ROOT / "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_PREDICTION.csv")
    r1f = pd.read_csv(ROOT / "results_sag_g1/round_r1f/oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv")
    row = r1f.loc[(r1f["dataset"] == "uair") & (r1f["is_warmup_eligible"])].iloc[0]
    wid = int(row["window_id"])
    chunk = pred.loc[(pred["dataset"] == "uair") & (pred["window_id"] == wid)]
    pos = chunk.loc[pd.to_numeric(chunk["pi_tar"], errors="coerce") > 0]
    c_oracle, _ = c_oracle_safe_from_pairs(
        pos["pi_tar"].tolist(),
        pd.to_numeric(pos["pi_opp_realized"], errors="coerce").fillna(0).tolist(),
        float(row["pi_safe"]),
    )
    assert abs(c_oracle - float(row["C_oracle_safe"])) < 1e-9
