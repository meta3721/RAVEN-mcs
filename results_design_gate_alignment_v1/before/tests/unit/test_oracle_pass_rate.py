"""Oracle pass rate matches summary artifact."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_oracle_pass_rate() -> None:
    by = pd.read_csv(ROOT / "results_sag_g1/round_r1f/oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv")
    summary = pd.read_csv(ROOT / "results_sag_g1/round_r1f/summary/ORACLE_COVERAGE_CEILING_SUMMARY.csv")
    for dataset in ("sensorscope", "uair"):
        warm = by.loc[(by["dataset"] == dataset) & (by["is_warmup_eligible"] == True)]  # noqa: E712
        rec = summary.loc[summary["dataset"] == dataset].iloc[0]
        assert int(rec["n_oracle_pass"]) == int(warm["oracle_pass"].sum())
        assert abs(float(rec["fraction_oracle_pass"]) - float(warm["oracle_pass"].mean())) < 1e-12
