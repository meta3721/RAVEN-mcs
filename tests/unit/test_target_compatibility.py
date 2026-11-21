"""μ and π^{tar} must come from one frozen train-split atomic law."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from raven_mcs.sag.deployment_groups import N_H_GROUPS
from raven_mcs.sag.target_law import COMPAT_ATOL, build_frozen_atomic_target_law


def _toy_atomic() -> tuple[pd.DataFrame, dict[str, str], dict[str, int]]:
    rows = []
    h_map: dict[str, int] = {}
    for split, prefix, n in (("train", "tr", 8), ("test", "te", 8)):
        for i in range(n):
            uid = f"{prefix}{i}"
            h = i % N_H_GROUPS
            h_map[uid] = h
            rows.append(
                {
                    "unit_id": uid,
                    "split": split,
                    "support_flag": True,
                    "spatial_id": f"st{i % 4}",
                    "opportunity_stratum": f"s{i % 4}",
                    "absolute_time": f"2020-01-01T{6 * h:02d}:00:00Z",
                    "y": 100.0 + i if split == "test" else 0.0,
                }
            )
    mapping = {f"st{i}": f"client-{i}" for i in range(4)}
    return pd.DataFrame(rows), mapping, h_map


def test_target_compatibility() -> None:
    atomic, mapping, h_map = _toy_atomic()
    law = build_frozen_atomic_target_law(atomic, mapping, h_map, dataset="toy")
    assert law.compatibility["passed"] is True
    assert law.compatibility["max_abs_error"] <= COMPAT_ATOL
    assert law.compatibility["sum_varpi"] == pytest.approx(1.0, abs=COMPAT_ATOL)
    assert law.compatibility["sum_pi"] == pytest.approx(1.0, abs=COMPAT_ATOL)
    assert float(law.mu.sum()) == pytest.approx(1.0, abs=COMPAT_ATOL)
    rebuilt = np.zeros(N_H_GROUPS)
    for uid, w in law.varpi.items():
        rebuilt[h_map[uid]] += w
    assert np.max(np.abs(law.mu - rebuilt)) <= COMPAT_ATOL
    mu_from_pi = np.zeros(N_H_GROUPS)
    for key, mass in law.pi_target.items():
        mu_from_pi += float(mass) * law.share_ks_g[key]
    assert np.max(np.abs(law.mu - mu_from_pi)) <= COMPAT_ATOL
    assert law.uses_test_split_mass is False
    assert law.uses_test_outcomes is False
    assert law.split == "train"
