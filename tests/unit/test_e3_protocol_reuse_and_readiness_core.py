"""Unit tests for E3 protocol reuse/readiness (no training)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from raven_mcs.e3.protocol_readiness import CANARY_SEED, E2_FORMAL_SEEDS, E2_TRAFFIC_METHODS, EPS_ZERO

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts/e3_protocol_reuse_and_readiness_r1"


def test_reused_block_exactly_100_unique():
    payload = json.loads((ART / "E3_REUSED_E2_TRAFFIC_BLOCK_MANIFEST.json").read_text(encoding="utf-8"))
    assert payload["reusable_run_count"] == 100
    keys = [(r["seed"], r["method"]) for r in payload["records"]]
    assert len(keys) == len(set(keys)) == 100
    expected = {(s, m) for s in E2_FORMAL_SEEDS for m in E2_TRAFFIC_METHODS}
    assert set(keys) == expected
    assert set(payload["methods"]) == set(E2_TRAFFIC_METHODS)
    assert all(r["scenario"] == "complete_aligned" for r in payload["records"])


def test_reused_result_hash_identity_present():
    payload = json.loads((ART / "E3_REUSED_E2_TRAFFIC_BLOCK_MANIFEST.json").read_text(encoding="utf-8"))
    for r in payload["records"]:
        assert r["result_hash"] and len(r["result_hash"]) == 64
        assert r["checkpoint_hash"] and len(r["checkpoint_hash"]) == 64
        assert r["registry_hash"]
        assert Path(r["result_path"]).is_file()
        assert Path(r["checkpoint_path"]).is_file()


def test_no_duplicate_scheduling_of_reused_traffic_block():
    matrix = json.loads((ART / "E3_MINIMUM_NEW_RUN_MATRIX.json").read_text(encoding="utf-8"))
    rows = matrix["rows"]
    reused = [
        r
        for r in rows
        if r["dataset"] == "traffic"
        and r["method"] in E2_TRAFFIC_METHODS
        and r["already_available_and_reusable"]
    ]
    assert len(reused) == 5
    assert all(int(r["number_of_new_runs"]) == 0 for r in reused)
    assert int(matrix["reusable_existing_runs"]) == 100
    assert int(matrix["new_runs_actually_needed_for_ready_scope"]) == 80


def test_method_registry_uniqueness():
    methods = pd.read_csv(ART / "E3_METHOD_REGISTRY_AUDIT.csv")
    assert methods["method"].is_unique


def test_flamf_name_integrity():
    methods = pd.read_csv(ART / "E3_METHOD_REGISTRY_AUDIT.csv")
    flamf = methods.loc[methods.method == "flamf_original"].iloc[0]
    assert flamf["E3_table_role"] == "EXCLUDED_WITH_REASON"
    assert "flamf_timealign_adapted" in set(methods.method)


def test_metric_formula_registry():
    metrics = pd.read_csv(ART / "E3_METRIC_AVAILABILITY.csv")
    assert "RMSE_mu" in set(metrics.metric)
    assert "Delta_pair" in set(metrics.metric)
    assert metrics["metric"].is_unique


def test_delta_pair_sufficient_statistic_schema():
    pair = json.loads((ART / "E3_PAIR_METRIC_READINESS.json").read_text(encoding="utf-8"))
    assert pair["status"] == "PAIR_METRIC_NOT_READY_BLOCK_E3_PAIR_CLAIMS"
    assert "Pi_hat" in " ".join(pair["sufficient_statistics_required"])
    assert "pair_metrics.json" in pair["output_schema_draft"]


def test_eps_zero_frozen():
    stats = json.loads((ART / "E3_STATISTICAL_PROTOCOL.json").read_text(encoding="utf-8"))
    assert stats["EPS_ZERO"] == EPS_ZERO == 1e-12
    assert "win/tie/loss" in stats["eps_applied_before"]


def test_canary_seed_disjoint():
    canary = json.loads((ART / "E3_CANARY_PLAN.json").read_text(encoding="utf-8"))
    assert canary["canary_seed"] == CANARY_SEED
    assert CANARY_SEED not in E2_FORMAL_SEEDS
    assert canary["execute_in_this_round"] is False


def test_no_formal_seed_execution_in_protocol_round():
    stop = json.loads((ART / "E3_PROTOCOL_REUSE_AND_READINESS_STOP_STATUS.json").read_text(encoding="utf-8"))
    assert stop["no_training"] is True
    assert not any(ART.rglob("*.pt"))


def test_no_e4_e9_execution_artifacts():
    for name in ("e4_", "e5_", "e6_", "e7_", "e8_", "e9_"):
        assert not any(ART.rglob(f"*{name}*"))
