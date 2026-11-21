"""Unit tests for E3 pair/rho production consumption hotfix."""
from __future__ import annotations

from pathlib import Path

import pytest

from raven_mcs.e3.hotfix.production_tests import (
    piopp_semantic_identity,
    pobs_field_usage_audit,
    production_atomic_pobs_perturbation,
    production_joint_piopp_perturbation,
)
from raven_mcs.e3.target_pair.metric_applicability import (
    MechanismMetricApplicabilityError,
    applicability_for,
    emit_metric_value,
    mechanism_metric_applicability_matrix,
)
from raven_mcs.e3.target_pair.pair_state_v4 import nonsymmetric_delta_c_s_toy
from raven_mcs.e3.target_pair.rho_weights import (
    production_rho_analytical_test,
    rho_group_diagnostics,
)

ROOT = Path(__file__).resolve().parents[2]


def test_identity_is_delta_c_s_not_atomic_pair():
    assert applicability_for("raven", "Delta_c_s") == "APPLICABLE"
    assert applicability_for("raven", "Delta_pair") == "NOT_MATERIALIZED"
    toy = nonsymmetric_delta_c_s_toy()
    assert toy["structural_metric_name"] == "Delta_c_s"
    assert toy["status"] == "PASS"
    assert toy["delta_differ"]
    assert toy["pi_hat_differ"]


def test_rho_group_mass_not_inflated_by_n_g():
    test_groups = ["g0", "g0", "g0", "g1"]
    c = {"g0": 2.0, "g1": 6.0}
    diag = rho_group_diagnostics(test_groups=test_groups, delivered_group_counts=c)
    assert diag["status"] == "PASS"
    assert diag["max_normalization_error"] <= 1e-12
    out = production_rho_analytical_test()
    assert out["status"] == "PASS"
    assert out["n_g_does_not_inflate_rho_g"]
    assert out["differ"]


def test_production_atomic_pobs_perturbation(tmp_path):
    out = production_atomic_pobs_perturbation(tmp_path / "pobs")
    assert out["status"] == "PASS"
    assert out["weights_differ"]
    assert abs(out["mean_p"] - 0.5) < 1e-12


def test_production_joint_piopp_and_semantic():
    sem = piopp_semantic_identity()
    assert sem["identity"] == "A"
    out = production_joint_piopp_perturbation()
    assert out["status"] == "PASS"
    assert out["uses_joint_not_conditional_only"]
    assert out["error"] <= 1e-12


def test_pobs_field_usage_audit():
    audit = pobs_field_usage_audit()
    assert audit["status"] == "AUDITED"


def test_qs_na_for_non_debt_methods():
    assert applicability_for("fedavg_window", "Q_norm1_over_S") == "NOT_APPLICABLE"
    assert applicability_for("raven", "Q_norm1_over_S") == "APPLICABLE"
    with pytest.raises(MechanismMetricApplicabilityError):
        emit_metric_value("fedavg_window", "Q_norm1_over_S", 0.0)
    packed = emit_metric_value("fedavg_window", "Q_norm1_over_S", None)
    assert packed["value"] is None
    matrix = mechanism_metric_applicability_matrix()
    fedavg_q = next(
        r
        for r in matrix["rows"]
        if r["method"] == "fedavg_window" and r["metric"] == "Q_norm1_over_S"
    )
    assert fedavg_q["applicability"] == "NOT_APPLICABLE"
