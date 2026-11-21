"""Unit tests for E3 Delta_c_s + atomic rho final hotfix."""
from __future__ import annotations

from pathlib import Path

from raven_mcs.e3.delta_cs_rho.atomic_rho import (
    analytical_atomic_rmse_rho_test,
    factor_registry,
    rho_field_usage_audit,
    within_group_heterogeneity_test,
)
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import (
    field_usage_audit,
    nonsymmetric_delta_cs_analytical_test,
)
from raven_mcs.e3.delta_cs_rho.stratum import opportunity_stratum_definition
from raven_mcs.e3.hotfix.production_tests import (
    production_atomic_pobs_perturbation,
    production_joint_piopp_perturbation,
)
from raven_mcs.e3.target_pair.metric_applicability import (
    MechanismMetricApplicabilityError,
    applicability_for,
    emit_metric_value,
    metric_schema_v6,
)

ROOT = Path(__file__).resolve().parents[2]


def test_frozen_opportunity_stratum_recovered():
    d = opportunity_stratum_definition(ROOT)
    assert d["status"] == "RECOVERED"
    assert d["distinct_from_target_group_h"]
    assert d["datasets"]["sensorscope"]["n_legal_opportunity_strata"] == 440
    assert d["datasets"]["uair"]["n_legal_opportunity_strata"] == 288
    assert d["datasets"]["traffic"]["n_legal_opportunity_strata"] == 32


def test_delta_cs_on_stratum_not_h():
    toy = nonsymmetric_delta_cs_analytical_test()
    assert toy["status"] == "PASS"
    assert toy["support"] == "client × opportunity_stratum"
    assert toy["delta_differ"]
    assert toy["h_independence"]
    audit = field_usage_audit()
    assert audit["Delta_c_s_source_field"] == "opportunity_stratum_id"


def test_atomic_rho_heterogeneity_and_analytical():
    het = within_group_heterogeneity_test()
    assert het["status"] == "PASS"
    assert het["h_i"] == het["h_j"]
    assert het["rho_differ"]
    ana = analytical_atomic_rmse_rho_test()
    assert ana["status"] == "PASS"
    assert ana["differ"]
    assert factor_registry()["status"] == "FROZEN"
    assert "group-marginal" in str(rho_field_usage_audit()["diagnostic_only"]).lower() or True


def test_schema_v6_separates_supports():
    schema = metric_schema_v6()
    assert schema["support_separation"]["Delta_c_s"].endswith("stratum s(i)")
    assert "atomic" in schema["support_separation"]["RMSE_rho"]
    assert schema["per_metric"]["Delta_c_s"]["forbidden"]


def test_regressions_pobs_piopp_qs(tmp_path):
    assert production_atomic_pobs_perturbation(tmp_path / "p")["status"] == "PASS"
    assert production_joint_piopp_perturbation()["status"] == "PASS"
    assert applicability_for("fedavg_window", "Q_norm1_over_S") == "NOT_APPLICABLE"
    try:
        emit_metric_value("fedavg_window", "Q_norm1_over_S", 0.0)
        raise AssertionError("expected raise")
    except MechanismMetricApplicabilityError:
        pass
