"""Canonical E3 real runner — h target, Delta_c_s on s, atomic rho_i^arr."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

from raven_mcs.correction.pi_target import (
    build_pi_target,
    build_pi_target_support_compatible,
)
from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.e3.delta_cs_rho.atomic_rho import build_atomic_arrival_rho
from raven_mcs.e3.delta_cs_rho.constants import METRIC_SCHEMA_VERSION, PAIR_SCHEMA_VERSION
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import accumulate_delta_cs_v6
from raven_mcs.e3.protocol_closure.reuse_guard import assert_schedulable_e3_run
from raven_mcs.e3.real_runner.central_real import run_central_real
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.e3.stratum_seal.traffic_regions import load_frozen_traffic_station_regions
from raven_mcs.e3.target_pair.errors import HeadTailWiringError, TargetWiringError
from raven_mcs.e3.target_pair.metric_applicability import (
    applicability_for,
    finalize_metrics_dict,
    metric_schema_v6,
)
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
from raven_mcs.metrics.accuracy import mae_mu, rmse_mu, rmse_rho
from raven_mcs.metrics.distribution import avg_delta_ref, delta_group
from raven_mcs.simulation.event_trace import load_event_trace
from raven_mcs.training.window_runner import build_full_runner
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

SCENARIO = "complete_aligned"

REQUIRED_METRICS = [
    "RMSE_mu",
    "MAE_mu",
    "Head_RMSE",
    "Tail_RMSE",
    "RMSE_rho",
    "Delta_group",
    "Delta_c_s",
    "Delta_pair",
    "delta_ref",
    "Q_norm1_over_S",
    "Q_norm2_over_S",
    "ESS",
    "clip_rate_stage1",
    "clip_rate_stage2",
    "solver_status",
    "runtime_seconds",
]


def metric_schema_v3() -> dict[str, Any]:
    """ Backward-compatible alias; production uses V6. """
    return metric_schema_v6()


def _atomic_rho_for_pred(
    *,
    pred: dict[str, Any],
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
    pi_opp_joint: dict[tuple[str, str], float],
    events: pd.DataFrame,
    run_dir: Path,
) -> np.ndarray:
    """Scientific RMSE_rho weights — atomic rho_i^arr only."""
    out = build_atomic_arrival_rho(
        test_unit_ids=[str(u) for u in pred["unit_ids"]],
        atomic=atomic,
        spatial_to_client=spatial_to_client,
        pi_opp_joint=pi_opp_joint,
        events=events,
    )
    out["frame"].to_parquet(run_dir / "atomic_rho_v2.parquet", index=False)
    dump_json(
        {
            "sum_rho": out["sum_rho"],
            "n_units": out["n_units"],
            "builder": out["builder"],
            "group_marginal_used": False,
            "status": out["status"],
        },
        run_dir / "atomic_rho_summary.json",
    )
    return np.asarray(out["rho"], dtype=np.float64)


def _append_ledger(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def _predict(runner, dataset: ProcessedDataset, split: str = "test") -> dict[str, Any]:
    """Predict with the SAME feature extraction used by ClientTrainer.

    UNIT_SCALE_FIX / PREPROCESSING_CONSISTENCY_FIX:
    Federated training normalizes trend via ``extract_features``
    (time_index / total_time_slots). The previous eval path fed raw
    ``time_index`` and weekday=0, causing U-Air/Traffic prediction explosion.
    """
    from raven_mcs.models.features import extract_features

    units = dataset.get_atomic_units(split=split)
    if not units:
        return {
            "y_true": np.zeros(0),
            "y_pred": np.zeros(0),
            "groups": np.zeros(0, dtype=int),
            "group_strs": [],
            "unit_ids": [],
        }
    model = runner.model
    model.eval()
    y_true, y_pred, groups, group_strs, uids = [], [], [], [], []
    inv = {i: g for g, i in dataset._target_group_str_to_int.items()}
    spatial_to_idx = {
        str(sid): int(i) for sid, i in dataset._spatial_to_idx.items()
    }
    total_slots = int(dataset.atomic_df["time_index"].max()) + 1
    with torch.no_grad():
        for u in units:
            sp_idx, hour_t, wday_t, trend_t = extract_features(
                [u.spatial_id],
                [float(u.absolute_time)],
                [int(u.time_index)],
                spatial_to_idx,
                total_slots,
            )
            pred = model(sp_idx, hour_t, wday_t, trend_t).cpu().numpy().reshape(-1)
            y_pred.append(float(pred[0]))
            y_true.append(float(u.target_value))
            groups.append(int(u.target_group))
            group_strs.append(inv.get(int(u.target_group), str(u.target_group)))
            uids.append(u.unit_id)
    return {
        "y_true": np.asarray(y_true, dtype=np.float64),
        "y_pred": np.asarray(y_pred, dtype=np.float64),
        "groups": np.asarray(groups, dtype=int),
        "group_strs": group_strs,
        "unit_ids": uids,
    }


def _mu_weights_for_test(pred: dict[str, Any], target_mu: np.ndarray) -> np.ndarray:
    """Per-test-unit mu weight = mu_g / count(units in g) so sum_i w_i = 1."""
    gids = pred["groups"]
    if len(gids) == 0:
        return np.zeros(0, dtype=np.float64)
    counts: dict[int, int] = {}
    for g in gids.tolist():
        counts[int(g)] = counts.get(int(g), 0) + 1
    w = np.zeros(len(gids), dtype=np.float64)
    for i, g in enumerate(gids.tolist()):
        g = int(g)
        mg = float(target_mu[g]) if g < len(target_mu) else 0.0
        w[i] = mg / max(counts[g], 1)
    s = float(w.sum())
    if s <= 0:
        w[:] = 1.0 / len(w)
    else:
        w = w / s
    return w


def _head_tail_rmse(
    pred: dict[str, Any],
    mu_w: np.ndarray,
    head_ids: list[int],
    tail_ids: list[int],
) -> tuple[float, float]:
    if len(mu_w) == 0:
        raise HeadTailWiringError("HEAD_TAIL_WIRING_ERROR: empty predictions")
    gids = pred["groups"]
    head_mask = np.isin(gids, np.asarray(head_ids, dtype=int))
    tail_mask = np.isin(gids, np.asarray(tail_ids, dtype=int))
    if not head_mask.any() or not tail_mask.any():
        raise HeadTailWiringError("HEAD_TAIL_WIRING_ERROR: empty Head or Tail mask on test")

    def _wrmse(mask: np.ndarray) -> float:
        ww = mu_w[mask].copy()
        ww = ww / float(ww.sum())
        return float(np.sqrt(np.sum(ww * (pred["y_true"][mask] - pred["y_pred"][mask]) ** 2)))

    return _wrmse(head_mask), _wrmse(tail_mask)


def run_e3_real(
    *,
    root: Path,
    run_dir: Path,
    dataset: ProcessedDataset,
    method: str,
    seed: int,
    eventtrace_dir: Path,
    spatial_to_client: dict[str, str],
    scenario: str = SCENARIO,
    local_steps: int = 2,
    head_groups: list[int] | None = None,
    tail_groups: list[int] | None = None,
    ledger_path: Path | None = None,
    dataset_name: str = "fixture",
    target_artifact: dict[str, Any] | None = None,
    attempt_id: str | None = None,
    source_identity: dict[str, Any] | None = None,
    pi_target_mode: str = "test",
    pi_target_override: dict[tuple[str, str], float] | None = None,
) -> dict[str, Any]:
    """Production E3 runner used by future Canary (true training path)."""
    assert_schedulable_e3_run(
        dataset=dataset_name, scenario=scenario, seed=int(seed), method=method
    )
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"e3::{dataset_name}::{scenario}::{method}::seed{seed}"
    attempt_id = attempt_id or f"{run_id}__attempt1"
    t0 = time.perf_counter()
    ledger_path = Path(ledger_path or (run_dir / "ledger.jsonl"))
    source_identity = dict(source_identity or {})

    # --- TASK 1: frozen spatial×time target (no time-only fallback) ---
    bundle = production_target_bundle(
        root=Path(root),
        dataset_name=dataset_name,
        dataset=dataset,
        fixture_artifact=target_artifact,
    )
    if bundle["uses_repeatable_time_of_day_mapper"]:
        raise TargetWiringError("TARGET_WIRING_ERROR: RepeatableTimeOfDayMapper fallback active")
    target_mu = np.asarray(bundle["mu"], dtype=np.float64)
    n_groups = int(bundle["n_groups_runtime"])
    ht = bundle["head_tail"]
    # Prefer frozen artifact partition; ignore caller half-split defaults
    head_ids = list(ht["head_group_ids"])
    tail_ids = list(ht["tail_group_ids"])
    if head_groups is not None and set(head_groups) != set(head_ids):
        # Explicit override only allowed if it matches frozen ids (test harness may pass frozen ids)
        if sorted(head_groups) != sorted(head_ids):
            raise HeadTailWiringError(
                "HEAD_TAIL_WIRING_ERROR: caller Head/Tail does not match frozen artifact"
            )

    config = {
        "dataset": dataset_name,
        "seed": int(seed),
        "method": method,
        "scenario": scenario,
        "local_steps": int(local_steps),
        "pair_state_schema_version": PAIR_SCHEMA_VERSION,
        "metric_schema_version": METRIC_SCHEMA_VERSION,
        "n_groups_runtime": n_groups,
        "n_groups_frozen": bundle["n_groups_frozen"],
        "uses_spatial_time_target": True,
        "target_artifact_path": bundle["artifact_path"],
        "target_artifact_sha256": bundle["artifact_sha256"],
        "path": "REAL",
        "pi_target_mode": (
            "override" if pi_target_override is not None else str(pi_target_mode)
        ),
    }
    dump_json(config, run_dir / "config_snapshot.json")
    dump_json(
        {
            "n_groups_runtime": n_groups,
            "n_groups_frozen": bundle["n_groups_frozen"],
            "artifact_path": bundle["artifact_path"],
            "artifact_sha256": bundle["artifact_sha256"],
            "uses_repeatable_time_of_day_mapper": False,
            "head_tail": ht,
        },
        run_dir / "target_wiring.json",
    )
    config_hash = sha256_file(run_dir / "config_snapshot.json")

    trace, identity = load_event_trace(Path(eventtrace_dir))
    et_hash = identity.get("trace_hash")
    _append_ledger(
        ledger_path,
        {
            "event": "START",
            "run_id": run_id,
            "attempt_id": attempt_id,
            "dataset": dataset_name,
            "seed": int(seed),
            "scenario": scenario,
            "canonical_method": method,
            "config_hash": config_hash,
            "EventTrace_hash": et_hash,
            "git_commit": source_identity.get("git_commit"),
            "source_manifest_hash": source_identity.get("source_manifest_hash"),
            "method_source_hash": source_identity.get("method_source_hash"),
            "runner_source_hash": source_identity.get("runner_source_hash"),
            "dataset_hash": source_identity.get("dataset_hash"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    metrics: dict[str, Any] = {k: None for k in REQUIRED_METRICS}
    pair_summary: dict[str, Any] = {}
    smoke_audit: dict[str, Any] = {
        "method": method,
        "local_optimizer_steps": 0,
        "n_local_updates": 0,
        "n_delivered_updates": 0,
        "aggregation_invoked": False,
        "P2_invoked": False,
        "checkpoint_written": False,
        "metric_computation_invoked": False,
        "placeholder_fields": [],
        "n_groups_runtime": n_groups,
        "status": "BLOCKED",
    }

    # Sealed opportunity-stratum identity (Traffic → 4 real regions; SS/UA station-level)
    atomic_sealed, stratum_meta = apply_sealed_opportunity_stratum(
        dataset.atomic_df,
        dataset=dataset_name,
        root=Path(root),
    )
    dump_json(stratum_meta, run_dir / "opportunity_stratum_identity.json")
    if dataset_name == "traffic" and int(stratum_meta.get("n_unique_strata", 0)) > 32:
        raise RuntimeError("TRAFFIC_STRATUM_IDENTITY_ERROR: strata cardinality > 32")

    # Keep ProcessedDataset opportunity_stratum identical to the sealed identity used
    # by pi_tar / Delta_c_s / EventTrace (Traffic region remap); otherwise window
    # extracts read raw station-level s(i) and zeta fails for Traffic.
    sealed_by_unit = {
        str(r.unit_id): str(r.opportunity_stratum)
        for r in atomic_sealed.itertuples(index=False)
    }
    dataset._atomic_df = dataset._atomic_df.copy()
    dataset._atomic_df["opportunity_stratum"] = [
        sealed_by_unit.get(str(uid), str(s))
        for uid, s in zip(
            dataset._atomic_df["unit_id"].tolist(),
            dataset._atomic_df["opportunity_stratum"].tolist(),
        )
    ]
    # pi_target on sealed opportunity strata (joint scale compatible)
    atomic_for_pi = atomic_sealed.copy()
    if "target_group_main" not in atomic_for_pi.columns:
        # Keep string spatial×time group for pi_target builder via column alias
        atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"].astype(str)
    # Joint pi_opp on the same client×stratum support (production design-ratio denominator)
    train = atomic_sealed.loc[atomic_sealed["split"].astype(str) == "train"]
    strata_by_client: dict[str, list[str]] = {}
    for r in train.itertuples(index=False):
        c = spatial_to_client.get(str(r.spatial_id))
        if c is None:
            continue
        strata_by_client.setdefault(c, []).append(str(r.opportunity_stratum))
    for c in strata_by_client:
        strata_by_client[c] = sorted(set(strata_by_client[c]))
    pi_opp_joint = build_joint_pi_opp(sorted(strata_by_client), strata_by_client)
    if pi_target_override is not None:
        pi_target = {
            (str(k[0]), str(k[1])): float(v) for k, v in pi_target_override.items()
        }
    else:
        mode = str(pi_target_mode).strip().lower()
        if mode == "support_compatible":
            pi_frame = build_pi_target_support_compatible(
                atomic_for_pi,
                spatial_to_client,
                split="test",
                pi_opp_joint=pi_opp_joint,
            )
        elif mode == "test":
            pi_frame = build_pi_target(atomic_for_pi, spatial_to_client, split="test")
        else:
            raise ValueError(f"unknown pi_target_mode: {pi_target_mode}")
        pi_target = {
            (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
            for r in pi_frame.itertuples()
        }

    events = trace.events.copy()
    for col in ("risk_set_unit_ids", "opportunity_features", "observed_unit_ids", "O"):
        if events[col].dtype == object:
            events[col] = events[col].map(lambda v: json.loads(v) if isinstance(v, str) else v)
    if dataset_name == "traffic":
        station_to_region, _ = load_frozen_traffic_station_regions(Path(root))

        def _remap_feat_stratum(feats: dict) -> dict:
            feats = dict(feats or {})
            old = str(feats.get("opportunity_stratum") or "")
            parts = old.split("::")
            if len(parts) >= 3 and parts[0] in station_to_region:
                feats["opportunity_stratum"] = (
                    f"{station_to_region[parts[0]]}::{parts[1]}::{parts[2]}"
                )
            return feats

        events["opportunity_features"] = events["opportunity_features"].map(_remap_feat_stratum)

    unit_to_group = {
        str(r.unit_id): str(r.target_group) for r in atomic_sealed.itertuples(index=False)
    }

    if method in {"central_all", "central_delivered"}:
        central = run_central_real(
            run_dir=run_dir,
            method=method,
            dataset=dataset,
            events=events,
            seed=int(seed),
            local_steps=max(local_steps * 10, 20),
        )
        smoke_audit.update(
            {
                "local_optimizer_steps": int(central["steps"]),
                "n_local_updates": int(central["n_train_units"]),
                "n_delivered_updates": int(central["n_train_units"]),
                "aggregation_invoked": False,
                "checkpoint_written": (run_dir / "checkpoints" / "final.pt").is_file(),
                "metric_computation_invoked": True,
                "status": "REAL_PATH_EXECUTED",
            }
        )
        model = CommonNDMF_from_ckpt(run_dir / "checkpoints" / "final.pt", dataset.num_spatial)
        pred = _predict_model(model, dataset)
        mu_w = _mu_weights_for_test(pred, target_mu)
        rho_w = _atomic_rho_for_pred(
            pred=pred,
            atomic=atomic_sealed,
            spatial_to_client=spatial_to_client,
            pi_opp_joint=pi_opp_joint,
            events=events,
            run_dir=run_dir,
        )
        metrics["RMSE_mu"] = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else None
        metrics["MAE_mu"] = float(mae_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else None
        metrics["RMSE_rho"] = float(rmse_rho(pred["y_pred"], pred["y_true"], rho_w)) if len(rho_w) else None
        head_rmse, tail_rmse = _head_tail_rmse(pred, mu_w, head_ids, tail_ids)
        metrics["Head_RMSE"] = head_rmse
        metrics["Tail_RMSE"] = tail_rmse
        # Structural N/A — must NOT be fake zeros
        metrics["Delta_group"] = None
        metrics["Delta_c_s"] = None
        metrics["Delta_pair"] = None
        metrics["delta_ref"] = None
        metrics["Q_norm1_over_S"] = None
        metrics["Q_norm2_over_S"] = None
        metrics["ESS"] = None
        metrics["clip_rate_stage1"] = None
        metrics["clip_rate_stage2"] = None
        metrics["solver_status"] = "CENTRAL_NO_P2"
        pair_summary = {
            "Delta_c_s": None,
            "Delta_pair": None,
            "Delta_pair_status": "NOT_MATERIALIZED",
            "support": "client × opportunity_stratum",
            "status": "NOT_APPLICABLE_CENTRAL",
        }
        dump_json(pair_summary, run_dir / "delta_cs_summary_v6.json")
        dump_json(pair_summary, run_dir / "delta_c_s_summary.json")
        pd.DataFrame([]).to_parquet(run_dir / "delta_cs_state_v6.parquet", index=False)
    else:
        runner = build_full_runner(
            trace,
            dataset,
            method=method,
            n_groups=n_groups,
            model_seed=int(seed),
            local_steps=int(local_steps),
            target_mu=target_mu,
            pi_target=pi_target,
            s_max=int(trace.metadata.s_max),
            device="cpu",
            use_coarse_time_groups=False,
            pi_opp_joint=pi_opp_joint,
        )
        window_metrics = runner.run()
        (run_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
        torch.save(runner.theta, run_dir / "checkpoints" / "final.pt")

        n_updates = sum(1 for wm in window_metrics if wm.active)
        n_delivered = sum(int(wm.a_r_size) for wm in window_metrics)
        max_ar = max((int(wm.a_r_size) for wm in window_metrics), default=0)
        p2_methods = {
            "inst_cal", "debt_cal", "raven", "raven_simoracle",
            "raven_wo_design", "raven_wo_obs", "raven_wo_use",
            "raven_wo_inst", "raven_wo_debt",
        }
        smoke_audit.update(
            {
                "local_optimizer_steps": int(local_steps) * max(n_delivered, 1),
                "n_local_updates": int(n_updates),
                "n_delivered_updates": int(n_delivered),
                "max_a_r_size": int(max_ar),
                "aggregation_invoked": any(len(wm.alpha) > 0 for wm in window_metrics),
                "P2_invoked": method in p2_methods and any(len(wm.alpha) > 0 for wm in window_metrics),
                "checkpoint_written": True,
                "metric_computation_invoked": True,
                "status": "REAL_PATH_EXECUTED",
            }
        )

        pred = _predict(runner, dataset, split="test")
        mu_w = _mu_weights_for_test(pred, target_mu)
        rho_w = _atomic_rho_for_pred(
            pred=pred,
            atomic=atomic_sealed,
            spatial_to_client=spatial_to_client,
            pi_opp_joint=pi_opp_joint,
            events=events,
            run_dir=run_dir,
        )
        metrics["RMSE_mu"] = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else None
        metrics["MAE_mu"] = float(mae_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else None
        metrics["RMSE_rho"] = float(rmse_rho(pred["y_pred"], pred["y_true"], rho_w)) if len(rho_w) else None
        head_rmse, tail_rmse = _head_tail_rmse(pred, mu_w, head_ids, tail_ids)
        metrics["Head_RMSE"] = head_rmse
        metrics["Tail_RMSE"] = tail_rmse

        try:
            omega = runner.omega_bar()
            metrics["Delta_group"] = float(delta_group(omega, target_mu))
        except Exception:  # noqa: BLE001
            metrics["Delta_group"] = float("nan")

        alphas = [np.asarray(wm.alpha, dtype=np.float64) for wm in window_metrics if wm.active and len(wm.alpha)]
        betas = [np.asarray(wm.beta_hat, dtype=np.float64) for wm in window_metrics if wm.active and len(wm.beta_hat)]
        if applicability_for(method, "delta_ref") == "APPLICABLE":
            if alphas and betas and len(alphas) == len(betas):
                metrics["delta_ref"] = float(
                    avg_delta_ref(alphas, betas, [True] * len(alphas), [1.0] * len(alphas))
                )
            else:
                metrics["delta_ref"] = 0.0
        else:
            metrics["delta_ref"] = None
        if applicability_for(method, "Q_norm1_over_S") == "APPLICABLE":
            debt_l1 = (
                float(np.linalg.norm(runner.debt, ord=1))
                if getattr(runner, "debt", None) is not None
                else 0.0
            )
            scale = float(max(getattr(runner, "scale", 0.0), 1e-12))
            metrics["Q_norm1_over_S"] = float(debt_l1 / scale)
            metrics["Q_norm2_over_S"] = (
                float(np.linalg.norm(runner.debt) / scale)
                if getattr(runner, "debt", None) is not None
                else 0.0
            )
        else:
            metrics["Q_norm1_over_S"] = None
            metrics["Q_norm2_over_S"] = None
        ess_vals = [float(x) for wm in window_metrics for x in (wm.n_eff_values or [])]
        metrics["ESS"] = float(np.mean(ess_vals)) if ess_vals else 0.0
        metrics["clip_rate_stage1"] = (
            float(np.mean([wm.clip_rate_stage1 for wm in window_metrics])) if window_metrics else 0.0
        )
        metrics["clip_rate_stage2"] = (
            float(np.mean([wm.clip_rate_stage2 for wm in window_metrics])) if window_metrics else 0.0
        )
        metrics["solver_status"] = "OK"

        pair_frame, pair_summary = accumulate_delta_cs_v6(
            window_metrics=window_metrics,
            diagnostics=list(runner.diagnostics),
            atomic=atomic_sealed,
            spatial_to_client=spatial_to_client,
            dataset=dataset_name,
            seed=int(seed),
            scenario=scenario,
            method=method,
            eventtrace_hash=et_hash,
            stratum_map_hash=None,
            target_mass_hash=bundle["artifact_sha256"],
            method_source_hash=None,
        )
        pair_frame.to_parquet(run_dir / "delta_cs_state_v6.parquet", index=False)
        dump_json(pair_summary, run_dir / "delta_cs_summary_v6.json")
        dump_json(pair_summary, run_dir / "delta_c_s_summary.json")
        metrics["Delta_c_s"] = float(pair_summary["Delta_c_s"])
        metrics["Delta_pair"] = None  # NOT_MATERIALIZED
        # Legacy aliases (content is V6 client×stratum; do not claim target_group)
        pair_frame.to_parquet(run_dir / "pair_state.parquet", index=False)
        dump_json(pair_summary, run_dir / "delta_pair_summary.json")
        dump_json(pair_summary, run_dir / "delta_pair_v4_summary.json")

        dump_json(
            [
                {
                    "window_id": wm.window_id,
                    "active": wm.active,
                    "a_r_size": wm.a_r_size,
                    "alpha": wm.alpha,
                    "active_clients": wm.active_clients,
                    "beta_hat": wm.beta_hat,
                }
                for wm in window_metrics
            ],
            run_dir / "window_metrics.json",
        )
        # E4 provenance: RavenAggregator records each P2 invocation together
        # with its inputs and solver diagnostics.  Other aggregators simply
        # produce an empty list, keeping the artifact shape stable.
        dump_json(
            list(getattr(runner.aggregator, "solve_results", [])),
            run_dir / "p2_invocation_states.json",
        )

    runtime = float(time.perf_counter() - t0)
    metrics["runtime_seconds"] = runtime
    metrics = finalize_metrics_dict(method, metrics)
    smoke_audit["placeholder_fields"] = [
        k
        for k in REQUIRED_METRICS
        if metrics.get(f"{k}_applicability") == "APPLICABLE" and metrics.get(k) is None
    ]
    if smoke_audit["placeholder_fields"]:
        smoke_audit["status"] = "BLOCKED_PLACEHOLDER_METRICS"

    # ACCEPTANCE_GATE_FIX / NONFINITE_PROPAGATION_FIX: never accept nonfinite metrics
    from raven_mcs.e3.numerical.finite import NonfiniteNumericalState, is_finite_number

    for key in ("RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho"):
        app = str(metrics.get(f"{key}_applicability", "APPLICABLE"))
        if app in {"NOT_APPLICABLE", "N_A", "N/A"}:
            continue
        if not is_finite_number(metrics.get(key)):
            raise NonfiniteNumericalState(
                f"NONFINITE_NUMERICAL_STATE: metric {key}={metrics.get(key)!r}"
            )
    if method not in {"central_all", "central_delivered"}:
        if not is_finite_number(metrics.get("Delta_c_s")):
            raise NonfiniteNumericalState(
                f"NONFINITE_NUMERICAL_STATE: metric Delta_c_s={metrics.get('Delta_c_s')!r}"
            )

    dump_json(metrics, run_dir / "final_metrics.json")
    dump_json(smoke_audit, run_dir / "method_smoke_audit.json")
    ckpt_hash = (
        sha256_file(run_dir / "checkpoints" / "final.pt")
        if (run_dir / "checkpoints" / "final.pt").is_file()
        else None
    )
    manifest = {
        "run_id": run_id,
        "attempt_id": attempt_id,
        "dataset": dataset_name,
        "seed": int(seed),
        "scenario": scenario,
        "method": method,
        "path": "REAL",
        "status": smoke_audit["status"],
        "config_hash": config_hash,
        "EventTrace_hash": et_hash,
        "checkpoint_hash": ckpt_hash,
        "metric_hash": sha256_file(run_dir / "final_metrics.json"),
        "pair_state_schema_version": PAIR_SCHEMA_VERSION,
        "n_groups_runtime": n_groups,
        "n_groups_frozen": bundle["n_groups_frozen"],
        "no_performance_claim": True,
    }
    dump_json(manifest, run_dir / "runtime_manifest.json")
    _append_ledger(
        ledger_path,
        {
            "event": "FINISH",
            "run_id": run_id,
            "attempt_id": attempt_id,
            "exit_code": 0,
            "runtime": runtime,
            "checkpoint_hash": ckpt_hash,
            "metrics_hash": sha256_file(run_dir / "final_metrics.json"),
            "git_commit": source_identity.get("git_commit"),
            "source_manifest_hash": source_identity.get("source_manifest_hash"),
            "status": smoke_audit["status"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    completed_windows = None
    wm_path = run_dir / "window_metrics.json"
    if wm_path.is_file():
        try:
            completed_windows = len(json.loads(wm_path.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            completed_windows = None
    return {
        "run_id": run_id,
        "metrics": metrics,
        "pair_summary": pair_summary,
        "smoke_audit": smoke_audit,
        "manifest": manifest,
        "target_wiring": bundle,
        "status": smoke_audit["status"],
        "completed_windows": completed_windows,
    }


def CommonNDMF_from_ckpt(path: Path, num_spatial: int):
    from raven_mcs.models.common_ndmf import CommonNDMF

    model = CommonNDMF(num_spatial=num_spatial)
    payload = torch.load(path, map_location="cpu")
    if isinstance(payload, dict) and "state_dict" in payload:
        model.load_state_dict(payload["state_dict"])
    else:
        model.load_state_dict(payload)
    model.eval()
    return model


def _predict_model(model, dataset: ProcessedDataset) -> dict[str, Any]:
    class _R:
        pass

    r = _R()
    r.model = model
    return _predict(r, dataset)
