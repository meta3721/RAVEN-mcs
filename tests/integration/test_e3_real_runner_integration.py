"""Integration tests for E3 real-runner correctness path."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from raven_mcs.e3.real_runner.central_real import _train_ids_all, _train_ids_delivered
from raven_mcs.e3.real_runner.constants import DEBUG_SEED, FEDERATED_METHODS, M_MC
from raven_mcs.e3.real_runner.fixture import build_correctness_fixture, load_fixture_dataset
from raven_mcs.e3.real_runner.generator_r3 import materialize_r3_trace
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.simulation.event_trace import load_event_trace

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def smoke_ctx(tmp_path_factory):
    root = tmp_path_factory.mktemp("e3r_int")
    fx = build_correctness_fixture(root / "fixture")
    ds = load_fixture_dataset(Path(fx["data_dir"]))
    mat = materialize_r3_trace(
        dataset="fixture",
        atomic=ds.atomic_df,
        spatial_to_client=fx["spatial_to_client"],
        out_dir=root / "trace",
        seed=DEBUG_SEED,
        num_windows=2,
        m_mc=100,  # faster than formal 2000 for CI integration
    )
    et = root / "trace" / "training_eventtrace"
    return {
        "root": root,
        "dataset": ds,
        "mapping": fx["spatial_to_client"],
        "et": et,
        "mat": mat,
    }


def test_federated_real_path_non_placeholder(smoke_ctx):
    method = "fedavg_window"
    out = run_e3_real(
        root=ROOT,
        run_dir=smoke_ctx["root"] / f"run_{method}",
        dataset=smoke_ctx["dataset"],
        method=method,
        seed=DEBUG_SEED,
        eventtrace_dir=smoke_ctx["et"],
        spatial_to_client=smoke_ctx["mapping"],
        local_steps=1,
        dataset_name="fixture",
    )
    assert out["status"] == "REAL_PATH_EXECUTED"
    assert out["smoke_audit"]["local_optimizer_steps"] > 0
    assert out["smoke_audit"]["checkpoint_written"]
    assert (smoke_ctx["root"] / f"run_{method}" / "checkpoints" / "final.pt").is_file()
    assert out["metrics"]["RMSE_mu"] is not None
    assert out["smoke_audit"]["placeholder_fields"] == []
    assert (smoke_ctx["root"] / f"run_{method}" / "pair_state.parquet").is_file()


def test_raven_simoracle_uses_mc_q_in_trace(smoke_ctx):
    trace, _ = load_event_trace(smoke_ctx["et"])
    assert int(trace.events["oracle_q"].notna().sum()) == len(trace.events)
    # Formal generator path uses M_MC in opportunity features
    feats = trace.events["opportunity_features"].iloc[0]
    if isinstance(feats, str):
        feats = json.loads(feats)
    assert int(feats.get("M_MC", 0)) in {100, M_MC} or "q_use_true" in feats


def test_central_delivered_matches_eventtrace_ids(smoke_ctx):
    trace, _ = load_event_trace(smoke_ctx["et"])
    events = trace.events.copy()
    for col in ("observed_unit_ids", "opportunity_features", "risk_set_unit_ids", "O"):
        if events[col].dtype == object:
            events[col] = events[col].map(lambda v: json.loads(v) if isinstance(v, str) else v)
    expected = _train_ids_delivered(events, smoke_ctx["dataset"])
    out = run_e3_real(
        root=ROOT,
        run_dir=smoke_ctx["root"] / "run_central_delivered",
        dataset=smoke_ctx["dataset"],
        method="central_delivered",
        seed=DEBUG_SEED,
        eventtrace_dir=smoke_ctx["et"],
        spatial_to_client=smoke_ctx["mapping"],
        local_steps=5,
        dataset_name="fixture",
    )
    summary = json.loads(
        (smoke_ctx["root"] / "run_central_delivered" / "central_train_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["bernoulli_resample"] is False
    assert summary["train_unit_ids"] == expected
    assert set(summary["train_unit_ids"]).issubset(set(_train_ids_all(smoke_ctx["dataset"])))
    assert out["status"] == "REAL_PATH_EXECUTED"


def test_all_federated_methods_enter_real_path(smoke_ctx):
    # Spot-check a second method besides fedavg
    for method in ("local_hajek", "raven"):
        assert method in FEDERATED_METHODS
        out = run_e3_real(
            root=ROOT,
            run_dir=smoke_ctx["root"] / f"run_{method}",
            dataset=smoke_ctx["dataset"],
            method=method,
            seed=DEBUG_SEED,
            eventtrace_dir=smoke_ctx["et"],
            spatial_to_client=smoke_ctx["mapping"],
            local_steps=1,
            dataset_name="fixture",
        )
        assert out["status"] == "REAL_PATH_EXECUTED"
        assert out["metrics"]["RMSE_mu"] is not None
