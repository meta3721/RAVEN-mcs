"""Unit tests for E3 real-runner pair/oracle correctness closure."""
from __future__ import annotations

import numpy as np
import pytest

from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.real_runner.constants import M_MC, M_MC_CHECK, S_MAX
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
from raven_mcs.e3.real_runner.pair_state_v3 import toy_exact_delta_pair
from raven_mcs.e3.real_runner.simoracle_q import diagnostic_mc_check, estimate_q_true_mc
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3, sample_tau


def test_toy_delta_pair_exact_and_method_dependent():
    toy = toy_exact_delta_pair()
    assert toy["methods_differ"]
    assert toy["exact_match_A"]
    assert toy["exact_match_B"]
    assert toy["Delta_pair_A"] == pytest.approx(0.6)
    assert not np.allclose([0.8, 0.2], [0.2, 0.8])


def test_joint_pi_opp_sums_to_one():
    clients = ["c0", "c1"]
    strata = {"c0": ["c0::block0::weekday", "c0::block2::weekday"], "c1": ["c1::block1::weekday"]}
    pi = build_joint_pi_opp(clients, strata)
    assert abs(sum(pi.values()) - 1.0) < 1e-12
    assert all(v > 0 for v in pi.values())


def test_staleness_can_exceed_smax_and_rejects_u():
    rng = np.random.default_rng(0)
    ages = [sample_tau(rng, window_id=10, s_max=S_MAX)[1] for _ in range(500)]
    assert any(a > S_MAX for a in ages)
    out = compute_usable_r3(
        rng=np.random.default_rng(1),
        registration_time=10.05,
        window_deadline=11.0,
        window_id=10,
        s_max=S_MAX,
        has_observations=True,
        force_device_tier=2,
    )
    # Force a stale outcome by searching
    found_stale_u0 = False
    for seed in range(200):
        o = compute_usable_r3(
            rng=np.random.default_rng(seed),
            registration_time=10.05,
            window_deadline=11.0,
            window_id=10,
            s_max=S_MAX,
            has_observations=True,
            force_device_tier=2,
        )
        if o["tau"] > S_MAX:
            assert o["U"] == 0
            assert o["staleness_pass"] is False
            found_stale_u0 = True
            break
    assert found_stale_u0


def test_simoracle_mc_fixed_prestate_deterministic():
    pre = {
        "registration_time": 0.1,
        "window_deadline": 1.0,
        "window_id": 7,
        "s_max": S_MAX,
        "align_disadvantage": False,
        "has_observations": True,
        "device_tier_prior": 1,
    }
    a = estimate_q_true_mc(prestate=pre, m_mc=M_MC, mc_seed=42)
    b = estimate_q_true_mc(prestate=pre, m_mc=M_MC, mc_seed=42)
    assert a["M_MC"] == M_MC
    assert a["q_true"] == b["q_true"]
    assert 0.0 <= a["q_true"] <= 1.0
    diag = diagnostic_mc_check(prestate=pre, mc_seed=42)
    assert diag["M_MC_CHECK"] == M_MC_CHECK


def test_traffic_reuse_block_cannot_schedule():
    with pytest.raises(DuplicateReusedTrafficRunBlocked):
        assert_schedulable_e3_run(
            dataset="traffic",
            scenario="complete_aligned",
            seed=30001,
            method="raven",
        )
