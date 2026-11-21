"""Semantic tests for E3 alignment closure (no performance Canary)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.semantic_alignment.constants import CANARY_SEED, EPS_ZERO, FORMAL_SEEDS, M_MC
from raven_mcs.e3.semantic_alignment.stage2_usable import compute_usable_indicator
from raven_mcs.e3.semantic_alignment.target_semantics import parse_time_block
from raven_mcs.metrics.distribution import delta_pair

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1"


def test_sensorscope_spatial_time_not_time_only():
    ss = json.loads((ART / "E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json").read_text(encoding="utf-8"))
    assert ss["status"] == "SENSORSCOPE_TARGET_SEMANTICS_READY"
    assert ss["n_groups"] > 4
    assert ss["uses_e1_time_only_target"] is False
    assert all("::" in g for g in ss["mu"])
    assert abs(ss["mu_sum"] - 1.0) < 1e-9


def test_uair_spatial_time_not_time_only():
    ua = json.loads((ART / "E3_UAIR_TARGET_SEMANTICS_R2.json").read_text(encoding="utf-8"))
    assert ua["status"] == "UAIR_TARGET_SEMANTICS_READY"
    assert ua["n_groups"] > 4
    assert all(parse_time_block(g) in {0, 1, 2, 3} for g in ua["mu"])


def test_mu_not_train_label_derived_markers():
    for name in ("E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json", "E3_UAIR_TARGET_SEMANTICS_R2.json"):
        payload = json.loads((ART / name).read_text(encoding="utf-8"))
        assert "training label magnitude" in payload["mu_not_from"]
        assert "uniform over supported TEST atomic units" in payload["mu_construction"]


def test_stage2_deadline_and_failures():
    rng = np.random.default_rng(0)
    # compute fail
    out = compute_usable_indicator(
        rng=rng, registration_time=0.1, window_deadline=1.0, window_id=0, has_observations=False
    )
    assert out["U"] == 0
    # force deadline miss via huge registration near deadline with long delays
    rng = np.random.default_rng(1)
    out2 = compute_usable_indicator(
        rng=rng, registration_time=0.99, window_deadline=1.0, window_id=0, has_observations=True
    )
    if out2["T_arr"] >= out2["window_deadline"]:
        assert out2["U"] == 0
        assert out2["deadline_pass"] is False


def test_probability_object_no_aliasing():
    reg = json.loads((ART / "E3_PROBABILITY_OBJECT_REGISTRY.json").read_text(encoding="utf-8"))
    names = [o["name"] for o in reg["objects"]]
    assert len(names) == len(set(names))
    fields = [reg["field_separation"][k] for k in ("pi_opp_true", "p_obs_true", "q_use_true", "U_realized")]
    assert len(fields) == len(set(fields))


def test_direction_diagnostic_pass():
    diag = json.loads((ART / "E3_COMPLETE_ALIGNED_DIRECTION_DIAGNOSTIC.json").read_text(encoding="utf-8"))
    assert diag["status"] == "PASS"
    assert all(r["direction_pass"] for r in diag["rows"])


def test_simoracle_mmc():
    oracle = json.loads((ART / "E3_SIMORACLE_PROTOCOL_R2.json").read_text(encoding="utf-8"))
    assert oracle["M_MC"] == M_MC == 2000


def test_pair_runner_integration_files():
    status = json.loads((ART / "E3_PAIR_STATE_RUNNER_STATUS.json").read_text(encoding="utf-8"))
    assert status["status"] == "PAIR_STATE_RUNNER_INTEGRATED"
    pair = ART / "runner_dry/sensorscope/raven/pair_state.parquet"
    summary = ART / "runner_dry/sensorscope/raven/pair_metric_summary.json"
    assert pair.is_file() and summary.is_file()
    frame = pd.read_parquet(pair)
    assert len(frame) > 0
    assert "estimated_pair_mass" in frame.columns
    assert np.isfinite(frame["estimated_pair_mass"]).all()


def test_pair_metric_reconstructs():
    summary = json.loads(
        (ART / "runner_dry/sensorscope/raven/pair_metric_summary.json").read_text(encoding="utf-8")
    )
    frame = pd.read_parquet(ART / "runner_dry/sensorscope/raven/pair_state.parquet")
    groups = sorted(frame["pair_id"].unique())
    est = frame.groupby("pair_id")["estimated_pair_mass"].sum().reindex(groups).fillna(0.0).to_numpy()
    tar = frame.groupby("pair_id")["target_pair_mass"].mean().reindex(groups).fillna(0.0).to_numpy()
    est = est / est.sum()
    tar = tar / tar.sum()
    assert summary["Delta_pair"] == pytest.approx(delta_pair(est, tar), rel=0, abs=1e-9)


def test_central_runner_ready():
    central = json.loads((ART / "E3_CENTRAL_RUNNER_INTEGRATION_R2.json").read_text(encoding="utf-8"))
    assert central["status"] == "CENTRAL_RUNNER_READY"
    assert (ART / "runner_dry/sensorscope/central_all/runtime_manifest.json").is_file()
    assert (ART / "runner_dry/sensorscope/central_all/final_metrics.json").is_file()


def test_reuse_blocked():
    with pytest.raises(DuplicateReusedTrafficRunBlocked):
        assert_schedulable_e3_run(dataset="traffic", scenario="complete_aligned", seed=30001, method="raven")


def test_eps_and_canary_disjoint():
    assert EPS_ZERO == 1e-12
    assert CANARY_SEED not in FORMAL_SEEDS
    canary = json.loads((ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R2.json").read_text(encoding="utf-8"))
    assert canary["execute_in_this_round"] is False


def test_no_performance_pt_in_artifacts():
    stop = json.loads((ART / "E3_SEMANTIC_ALIGNMENT_STOP_STATUS.json").read_text(encoding="utf-8"))
    assert stop["no_training"] is True
    assert stop["canary_executed"] is False
    assert not any(ART.rglob("*.pt"))


def test_flamf_and_aliases():
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    assert flamf["status"] == "EXCLUDED_WITH_REASON"
    matrix = pd.read_csv(ART / "E3_METHOD_MATRIX_R2.csv")
    assert "timealign_agg" not in set(matrix.method)
