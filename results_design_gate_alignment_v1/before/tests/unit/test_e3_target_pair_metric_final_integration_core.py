"""Unit tests for E3 target/pair/metric final integration."""
from __future__ import annotations

from pathlib import Path

import pytest

from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.target_pair.errors import PairWeightBindingError
from raven_mcs.e3.target_pair.metric_applicability import (
    MechanismMetricApplicabilityError,
    emit_metric_value,
)
from raven_mcs.e3.target_pair.oracle_consumption import (
    atomic_pobs_oracle_weights,
    joint_piopp_production_test,
)
from raven_mcs.e3.target_pair.pair_state_v4 import (
    analytical_delta_pair_toy,
    bind_alpha_by_client,
)
from raven_mcs.e3.target_pair.rho_weights import analytical_mu_rho_test
from raven_mcs.e3.target_pair.target_wiring import load_frozen_target_artifact

ROOT = Path(__file__).resolve().parents[2]


def test_sensorscope_uair_frozen_spatial_time_groups():
    ss = load_frozen_target_artifact(ROOT, "sensorscope")
    ua = load_frozen_target_artifact(ROOT, "uair")
    assert ss["n_groups"] == 220
    assert ua["n_groups"] == 144
    assert ss["n_groups"] != 4
    assert all("::" in g for g in ss["mu"])


def test_analytical_delta_pair_common_support():
    toy = analytical_delta_pair_toy()
    assert toy["exact_match"]
    assert toy["pi_hat_differ"]
    assert toy.get("delta_differ", True)
    assert toy["error_A"] <= 1e-12
    assert toy.get("structural_metric_name") == "Delta_c_s"


def test_alpha_binding_no_silent_uniform():
    class WM:
        alpha = [0.7, 0.3]
        active_clients = ["c0", "c1"]

    m = bind_alpha_by_client(WM())
    assert m == {"c0": 0.7, "c1": 0.3}

    class Bad:
        alpha = [1.0]
        active_clients = ["c0", "c1"]

    with pytest.raises(PairWeightBindingError):
        bind_alpha_by_client(Bad())


def test_rmse_mu_rho_analytical():
    out = analytical_mu_rho_test()
    assert out["status"] == "PASS"
    assert out["differ"]


def test_atomic_pobs_and_joint_piopp():
    assert atomic_pobs_oracle_weights(p1=0.2, p2=0.8)["status"] == "PASS"
    assert joint_piopp_production_test()["status"] == "PASS"


def test_central_na_not_fake_zero():
    with pytest.raises(MechanismMetricApplicabilityError):
        emit_metric_value("central_all", "Delta_c_s", 0.0)
    packed_cs = emit_metric_value("central_all", "Delta_c_s", None)
    assert packed_cs["value"] is None
    assert packed_cs["applicability"] == "NOT_APPLICABLE"
    packed_pair = emit_metric_value("central_all", "Delta_pair", None)
    assert packed_pair["value"] is None
    assert packed_pair["applicability"] == "NOT_MATERIALIZED"
    with pytest.raises(MechanismMetricApplicabilityError):
        emit_metric_value("fedavg_window", "Q_norm1_over_S", 0.0)


def test_traffic_reuse_guard():
    with pytest.raises(DuplicateReusedTrafficRunBlocked):
        assert_schedulable_e3_run(
            dataset="traffic", scenario="complete_aligned", seed=30001, method="raven"
        )
