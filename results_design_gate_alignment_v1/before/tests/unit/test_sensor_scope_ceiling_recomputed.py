"""SensorScope oracle ceiling recomputed: max below tau_cov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TAU = 0.05


def test_sensor_scope_ceiling_recomputed() -> None:
    summary = pd.read_csv(ROOT / "results_sag_g1/round_r1f/summary/ORACLE_COVERAGE_CEILING_SUMMARY.csv")
    ss = summary.loc[summary["dataset"] == "sensorscope"].iloc[0]
    assert float(ss["max_C_real_support"]) < TAU
    assert float(ss["max_C_oracle_safe"]) < TAU
    assert int(ss["n_oracle_pass"]) == 0
    assert ss["compatibility"] == "E3_THRESHOLD_INCOMPATIBLE"
