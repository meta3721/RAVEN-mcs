"""Gap decomposition identity holds."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_threshold_gap_decomposition_identity() -> None:
    decomp = pd.read_csv(ROOT / "results_sag_g1/round_r1f/oracle_ceiling/ORACLE_THRESHOLD_GAP_DECOMPOSITION.csv")
    assert np.allclose(decomp["decomposition_sum"], decomp["tau_minus_formal"], atol=1e-9, rtol=0)
