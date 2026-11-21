"""R1-A Cases A–D: Δβ / ΔM / ΔV / service must be independent."""

from __future__ import annotations

import numpy as np
import pytest

from raven_mcs.sag.counterfactual_audit import metrics_from_raw_states


def test_case_a_beta_only() -> None:
    beta_d = np.array([0.8, 0.2])
    beta_0 = np.array([0.5, 0.5])
    m = np.array([[0.6, 0.4], [0.4, 0.6]], dtype=np.float64)
    v = np.diag([0.2, 0.3])
    alpha = np.array([0.5, 0.5])
    mets = metrics_from_raw_states(
        beta_d=beta_d, beta_0=beta_0, m_d=m, m_0=m, v_d=v, v_0=v,
        alpha_d=alpha, alpha_0=alpha,
    )
    assert mets["Delta_beta"] > 0
    assert mets["Delta_M"] == pytest.approx(0.0)
    assert mets["Delta_V"] == pytest.approx(0.0)


def test_case_b_m_only() -> None:
    beta = np.array([0.5, 0.5])
    m_d = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64)
    m_0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.float64)
    v = np.diag([0.2, 0.3])
    alpha = np.array([1.0, 0.0])
    mets = metrics_from_raw_states(
        beta_d=beta, beta_0=beta, m_d=m_d, m_0=m_0, v_d=v, v_0=v,
        alpha_d=alpha, alpha_0=alpha,
    )
    assert mets["Delta_beta"] == pytest.approx(0.0)
    assert mets["Delta_M"] > 0
    assert mets["Delta_V"] == pytest.approx(0.0)
    assert mets["service_diff_l1"] > 0
    assert mets["Delta_beta"] != pytest.approx(mets["Delta_M"])


def test_case_c_v_from_n_eff() -> None:
    beta = np.array([0.5, 0.5])
    m = np.array([[0.6, 0.4], [0.4, 0.6]], dtype=np.float64)
    v_d = np.diag([1.0 / 4.0 + 1e-4, 1.0 / 4.0 + 1e-4])
    v_0 = np.diag([1.0 / 1.0 + 1e-4, 1.0 / 1.0 + 1e-4])
    alpha = np.array([0.5, 0.5])
    mets = metrics_from_raw_states(
        beta_d=beta, beta_0=beta, m_d=m, m_0=m, v_d=v_d, v_0=v_0,
        alpha_d=alpha, alpha_0=alpha,
    )
    assert mets["Delta_V"] > 0
    assert mets["Delta_beta"] == pytest.approx(0.0)
    assert mets["Delta_M"] == pytest.approx(0.0)


def test_case_d_all_change_not_forced_equal() -> None:
    beta_d = np.array([0.9, 0.1])
    beta_0 = np.array([0.2, 0.8])
    m_d = np.array([[0.9, 0.1], [0.1, 0.9]], dtype=np.float64)
    m_0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.float64)
    v_d = np.diag([0.1, 0.2])
    v_0 = np.diag([0.8, 0.4])
    alpha_d = np.array([0.7, 0.3])
    alpha_0 = np.array([0.4, 0.6])
    mets = metrics_from_raw_states(
        beta_d=beta_d, beta_0=beta_0, m_d=m_d, m_0=m_0, v_d=v_d, v_0=v_0,
        alpha_d=alpha_d, alpha_0=alpha_0,
    )
    vals = [
        mets["Delta_beta"],
        mets["Delta_M"],
        mets["Delta_V"],
        mets["service_diff_l1"],
    ]
    assert all(v > 0 for v in vals)
    assert len({round(v, 12) for v in vals}) == 4
