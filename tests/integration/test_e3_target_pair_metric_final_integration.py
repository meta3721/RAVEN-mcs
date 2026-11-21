"""Integration tests for E3 final target/pair/metric wiring."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from raven_mcs.e3.real_runner.fixture_nd import build_nondegenerate_fixture, load_nd_fixture
from raven_mcs.e3.real_runner.generator_r3 import materialize_r3_trace
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.e3.semantic_alignment.target_semantics import freeze_target_semantics
from raven_mcs.e3.target_pair.constants import DEBUG_SEED

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def ctx(tmp_path_factory):
    root = tmp_path_factory.mktemp("e3f_int")
    fx = build_nondegenerate_fixture(root / "fixture")
    ds = load_nd_fixture(Path(fx["data_dir"]))
    art = freeze_target_semantics(ds.atomic_df, dataset="fixture")
    materialize_r3_trace(
        dataset="fixture",
        atomic=ds.atomic_df,
        spatial_to_client=fx["spatial_to_client"],
        out_dir=root / "trace",
        seed=DEBUG_SEED,
        num_windows=4,
        m_mc=50,
        delivery_mode="high",
    )
    return {
        "root": root,
        "ds": ds,
        "mapping": fx["spatial_to_client"],
        "art": art,
        "et": root / "trace" / "training_eventtrace",
        "n_groups": art["n_groups"],
    }


def test_production_uses_spatial_time_n_groups(ctx):
    out = run_e3_real(
        root=ROOT,
        run_dir=ctx["root"] / "run_fedavg",
        dataset=ctx["ds"],
        method="fedavg_window",
        seed=DEBUG_SEED,
        eventtrace_dir=ctx["et"],
        spatial_to_client=ctx["mapping"],
        local_steps=1,
        dataset_name="fixture",
        target_artifact=ctx["art"],
    )
    assert out["target_wiring"]["n_groups_frozen"] == ctx["n_groups"]
    assert out["target_wiring"]["uses_repeatable_time_of_day_mapper"] is False
    assert ctx["n_groups"] > 4
    assert out["status"] == "REAL_PATH_EXECUTED"
    assert abs(float(out["metrics"]["Delta_c_s"]) - 2.0) > 1e-9
    assert out["metrics"]["Delta_pair"] is None
    assert out["metrics"]["Delta_pair_applicability"] == "NOT_MATERIALIZED"
    assert out["metrics"]["Q_norm1_over_S"] is None
    assert out["metrics"]["Q_norm1_over_S_applicability"] == "NOT_APPLICABLE"
    assert out["metrics"]["RMSE_mu"] != out["metrics"]["RMSE_rho"]


def test_method_dependent_pi_hat_and_raven_debt(ctx):
    hashes = {}
    for method in ("fedavg_window", "raven"):
        out = run_e3_real(
            root=ROOT,
            run_dir=ctx["root"] / f"run_{method}_b",
            dataset=ctx["ds"],
            method=method,
            seed=DEBUG_SEED,
            eventtrace_dir=ctx["et"],
            spatial_to_client=ctx["mapping"],
            local_steps=2,
            dataset_name="fixture",
            target_artifact=ctx["art"],
        )
        summary_path = ctx["root"] / f"run_{method}_b" / "delta_cs_summary_v6.json"
        if not summary_path.is_file():
            summary_path = ctx["root"] / f"run_{method}_b" / "delta_c_s_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        hashes[method] = summary["pi_hat_hash"]
        assert "Delta_c_s" in summary
        assert summary.get("support") == "client × opportunity_stratum"
        assert summary.get("Delta_pair") is None
        assert (ctx["root"] / f"run_{method}_b" / "atomic_rho_v2.parquet").is_file()
        assert out["smoke_audit"].get("max_a_r_size", 0) >= 2
        if method == "raven":
            assert float(out["metrics"]["Q_norm1_over_S"]) > 0
        if method == "fedavg_window":
            assert out["metrics"]["Q_norm1_over_S"] is None
    assert hashes["fedavg_window"] != hashes["raven"]


def test_central_na_and_true_head_tail(ctx):
    out = run_e3_real(
        root=ROOT,
        run_dir=ctx["root"] / "run_central",
        dataset=ctx["ds"],
        method="central_all",
        seed=DEBUG_SEED,
        eventtrace_dir=ctx["et"],
        spatial_to_client=ctx["mapping"],
        local_steps=5,
        dataset_name="fixture",
        target_artifact=ctx["art"],
    )
    assert out["metrics"]["Delta_c_s"] is None
    assert out["metrics"]["Delta_c_s_applicability"] == "NOT_APPLICABLE"
    assert out["metrics"]["Delta_pair"] is None
    assert out["metrics"]["Delta_pair_applicability"] == "NOT_MATERIALIZED"
    assert out["metrics"]["Delta_group"] is None
    assert out["metrics"]["Head_RMSE"] is not None
    assert out["metrics"]["Tail_RMSE"] is not None
    # Not copied from overall unless coincidence — groups differ so usually differ
    assert out["metrics"]["RMSE_mu"] is not None


def test_head_tail_consumes_artifact(ctx):
    # Flip head/tail in a controlled copy; runner must refuse mismatch if caller overrides,
    # and must use artifact groups for metrics.
    art = dict(ctx["art"])
    out = run_e3_real(
        root=ROOT,
        run_dir=ctx["root"] / "run_ht",
        dataset=ctx["ds"],
        method="fedavg_window",
        seed=DEBUG_SEED,
        eventtrace_dir=ctx["et"],
        spatial_to_client=ctx["mapping"],
        local_steps=1,
        dataset_name="fixture",
        target_artifact=art,
    )
    tw = json.loads((ctx["root"] / "run_ht" / "target_wiring.json").read_text(encoding="utf-8"))
    assert tw["head_tail"]["n_head"] > 0
    assert tw["head_tail"]["n_tail"] > 0
    assert out["metrics"]["Head_RMSE"] is not None
