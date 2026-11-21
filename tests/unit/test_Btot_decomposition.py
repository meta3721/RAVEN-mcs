"""B_tot = B_srv + 2 δ_A + 2 δ_cal."""

from __future__ import annotations

import pytest

from raven_mcs.sag.certificates import b_tot_decomposition, b_tot_from_parts


def test_btot_matches_parts() -> None:
    parts = b_tot_decomposition(
        delta_beta_ucb=0.2,
        delta_m_ucb=0.1,
        delta_v_ucb=0.05,
        b_m_pre=3.0,
        b_q=1.0,
        delta_a_ucb=0.1,
        delta_cal=0.05,
        n_groups=4,
        lambda_group=1.0,
        lambda_beta=1.0,
        lambda_variance=0.1,
    )
    assert parts["B_tot_UCB"] == pytest.approx(
        b_tot_from_parts(parts["B_srv_UCB"], 0.1, 0.05)
    )
    assert parts["B_tot_UCB"] == pytest.approx(
        parts["B_srv_UCB"] + parts["active_set_term"] + parts["cal_failure_term"]
    )
    assert parts["D_alpha_UCB"] == pytest.approx(
        parts["term_beta"] + parts["term_M"] + parts["term_V"]
    )
