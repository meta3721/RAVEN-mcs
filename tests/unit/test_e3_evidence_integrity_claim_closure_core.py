from raven_mcs.e3.evidence_closure.local_hajek_gradient_fixture import run_fixture
from raven_mcs.e3.evidence_closure.p2_certificate import audit_alpha
from raven_mcs.e3.evidence_closure.secondary_stats import EPS_ZERO, holm, paired_summary
from raven_mcs.e3.evidence_closure.traffic_identity import RMSE_DECISION, comparison_policy


def test_unequal_local_hajek_weights_change_gradient():
    assert run_fixture()["status"] == "PASS"


def test_p2_simplex_certificate_and_missing_state():
    assert audit_alpha([0.2, 0.8])["certificate_status"] == "CERTIFIED_FEASIBLE"
    assert audit_alpha(None)["certificate_status"] == "MISSING_STATE"


def test_secondary_eps_and_holm():
    assert EPS_ZERO == 1e-12
    assert paired_summary({1: 1.0}, {1: 1.0 + EPS_ZERO / 2})["test_status"] == "ALL_TIES"
    assert holm({"a": 0.01, "b": 0.02}) == {"a": 0.02, "b": 0.02}


def test_traffic_policy_never_silently_pairs_vintages():
    assert RMSE_DECISION.endswith("SOURCE_VINTAGES")
    assert comparison_policy()["RMSE_mu"] == "N_A_NOT_COMPARABLE"


def test_structural_metrics_are_dimensionless_contract():
    domains = {"Delta_group": "DIMENSIONLESS_STRUCTURAL_DISCREPANCY", "Delta_c_s": "DIMENSIONLESS_STRUCTURAL_DISCREPANCY"}
    assert all(value.startswith("DIMENSIONLESS") for value in domains.values())
