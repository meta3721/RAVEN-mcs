"""Unit tests for E4 wo_inst reference-penalty final correction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from raven_mcs.aggregation.feasibility import validate_p2_lambdas
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import (
    RavenAggregator,
    RavenWoInstAggregator,
    get_aggregator,
)
from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.e4.wo_inst_final.constants import E3_METHODS_HASH, EXPECTED_E3_LAMBDA_BETA
from raven_mcs.e4.wo_inst_final.design_audit import _classify, _set_hash


def _payload() -> WindowAggregateInput:
    return WindowAggregateInput(
        client_ids=["c0", "c1", "c2", "c3"],
        raw_counts=np.ones(4),
        total_masses=np.ones(4),
        compositions=np.array(
            [[0.9, 0.1, 0.2, 0.3], [0.1, 0.9, 0.8, 0.7]], dtype=np.float64
        ),
        beta_hat=np.array([0.1, 0.7, 0.1, 0.1], dtype=np.float64),
        staleness=np.array([0.0, 1.0, 0.5, 0.2]),
        variance_diag=np.array([1.0, 5.0, 1.0, 1.0]),
        debt=np.array([2.0, -1.5], dtype=np.float64),
        mu=np.array([0.5, 0.5], dtype=np.float64),
    )


def test_e3_lambda_beta_provenance_recovery_hash_bound():
    root = Path(__file__).resolve().parents[2]
    recovered = root / "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/recovered_source/methods.py"
    if not recovered.is_file():
        pytest.skip("recovered methods.py not yet materialized")
    assert hashlib.sha256(recovered.read_bytes()).hexdigest() == E3_METHODS_HASH
    freeze = json.loads(
        (root / "artifacts/e3_formal_runs_r1/E3_FORMAL_SOURCE_FREEZE.json").read_text(
            encoding="utf-8"
        )
    )
    assert (
        freeze["source_hashes"]["src/raven_mcs/aggregation/methods.py"] == E3_METHODS_HASH
    )
    text = recovered.read_text(encoding="utf-8")
    assert "lambda_beta: float = 1.0" in text
    assert "class RavenAggregator" in text


def test_per_seed_p2_parameter_identity_defaults():
    raven = RavenAggregator()
    assert raven.lambda_group == 1.0
    assert raven.lambda_beta == EXPECTED_E3_LAMBDA_BETA
    assert raven.lambda_variance == 0.1
    assert raven.lambda_staleness == 0.1


def test_wo_inst_exact_one_factor():
    raven = RavenAggregator()
    wo = RavenWoInstAggregator()
    assert wo.lambda_group == 0.0
    assert wo.lambda_beta == raven.lambda_beta == EXPECTED_E3_LAMBDA_BETA
    assert wo.lambda_variance == raven.lambda_variance
    assert wo.lambda_staleness == raven.lambda_staleness
    assert wo.instant_calibration is False
    assert raven.instant_calibration is True
    pol_r = get_method_policy("raven")
    pol_w = get_method_policy("raven_wo_inst")
    for f in (
        "uses_design_ratio",
        "uses_observation_ipw",
        "uses_usable_ipw",
        "uses_debt",
    ):
        assert getattr(pol_r, f) == getattr(pol_w, f)
    assert pol_w.uses_instant_calibration is False


def test_wo_inst_p2_on_and_debt_on():
    agg = RavenWoInstAggregator(e_min=1.0)
    alpha = agg.compute_server_weights(_payload())
    assert len(agg.solve_results) == 1
    assert abs(float(alpha.sum()) - 1.0) < 1e-8
    assert get_method_policy("raven_wo_inst").uses_debt is True
    validate_p2_lambdas(
        lambda_beta=1.0,
        lambda_group=0.0,
        max_server_learning_rate=1.0,
        instant_calibration=False,
    )


def test_eventtrace_equality_helper_hashes():
    a = _set_hash(["c1", "c0"])
    b = _set_hash(["c0", "c1"])
    assert a == b


def test_design_layer_difference_classifier_valid_support():
    et = {
        "opportunity": "a",
        "observed": "b",
        "usable": "c",
        "registered": "d",
    }
    full_w = {
        "p2_candidate": "p1",
        "positive_design_weight": "d1",
        "positive_final_weight": "f1",
        "aggregation": "g1",
    }
    wo_w = {
        "p2_candidate": "p2",
        "positive_design_weight": "d2",
        "positive_final_weight": "f2",
        "aggregation": "g2",
    }
    first, _reason, cls = _classify(et, et, full_w, wo_w)
    assert first == "p2_candidate"
    assert cls == "VALID_WEIGHT_SUPPORT_EFFECT"


def test_design_layer_classifier_scope_leakage():
    full_et = {
        "opportunity": "a",
        "observed": "b",
        "usable": "c",
        "registered": "d",
    }
    wo_et = dict(full_et)
    wo_et["observed"] = "b2"
    full_w = {
        "p2_candidate": "p",
        "positive_design_weight": "d",
        "positive_final_weight": "f",
        "aggregation": "g",
    }
    first, _reason, cls = _classify(full_et, wo_et, full_w, full_w)
    assert first == "observed"
    assert cls == "SCOPE_LEAKAGE"


def test_final_evidence_index_uniqueness_if_present():
    root = Path(__file__).resolve().parents[2]
    path = (
        root
        / "artifacts/e4_wo_inst_reference_penalty_final_correction_r1"
        / "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv"
    )
    if not path.is_file():
        pytest.skip("evidence index not yet written")
    import csv

    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 240
    keys = {(r["dataset"], r["seed"], r["method"]) for r in rows}
    assert len(keys) == 240


def test_superseded_run_selection_if_present():
    root = Path(__file__).resolve().parents[2]
    path = (
        root
        / "artifacts/e4_wo_inst_reference_penalty_final_correction_r1"
        / "E4_WO_INST_SUPERSEDED_PROVENANCE.csv"
    )
    if not path.is_file():
        pytest.skip("provenance not yet written")
    import csv

    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    gens = {int(r["generation"]) for r in rows}
    assert gens == {0, 1, 2}
    finals = [r for r in rows if int(r["generation"]) == 2]
    assert all(r["status"] == "FINAL_VALID_ONE_FACTOR" for r in finals)


def test_aggregator_registry_wo_inst():
    assert isinstance(get_aggregator("raven_wo_inst"), RavenWoInstAggregator)
