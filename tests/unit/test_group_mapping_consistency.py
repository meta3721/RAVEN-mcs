"""mu, M, omega, B_srv, and Delta_group share the paper h(i) dimension."""

from __future__ import annotations

import numpy as np

from raven_mcs.metrics.distribution import delta_group
from raven_mcs.sag.certificates import b_tot_decomposition
from raven_mcs.sag.deployment_groups import N_H_GROUPS


def test_group_mapping_consistency_shapes() -> None:
    mu = np.array([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    m = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        dtype=np.float64,
    )
    alpha = np.array([0.5, 0.5], dtype=np.float64)
    omega = m @ alpha
    assert len(mu) == N_H_GROUPS
    assert m.shape[0] == len(mu)
    assert np.allclose(m.sum(axis=0), 1.0)
    assert omega.shape == (len(mu),)
    parts = b_tot_decomposition(
        delta_beta_ucb=0.1,
        delta_m_ucb=0.0,
        delta_v_ucb=0.0,
        b_m_pre=float(np.sqrt(8.0)),
        b_q=0.0,
        delta_a_ucb=0.0,
        delta_cal=0.05,
        n_groups=len(mu),
        lambda_group=1.0,
        lambda_beta=1.0,
        lambda_variance=0.1,
    )
    assert abs(parts["B_srv_UCB"] - (np.sqrt(4.0) * np.sqrt(8.0) * 0.1)) < 1e-12
    assert delta_group(omega, mu) >= 0.0
    assert omega.shape == mu.shape
