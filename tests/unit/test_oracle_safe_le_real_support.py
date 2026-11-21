"""C_oracle_safe <= C_real_support on all warm-up windows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from raven_mcs.sag.oracle_ceiling import NUM_TOL

ROOT = Path(__file__).resolve().parents[2]


def test_oracle_safe_le_real_support() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1f/oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv")
    warm = frame.loc[frame["is_warmup_eligible"] == True]  # noqa: E712
    assert (warm["C_oracle_safe"] <= warm["C_real_support"] + NUM_TOL).all()
