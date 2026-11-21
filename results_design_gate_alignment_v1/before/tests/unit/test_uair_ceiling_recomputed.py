"""U-Air oracle ceiling recomputed from artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_uair_ceiling_recomputed() -> None:
    summary = pd.read_csv(ROOT / "results_sag_g1/round_r1f/summary/ORACLE_COVERAGE_CEILING_SUMMARY.csv")
    r1e = pd.read_csv(ROOT / "outputs/sag_g1_r1e/diagnostic/R1D_NONVACUITY_ATTRIBUTION_SUMMARY.csv")
    ua = summary.loc[summary["dataset"] == "uair"].iloc[0]
    r1e_ua = r1e.loc[r1e["dataset"] == "uair"].iloc[0]
    assert abs(float(ua["mean_C_real_support"]) - float(r1e_ua["mean_C_real_support"])) < 1e-6
    assert ua["compatibility"] in {"E3_THRESHOLD_COMPATIBLE", "E3_THRESHOLD_MARGINAL", "E3_THRESHOLD_INCOMPATIBLE"}
