"""μ and π^{tar} under TARGET_LAW_RULE_V1 come from one ϖ."""

from __future__ import annotations

import numpy as np
import pytest

from raven_mcs.sag.deployment_groups import N_H_GROUPS
from raven_mcs.sag.target_law import COMPAT_ATOL, build_target_law_v1
from tests.unit.test_target_compatibility import _toy_atomic


def test_mu_pi_same_target_law() -> None:
    atomic, mapping, h_map = _toy_atomic()
    law = build_target_law_v1(atomic, mapping, h_map, dataset="toy")
    assert law.rule_id == "TARGET_LAW_RULE_V1"
    assert law.split == "test"
    assert law.uses_test_outcomes is False
    assert law.uses_test_public_metadata is True
    assert law.compatibility["passed"] is True
    assert law.compatibility["max_abs_error"] <= COMPAT_ATOL
    mu_from_varpi = np.zeros(N_H_GROUPS)
    for uid, w in law.varpi.items():
        mu_from_varpi[h_map[uid]] += w
    assert np.max(np.abs(law.mu - mu_from_varpi)) <= COMPAT_ATOL
    mu_from_pi = np.zeros(N_H_GROUPS)
    for key, mass in law.pi_target.items():
        mu_from_pi += float(mass) * law.share_ks_g[key]
    assert np.max(np.abs(law.mu - mu_from_pi)) <= COMPAT_ATOL
    train_ids = set(atomic.loc[atomic["split"] == "train", "unit_id"].astype(str))
    assert not (set(law.varpi) & train_ids)
    assert pytest.approx(float(sum(law.varpi.values())), abs=COMPAT_ATOL) == 1.0
