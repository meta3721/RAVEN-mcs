"""Formal C_cov <= C_oracle_safe when joint-valid."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from raven_mcs.sag.oracle_ceiling import NUM_TOL

ROOT = Path(__file__).resolve().parents[2]


def test_formal_cov_le_oracle_safe_when_joint_valid() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1f/oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv")
    warm = frame.loc[frame["is_warmup_eligible"] == True]  # noqa: E712
    valid = warm.loc[warm["C_cov_r1d"].notna()]
    assert (valid["C_cov_r1d"] <= valid["C_oracle_safe"] + NUM_TOL).all()
