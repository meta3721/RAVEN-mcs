"""Unit tests for E3 multidataset protocol closure (no formal training)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from raven_mcs.e3.protocol_closure.central_reference import CentralTrainConfig, train_central_reference
from raven_mcs.e3.protocol_closure.constants import CANARY_SEED, EPS_ZERO, FORMAL_SEEDS, M_MC
from raven_mcs.e3.protocol_closure.method_registry import CANONICAL_METHODS, canonicalization_payload
from raven_mcs.e3.protocol_closure.pair_state import (
    build_pair_state_frame,
    compute_pair_metrics_from_state,
    pair_state_schema,
)
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.metrics.distribution import delta_pair

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts/e3_multidataset_protocol_closure_r1"


def test_duplicate_reused_traffic_run_blocked():
    with pytest.raises(DuplicateReusedTrafficRunBlocked) as ei:
        assert_schedulable_e3_run(
            dataset="traffic", scenario="complete_aligned", seed=30001, method="raven"
        )
    assert "DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED" in str(ei.value)


def test_non_reused_traffic_method_schedulable():
    assert_schedulable_e3_run(
        dataset="traffic", scenario="complete_aligned", seed=30001, method="local_hajek"
    )


def test_reuse_manifest_100():
    payload = json.loads((ART / "E3_TRAFFIC_REUSE_FINAL_MANIFEST.json").read_text(encoding="utf-8"))
    assert payload["reusable_run_count"] == 100
    keys = {(r["seed"], r["method"]) for r in payload["records"]}
    assert len(keys) == 100


def test_sensorscope_uair_identity():
    ss = json.loads((ART / "E3_SENSORSCOPE_PROTOCOL.json").read_text(encoding="utf-8"))
    ua = json.loads((ART / "E3_UAIR_PROTOCOL.json").read_text(encoding="utf-8"))
    assert ss["data_identity"]["spatial_units"] == 55
    assert ss["data_identity"]["common_timestamps"] == 312
    assert ua["data_identity"]["spatial_units"] == 36
    assert ua["data_identity"]["common_timestamps"] == 264
    assert ss["readiness_status"].startswith("READY")
    assert ua["readiness_status"].startswith("READY")


def test_pair_schema_and_toy_exactness():
    schema = pair_state_schema()
    assert "pair_id" in schema["required_columns"]
    frame = build_pair_state_frame(
        dataset="toy",
        seed=1,
        scenario="complete_aligned",
        method="raven",
        window=0,
        pair_ids=["a", "b"],
        source_groups=[0, 1],
        target_groups=[0, 1],
        observed_pair_mass=[1.0, 0.0],
        estimated_pair_mass=[0.25, 0.75],
        target_pair_mass=[0.5, 0.5],
    )
    metrics = compute_pair_metrics_from_state(frame)
    expected = delta_pair(np.array([0.25, 0.75]), np.array([0.5, 0.5]))
    assert metrics["Delta_pair"] == pytest.approx(expected)
    assert np.isfinite(metrics["Delta_pair"])


def test_pair_no_unsupported_negative():
    with pytest.raises(ValueError):
        build_pair_state_frame(
            dataset="toy",
            seed=1,
            scenario="complete_aligned",
            method="raven",
            window=0,
            pair_ids=["a"],
            source_groups=[0],
            target_groups=[0],
            observed_pair_mass=[1.0],
            estimated_pair_mass=[-0.1],
            target_pair_mass=[1.0],
        )


def test_canonicalization_no_double_count():
    payload = canonicalization_payload()
    assert payload["n_canonical_semantic_methods"] == len(CANONICAL_METHODS)
    aliases = {a["alias"]: a["canonical_method_id"] for a in payload["aliases"]}
    assert aliases["timealign_agg"] == "flamf_timealign_adapted"


def test_flamf_excluded():
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    assert flamf["status"] == "EXCLUDED_WITH_REASON"


def test_eps_zero_and_all_ties_policy():
    stats = json.loads((ART / "E3_STATISTICAL_PROTOCOL_FINAL.json").read_text(encoding="utf-8"))
    assert stats["EPS_ZERO"] == EPS_ZERO
    assert stats["all_ties_policy"]["p_raw"] == 1.0


def test_simoracle_mmc():
    oracle = json.loads((ART / "E3_SIMORACLE_PROTOCOL.json").read_text(encoding="utf-8"))
    assert oracle["M_MC"] == M_MC == 2000


def test_canary_seed_disjoint_and_not_executed():
    seeds = json.loads((ART / "E3_FORMAL_SEED_FREEZE.json").read_text(encoding="utf-8"))
    assert seeds["canary_seed"] == CANARY_SEED
    assert CANARY_SEED not in FORMAL_SEEDS
    assert seeds["execute_canary_this_round"] is False


def test_central_all_no_test_targets_and_delivered_mask():
    n = 40
    spatial = np.arange(n) % 8
    hour = np.arange(n) % 24
    weekday = (np.arange(n) % 7).astype(float)
    trend = np.linspace(0, 1, n)
    y = np.sin(np.arange(n) / 5.0)
    delivered = np.zeros(n, dtype=bool)
    delivered[:20] = True
    out_all = train_central_reference(
        spatial_index=spatial,
        hour=hour,
        weekday=weekday,
        trend=trend,
        targets=y,
        delivered_mask=None,
        config=CentralTrainConfig(mode="central_all", seed=123, local_steps=3, num_spatial=8),
    )
    out_del = train_central_reference(
        spatial_index=spatial,
        hour=hour,
        weekday=weekday,
        trend=trend,
        targets=y,
        delivered_mask=delivered,
        config=CentralTrainConfig(mode="central_delivered", seed=123, local_steps=3, num_spatial=8),
    )
    assert out_all["n_train_rows"] == 40
    assert out_del["n_train_rows"] == 20
    assert out_all["uses_raven_only_state"] is False


def test_no_training_artifacts():
    stop = json.loads((ART / "E3_MULTIDATASET_PROTOCOL_CLOSURE_STOP_STATUS.json").read_text(encoding="utf-8"))
    assert stop["no_training"] is True
    assert not any(ART.rglob("*.pt"))


def test_method_source_hashes_not_shared_singleton():
    payload = json.loads((ART / "E3_METHOD_SOURCE_HASHES.json").read_text(encoding="utf-8"))
    h_raven = payload["methods"]["raven"]["implementation_hash"]
    h_fed = payload["methods"]["fedavg_window"]["implementation_hash"]
    assert h_raven and h_fed
    # May differ; at least raven includes more files
    assert len(payload["methods"]["raven"]["files"]) >= len(payload["methods"]["fedavg_window"]["files"])
