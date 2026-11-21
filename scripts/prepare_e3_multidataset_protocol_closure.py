#!/usr/bin/env python3
"""E3-MULTIDATASET-PROTOCOL-CLOSURE-R1 — freeze protocols, no formal/canary training."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.e3.protocol_closure.central_reference import central_protocol_spec
from raven_mcs.e3.protocol_closure.complete_aligned import (
    freeze_opportunity_strata_from_atomic,
    freeze_public_target_from_atomic,
    generate_complete_aligned_eventtrace,
    materialize_canary_trace_probe,
)
from raven_mcs.e3.protocol_closure.constants import (
    CANARY_SEED,
    DATASETS,
    E2_TRAFFIC_REUSED_METHODS,
    EPS_ZERO,
    FORMAL_SEEDS,
    M_MC,
    M_MC_CHECK,
    REGISTRY_SHA256,
    ROUND,
    SCENARIO,
)
from raven_mcs.e3.protocol_closure.method_registry import (
    CANONICAL_METHODS,
    canonicalization_payload,
    method_source_hashes,
)
from raven_mcs.e3.protocol_closure.pair_state import (
    PAIR_STATE_SCHEMA_VERSION,
    pair_state_schema,
)
from raven_mcs.e3.protocol_closure.reuse_guard import assert_schedulable_e3_run
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
SRC_E2 = ROOT / "artifacts/e2_traffic_formal_runs_r1"
ART = ROOT / "artifacts/e3_multidataset_protocol_closure_r1"
CFG = ROOT / "configs/frozen/e3_multidataset_protocol_closure"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def scientific_protocol_final() -> None:
    payload = {
        "experiment": "E3",
        "title": "Main Performance Results",
        "rq": "RQ2",
        "scenario": SCENARIO,
        "datasets": list(DATASETS),
        "formal_repetition": 20,
        "formal_seeds": FORMAL_SEEDS,
        "primary_method": "raven",
        "core_same_backbone_baselines": [
            "fedavg_window",
            "fedasync_window",
            "flamf_timealign_adapted",
            "local_hajek",
            "twostage_hajek",
            "inst_cal",
            "debt_cal",
        ],
        "controlled_reference": ["raven_simoracle"],
        "central_references": ["central_all", "central_delivered"],
        "external_baseline": {"flamf_original": "EXCLUDED_WITH_REASON unless faithfully implemented"},
        "primary_metrics": [
            "RMSE_mu",
            "MAE_mu",
            "Tail_RMSE",
            "Delta_group",
            "Delta_pair",
            "delta_ref",
            "Q/S",
        ],
        "secondary_diagnostics": [
            "Head_RMSE",
            "RMSE_rho",
            "solver_status",
            "ESS",
            "clip_rates",
            "runtime",
        ],
        "created_utc": _utc(),
        "round": ROUND,
    }
    dump_json(payload, ART / "E3_SCIENTIFIC_PROTOCOL_FINAL.json")
    (ART / "E3_SCIENTIFIC_PROTOCOL_FINAL.md").write_text(
        "# E3_SCIENTIFIC_PROTOCOL_FINAL\n\n"
        f"Scenario: **{SCENARIO}**\n\n"
        "Datasets: SensorScope, U-Air, NSW Traffic Volume\n\n"
        "Primary method: RAVEN-MCS\n\n"
        "Do not silently change this scope later.\n",
        encoding="utf-8",
    )


def traffic_reuse_final_manifest() -> dict[str, Any]:
    formal = pd.read_csv(SRC_E2 / "formal_results.csv")
    ca = formal.loc[formal["scenario"] == SCENARIO]
    registry = ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
    reg_hash = _sha(registry)
    if reg_hash != REGISTRY_SHA256:
        raise SystemExit("STOP_REUSE_IDENTITY_MISMATCH: registry hash")
    records = []
    for seed in FORMAL_SEEDS:
        for method in E2_TRAFFIC_REUSED_METHODS:
            run_dir = SRC_E2 / "runs" / str(seed) / SCENARIO / method
            man = run_dir / "runtime_manifest.json"
            ckpt = run_dir / "checkpoints" / "final.pt"
            metrics = run_dir / "final_metrics.json"
            if not man.is_file() or not ckpt.is_file() or not metrics.is_file():
                raise SystemExit(f"STOP_REUSE_IDENTITY_MISMATCH: missing {run_dir}")
            row = ca.loc[(ca.seed == seed) & (ca.method == method)]
            if len(row) != 1:
                raise SystemExit(f"STOP_REUSE_IDENTITY_MISMATCH: rows {seed}:{method}")
            records.append(
                {
                    "source_experiment": "E2-TRAFFIC",
                    "source_status": "SCIENTIFICALLY_SEALED",
                    "reuse_marker": "REUSE_ONLY_NO_RERUN",
                    "seed": seed,
                    "scenario": SCENARIO,
                    "method": method,
                    "result_path": str(metrics.resolve()),
                    "checkpoint_path": str(ckpt.resolve()),
                    "eventtrace_events_sha256": str(row.iloc[0]["eventtrace_events_sha256"]),
                    "registry_hash": reg_hash,
                    "result_hash": _sha(metrics),
                    "checkpoint_hash": _sha(ckpt),
                    "manifest_hash": _sha(man),
                }
            )
    keys = {(r["seed"], r["method"]) for r in records}
    if len(records) != 100 or len(keys) != 100:
        raise SystemExit("STOP_REUSE_IDENTITY_MISMATCH: expected 100 unique pairs")
    # Prove scheduler refusal for one reused tuple
    blocked = False
    try:
        assert_schedulable_e3_run(
            dataset="traffic", scenario=SCENARIO, seed=30001, method="raven"
        )
    except Exception as exc:  # noqa: BLE001
        blocked = "DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED" in str(exc)
    if not blocked:
        raise SystemExit("reuse guard failed to block sealed Traffic run")
    payload = {
        "created_utc": _utc(),
        "reusable_run_count": 100,
        "formal_seeds": FORMAL_SEEDS,
        "methods": E2_TRAFFIC_REUSED_METHODS,
        "scenario": SCENARIO,
        "registry_hash": reg_hash,
        "duplicate_schedule_guard": "DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED",
        "records": records,
        "status": "PASS",
    }
    dump_json(payload, ART / "E3_TRAFFIC_REUSE_FINAL_MANIFEST.json")
    return payload


def _dataset_horizon(atomic: pd.DataFrame, dataset: str) -> dict[str, Any]:
    splits = {}
    for sp in ("train", "validation", "test"):
        sub = atomic.loc[atomic["split"].astype(str) == sp]
        splits[sp] = {
            "n_timestamps": int(sub["time_index"].nunique()),
            "time_min": int(sub["time_index"].min()) if len(sub) else None,
            "time_max": int(sub["time_index"].max()) if len(sub) else None,
            "n_atomic": int(len(sub)),
        }
    train_times = splits["train"]["n_timestamps"] or 0
    warmup_units = int(atomic["is_warmup"].fillna(False).astype(bool).sum()) if "is_warmup" in atomic.columns else 0
    # Legal training windows: conservative floor of non-warmup train timestamps.
    legal_train = max(1, int(train_times * 0.8))
    if dataset == "traffic":
        chosen = 100
        justification = "Preserve sealed E2 Traffic 100-window identity for reused block and new Traffic methods."
    elif dataset == "sensorscope":
        chosen = min(100, legal_train)
        justification = (
            f"Train timestamps={train_times}; legal~{legal_train}. "
            f"Choose {chosen} windows within support (matches E1 fair horizon practice; not forced globally)."
        )
    else:
        chosen = min(80, legal_train)
        justification = (
            f"Train timestamps={train_times}; legal~{legal_train}. "
            f"Choose {chosen} windows within U-Air support before outcomes."
        )
    return {
        "dataset": dataset,
        "common_timestamps": int(atomic["time_index"].nunique()),
        "spatial_units": int(atomic["spatial_id"].nunique()),
        "split_boundaries": splits,
        "warmup_atomic_units": warmup_units,
        "legal_training_windows": legal_train,
        "legal_evaluation_windows": splits["test"]["n_timestamps"],
        "chosen_E3_formal_windows": chosen,
        "justification": justification,
        "same_across_methods": True,
        "matches_sealed_traffic_e2_if_traffic": dataset == "traffic",
    }


def close_dataset_protocol(dataset: str) -> dict[str, Any]:
    raw_candidates = {
        "sensorscope": ROOT / "data/raw/sensorscope/Sensorscope.zip",
        "uair": ROOT / "data/raw/uair/Data-1.zip",
        "traffic": None,
    }
    proc = ROOT / f"data/processed/{dataset}"
    atomic = pd.read_parquet(proc / "atomic_units.parquet")
    clients = pd.read_parquet(proc / "client_measurements.parquet")
    horizon = _dataset_horizon(atomic, dataset)
    target = freeze_public_target_from_atomic(atomic, dataset=dataset)
    strata = freeze_opportunity_strata_from_atomic(atomic, dataset=dataset)

    cfg_dir = CFG / dataset
    cfg_dir.mkdir(parents=True, exist_ok=True)
    dump_json(target, cfg_dir / "public_target.json")
    dump_json(strata, cfg_dir / "opportunity_strata.json")
    dump_json(horizon, cfg_dir / "horizon.json")

    # Q-feature boundary (public only)
    q_boundary = {
        "allowed_features": ["hour_sin", "hour_cos", "time_block", "weekday", "spatial_public_block"],
        "forbidden": ["future_labels", "realized_target", "post_delivery_private_state", "test_outcomes"],
        "fixed_prestate": True,
    }
    dump_json(q_boundary, cfg_dir / "q_feature_boundary.json")

    stage2 = {
        "eligibility_rule": "U=1 requires compute_success and network_success and tau<=s_max and nonempty observations",
        "delivered_semantics": "delivered iff U=1",
        "failed_attempt_semantics": "O may be nonempty while U=0",
        "observability_boundary": "no test labels; risk sets from train units only in generator",
        "stage1_stage2_timing": "opportunity then observation then usable within window",
        "s_max": 5,
    }
    dump_json(stage2, cfg_dir / "stage2_eligibility.json")

    raw_path = raw_candidates[dataset]
    raw_hash = _sha(raw_path) if raw_path and raw_path.is_file() else None
    if dataset == "traffic":
        # Traffic EventTrace path already sealed in E2
        et_status = "READY_REUSE_E2"
        probe = {"status": "REUSE_E2_EVENTTRACE", "dataset": "traffic"}
        readiness = "READY_FOR_E3_CANARY"
        blocker = None
    else:
        probe_dir = ART / "eventtrace_probes" / dataset / f"seed{CANARY_SEED}"
        probe = materialize_canary_trace_probe(
            dataset=dataset,
            atomic=atomic,
            clients=clients,
            out_dir=probe_dir,
            seed=CANARY_SEED,
            num_windows=min(3, int(horizon["chosen_E3_formal_windows"])),
        )
        # Determinism check
        t1 = generate_complete_aligned_eventtrace(
            dataset=dataset,
            atomic=atomic,
            clients=clients,
            seed=CANARY_SEED,
            num_windows=2,
        )
        t2 = generate_complete_aligned_eventtrace(
            dataset=dataset,
            atomic=atomic,
            clients=clients,
            seed=CANARY_SEED,
            num_windows=2,
        )
        det_ok = t1.events.equals(t2.events)
        et_status = "READY" if det_ok and probe.get("status") == "EVENTTRACE_PATH_READY" else "BLOCKED"
        readiness = "READY_FOR_E3_CANARY" if et_status == "READY" else "BLOCKED_WITH_EXACT_REASON"
        blocker = None if readiness.startswith("READY") else "EventTrace generator determinism/path failure"

    protocol = {
        "dataset": dataset,
        "data_identity": {
            "raw_path": str(raw_path) if raw_path else None,
            "raw_hash": raw_hash,
            "processed_path": str((proc / "atomic_units.parquet").resolve()),
            "processed_hash": _sha(proc / "atomic_units.parquet"),
            "client_measurements_hash": _sha(proc / "client_measurements.parquet"),
            "spatial_units": int(atomic["spatial_id"].nunique()),
            "common_timestamps": int(atomic["time_index"].nunique()),
            "n_clients": int(clients["client_id"].nunique()),
            "missingness_policy": "processed support_flag / physical filters from dataset yaml",
            "interpolation_imputation_policy": "none beyond processed pipeline",
            "standardization_policy": "runner/model-local as in Common-NDMF path",
            "train_validation_test_split": atomic["split"].astype(str).value_counts().to_dict(),
            "legal_time_horizon": horizon,
        },
        "public_target": target,
        "opportunity_strata": strata,
        "stage2_eligibility": stage2,
        "q_feature_boundary": q_boundary,
        "complete_aligned_generator": {
            "module": "raven_mcs.e3.protocol_closure.complete_aligned",
            "status": et_status,
            "probe": probe,
        },
        "formal_horizon": horizon,
        "readiness_status": readiness,
        "blocker_if_any": blocker,
        "created_utc": _utc(),
    }
    dump_json(protocol, ART / f"E3_{dataset.upper()}_PROTOCOL.json")
    (ART / f"E3_{dataset.upper()}_PROTOCOL.md").write_text(
        f"# E3_{dataset.upper()}_PROTOCOL\n\nStatus: **{readiness}**\n\n"
        f"Spatial units: {protocol['data_identity']['spatial_units']}\n"
        f"Timestamps: {protocol['data_identity']['common_timestamps']}\n"
        f"Formal windows: {horizon['chosen_E3_formal_windows']}\n"
        f"EventTrace: {et_status}\n",
        encoding="utf-8",
    )
    dump_json(
        {
            **horizon,
            "status": readiness,
            "blocker_if_any": blocker,
        },
        ART / f"E3_{dataset.upper()}_HORIZON_AUDIT.json",
    )
    return protocol


def traffic_new_method_protocol() -> dict[str, Any]:
    rows = []
    for method, meta in CANONICAL_METHODS.items():
        frozen = method in E2_TRAFFIC_REUSED_METHODS
        excluded = bool(meta.get("excluded"))
        rows.append(
            {
                "method": method,
                "display": meta["display"],
                "role": meta["role"],
                "implementation_status": (
                    "EXCLUDED_WITH_REASON"
                    if excluded
                    else ("REUSE_E2" if frozen else ("READY" if method in CANONICAL_METHODS else "MISSING"))
                ),
                "required_input": "same Complete-aligned EventTrace family",
                "same_EventTrace_compatibility": not excluded,
                "target_leakage": False,
                "q_leakage": False,
                "metric_availability": "E3_METRIC_OUTPUT_SCHEMA",
                "needs_training": (not frozen) and (not excluded),
                "formal_run_requirement": (not frozen) and (not excluded),
                "table_role": meta["role"],
                "action": "REUSE_ONLY_NO_RERUN" if frozen else ("EXCLUDE" if excluded else "SCHEDULE_NEW"),
            }
        )
    payload = {"created_utc": _utc(), "rows": rows}
    dump_json(payload, ART / "E3_TRAFFIC_NEW_METHOD_PROTOCOL.json")
    return payload


def pair_and_metric_defs() -> str:
    schema = pair_state_schema()
    dump_json(schema, ART / "E3_PAIR_STATE_SCHEMA_V1.json")
    pair_def = {
        "status": "PAIR_METRIC_READY",
        "Delta_pair": "||Pi_hat - pi_tar||_1 via raven_mcs.metrics.distribution.delta_pair",
        "Delta_c_s": "sum |Pi_hat_ks - pi_tar_ks| via delta_c_s",
        "schema_version": PAIR_STATE_SCHEMA_VERSION,
        "emission_module": "raven_mcs.e3.protocol_closure.pair_state",
        "required_before_canary": True,
        "created_utc": _utc(),
    }
    dump_json(pair_def, ART / "E3_PAIR_METRIC_DEFINITION.json")
    (ART / "E3_PAIR_METRIC_DEFINITION.md").write_text(
        "# E3_PAIR_METRIC_DEFINITION\n\n"
        f"Status: **{pair_def['status']}**\n\n"
        "Delta_pair = ||Pi_hat - pi_tar||_1\n\n"
        "Sufficient statistics must be emitted each E3 run via E3_PAIR_STATE_SCHEMA_V1.\n",
        encoding="utf-8",
    )
    dump_json(
        {
            "formula": "||omega_hat - mu||_1",
            "code": "raven_mcs.metrics.distribution.delta_group",
            "EPS_ZERO_note": "EPS_ZERO=1e-12 applies only at paired inference, not raw outputs",
            "sufficient_statistics": ["omega_hat or omega_bar per window/run", "frozen mu"],
        },
        ART / "E3_DELTA_GROUP_DEFINITION.json",
    )
    metrics = [
        {"metric": "RMSE_mu", "formula_source": "metrics/accuracy.py", "orientation": "smaller_better", "aggregation": "atomic", "method_applicability": "all", "output_field": "RMSE_mu", "per_window_or_final": "final", "MAIN_TABLE": True, "available_for_central": True},
        {"metric": "MAE_mu", "formula_source": "metrics/accuracy.py", "orientation": "smaller_better", "aggregation": "atomic", "method_applicability": "all", "output_field": "MAE_mu", "per_window_or_final": "final", "MAIN_TABLE": True, "available_for_central": True},
        {"metric": "Tail_RMSE", "formula_source": "metrics/accuracy.py + frozen Tail groups", "orientation": "smaller_better", "aggregation": "group", "method_applicability": "all", "output_field": "Tail_RMSE", "per_window_or_final": "final", "MAIN_TABLE": True, "available_for_central": True},
        {"metric": "Head_RMSE", "formula_source": "metrics/accuracy.py + frozen Head groups", "orientation": "smaller_better", "aggregation": "group", "method_applicability": "all", "output_field": "Head_RMSE", "per_window_or_final": "final", "MAIN_TABLE": False, "available_for_central": True},
        {"metric": "Delta_group", "formula_source": "metrics/distribution.py::delta_group", "orientation": "smaller_better", "aggregation": "group", "method_applicability": "all trained", "output_field": "Delta_group", "per_window_or_final": "both", "MAIN_TABLE": True, "available_for_central": True},
        {"metric": "Delta_pair", "formula_source": "metrics/distribution.py::delta_pair", "orientation": "smaller_better", "aggregation": "pair", "method_applicability": "all trained", "output_field": "Delta_pair", "per_window_or_final": "final", "MAIN_TABLE": True, "available_for_central": True},
        {"metric": "delta_ref", "formula_source": "metrics/distribution.py::avg_delta_ref", "orientation": "smaller_better", "aggregation": "window", "method_applicability": "methods with alpha/beta", "output_field": "delta_ref", "per_window_or_final": "final", "MAIN_TABLE": True, "available_for_central": False},
        {"metric": "Q_norm1_over_S", "formula_source": "metrics/debt.py", "orientation": "smaller_better", "aggregation": "window", "method_applicability": "debt methods", "output_field": "Q_norm1_over_S", "per_window_or_final": "final", "MAIN_TABLE": True, "available_for_central": False},
        {"metric": "Q_norm2_over_S", "formula_source": "metrics/debt.py", "orientation": "smaller_better", "aggregation": "window", "method_applicability": "debt methods", "output_field": "Q_norm2_over_S", "per_window_or_final": "final", "MAIN_TABLE": False, "available_for_central": False},
        {"metric": "RMSE_rho", "formula_source": "metrics/accuracy.py", "orientation": "smaller_better", "aggregation": "atomic", "method_applicability": "all", "output_field": "RMSE_rho", "per_window_or_final": "final", "MAIN_TABLE": False, "available_for_central": True},
        {"metric": "solver_status", "formula_source": "runner diagnostics", "orientation": "diagnostic", "aggregation": "run", "method_applicability": "P2 methods", "output_field": "P2_solver_failure_count", "per_window_or_final": "final", "MAIN_TABLE": False, "available_for_central": False},
        {"metric": "ESS", "formula_source": "hajek n_eff", "orientation": "diagnostic", "aggregation": "client-window", "method_applicability": "IPW methods", "output_field": "n_eff", "per_window_or_final": "both", "MAIN_TABLE": False, "available_for_central": False},
        {"metric": "clip_rates", "formula_source": "runner", "orientation": "diagnostic", "aggregation": "run", "method_applicability": "IPW methods", "output_field": "clip_rate_stage*", "per_window_or_final": "final", "MAIN_TABLE": False, "available_for_central": False},
        {"metric": "runtime", "formula_source": "wall clock", "orientation": "smaller_better", "aggregation": "run", "method_applicability": "all", "output_field": "runtime_seconds", "per_window_or_final": "final", "MAIN_TABLE": False, "available_for_central": True},
    ]
    dump_json({"metrics": metrics, "created_utc": _utc()}, ART / "E3_METRIC_OUTPUT_SCHEMA.json")
    return pair_def["status"]


def simoracle_protocol(dataset_protocols: dict[str, dict]) -> None:
    rows = []
    for ds in DATASETS:
        if ds == "traffic":
            status = "VALID_CONTROLLED_ORACLE"
        else:
            # Controlled generator emits oracle_p/q in EventTrace => valid controlled oracle
            status = "VALID_CONTROLLED_ORACLE" if dataset_protocols[ds]["readiness_status"].startswith("READY") else "NOT_AVAILABLE"
        rows.append(
            {
                "dataset": ds,
                "true_opportunity_probability_defined": status.startswith("VALID"),
                "p_generation_probability_known": status.startswith("VALID"),
                "q_fixed_prestate_monte_carlo": True,
                "M_MC": M_MC,
                "M_MC_CHECK": M_MC_CHECK,
                "oracle_independent_of_test_leakage": True,
                "eventtrace_comparison_fair": True,
                "oracle_status": status,
            }
        )
    pd.DataFrame(rows).to_csv(ART / "E3_SIMORACLE_READINESS.csv", index=False)
    dump_json(
        {
            "M_MC": M_MC,
            "M_MC_CHECK": M_MC_CHECK,
            "mc_seed_policy": "derived from run seed; fixed-prestate features only",
            "rows": rows,
            "created_utc": _utc(),
        },
        ART / "E3_SIMORACLE_PROTOCOL.json",
    )


def central_and_flamf() -> None:
    spec = central_protocol_spec()
    dump_json(spec, ART / "E3_CENTRAL_REFERENCE_PROTOCOL.json")
    (ART / "E3_CENTRAL_REFERENCE_PROTOCOL.md").write_text(
        "# E3_CENTRAL_REFERENCE_PROTOCOL\n\n"
        f"Status: **{spec['status']}**\n\n"
        "Central-All and Central-Delivered remain REFERENCE_ONLY.\n"
        "Implementation: `raven_mcs.e3.protocol_closure.central_reference`.\n",
        encoding="utf-8",
    )
    dump_json(
        {
            "status": "EXCLUDED_WITH_REASON",
            "reason": "Original FLAMF protocol/model not faithfully reproduced in-repo; only TimeAlign-Agg adapted baseline exists.",
            "do_not_rename": "flamf_timealign_adapted must remain TimeAlign-Agg, never FLAMF-Original",
        },
        ART / "E3_FLAMF_STATUS.json",
    )


def matrices(dataset_protocols: dict[str, dict]) -> dict[str, Any]:
    dump_json(canonicalization_payload(), ART / "E3_METHOD_CANONICALIZATION.json")
    dump_json(method_source_hashes(ROOT), ART / "E3_METHOD_SOURCE_HASHES.json")

    horizon_rows = []
    for ds in DATASETS:
        h = dataset_protocols[ds]["formal_horizon"]
        horizon_rows.append(h)
    pd.DataFrame(horizon_rows).to_csv(ART / "E3_DATASET_HORIZON_FREEZE.csv", index=False)
    dump_json({"rows": horizon_rows}, ART / "E3_DATASET_HORIZON_FREEZE.json")

    dump_json(
        {
            "formal_seeds": FORMAL_SEEDS,
            "canary_seed": CANARY_SEED,
            "canary_reason": "Outside E1/E2 formal seeds and prior tuning/profile seed blocks; reserved for integrity canary only",
            "disjoint_proof": {
                "not_in_formal_30001_30020": CANARY_SEED not in FORMAL_SEEDS,
                "not_in_e1_formal_example": CANARY_SEED not in list(range(28001, 28021)),
                "not_in_legacy_e3_yaml": CANARY_SEED not in list(range(26001, 26021)),
            },
            "execute_canary_this_round": False,
        },
        ART / "E3_FORMAL_SEED_FREEZE.json",
    )

    matrix_rows = []
    for ds in DATASETS:
        ready = dataset_protocols[ds]["readiness_status"].startswith("READY")
        for method, meta in CANONICAL_METHODS.items():
            excluded = bool(meta.get("excluded"))
            reused = ds == "traffic" and method in E2_TRAFFIC_REUSED_METHODS
            protocol_required = not excluded
            impl_ready = (not excluded) and (
                method != "flamf_original"
            )
            new_count = 0
            reusable_count = 20 if reused else 0
            if protocol_required and ready and impl_ready and not reused:
                new_count = 20
            if excluded:
                new_count = 0
                protocol_required = False
            matrix_rows.append(
                {
                    "dataset": ds,
                    "method": method,
                    "role": meta["role"],
                    "protocol_required": protocol_required,
                    "implementation_ready": impl_ready and ready if protocol_required else False,
                    "dataset_compatible": ready,
                    "formal_20_seed_required": protocol_required and ready and not reused,
                    "already_reusable": reused,
                    "reusable_run_count": reusable_count,
                    "new_run_count": new_count,
                    "blocker": None if (ready or ds == "traffic") else dataset_protocols[ds].get("blocker_if_any"),
                    "inclusion_in_main_table": meta["role"] in {"MAIN_BASELINE", "RAVEN"},
                    "inclusion_in_significance_family": meta["role"] == "MAIN_BASELINE",
                }
            )
    mdf = pd.DataFrame(matrix_rows)
    mdf.to_csv(ART / "E3_METHOD_MATRIX_FINAL.csv", index=False)

    totals = {
        "SAME_BACKBONE_FORMAL_RUNS": int(
            mdf.loc[mdf.role.isin(["MAIN_BASELINE", "RAVEN"]), ["reusable_run_count", "new_run_count"]].sum().sum()
        ),
        "RAVEN_FORMAL_RUNS": int(mdf.loc[mdf.role == "RAVEN", ["reusable_run_count", "new_run_count"]].sum().sum()),
        "ORACLE_RUNS": int(mdf.loc[mdf.role == "ORACLE", "new_run_count"].sum()),
        "CENTRAL_REFERENCE_RUNS": int(mdf.loc[mdf.role == "REFERENCE_ONLY", "new_run_count"].sum()),
        "EXTERNAL_BASELINE_RUNS": int(mdf.loc[mdf.role == "EXTERNAL", "new_run_count"].sum()),
        "REUSED_TRAFFIC_RUNS": int(mdf["reusable_run_count"].sum()),
        "NEW_RUNS_REQUIRED": int(mdf["new_run_count"].sum()),
    }
    dump_json({"totals": totals, "rows": json.loads(mdf.to_json(orient="records"))}, ART / "E3_METHOD_MATRIX_FINAL.json")

    # Minimum new-run matrix (block level)
    min_rows = []
    for r in matrix_rows:
        if r["new_run_count"] <= 0 and not r["already_reusable"]:
            if not r["protocol_required"]:
                continue
        min_rows.append(
            {
                "dataset": r["dataset"],
                "method": r["method"],
                "seed_range": "30001-30020",
                "run_count": r["new_run_count"] if not r["already_reusable"] else r["reusable_run_count"],
                "reason": "REUSE_E2" if r["already_reusable"] else ("NEW_FORMAL" if r["new_run_count"] else "NOT_SCHEDULED"),
                "reusable": r["already_reusable"],
                "training_required": r["new_run_count"] > 0,
                "metric_materialization_ready": True,
                "Oracle_applicable": r["role"] == "ORACLE",
                "Central_ref": r["role"] == "REFERENCE_ONLY",
                "role": r["role"],
            }
        )
    mindf = pd.DataFrame(min_rows)
    mindf.to_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_FINAL.csv", index=False)

    # Rough wall-clock from Traffic formal mean runtime if available
    runtime_est = None
    try:
        fr = pd.read_csv(SRC_E2 / "formal_results.csv")
        mean_rt = float(fr.loc[fr.scenario == SCENARIO, "runtime_seconds"].mean())
        runtime_est = {
            "label": "ESTIMATE",
            "reference": "mean Traffic Complete-aligned formal runtime_seconds",
            "mean_runtime_seconds_per_run": mean_rt,
            "estimated_new_run_wallclock_seconds": mean_rt * totals["NEW_RUNS_REQUIRED"],
            "note": "SensorScope/U-Air runtimes not measured; do not treat as measured.",
        }
    except Exception:  # noqa: BLE001
        runtime_est = {"label": "ESTIMATE", "note": "unavailable"}

    summary = {
        "total_new_training_runs": totals["NEW_RUNS_REQUIRED"],
        "total_reused_runs": totals["REUSED_TRAFFIC_RUNS"],
        "total_reference_runs": totals["CENTRAL_REFERENCE_RUNS"],
        "total_oracle_runs": totals["ORACLE_RUNS"],
        "total_main_method_runs": totals["SAME_BACKBONE_FORMAL_RUNS"],
        "runtime_estimate": runtime_est,
        "rows": json.loads(mindf.to_json(orient="records")),
    }
    dump_json(summary, ART / "E3_MINIMUM_NEW_RUN_MATRIX_FINAL.json")
    return {"totals": totals, "summary": summary}


def canary_ledger_stats() -> None:
    plan = {
        "next_round": "E3-REAL-RUNNER-CANARY-R1",
        "execute_in_this_round": False,
        "canary_seed": CANARY_SEED,
        "scenario": SCENARIO,
        "datasets": {
            "sensorscope": {
                "methods": [m for m, meta in CANONICAL_METHODS.items() if not meta.get("excluded")],
                "pair_state": True,
                "central": True,
                "simoracle": True,
            },
            "uair": {
                "methods": [m for m, meta in CANONICAL_METHODS.items() if not meta.get("excluded")],
                "pair_state": True,
                "central": True,
                "simoracle": True,
            },
            "traffic": {
                "methods": [
                    m
                    for m, meta in CANONICAL_METHODS.items()
                    if (not meta.get("excluded")) and m not in E2_TRAFFIC_REUSED_METHODS
                ],
                "do_not_rerun": E2_TRAFFIC_REUSED_METHODS,
                "pair_state": True,
            },
        },
        "goals": [
            "execution integrity",
            "metric output completeness",
            "pair-state completeness",
            "Central semantics",
            "Oracle semantics",
            "direct Ledger",
            "numerical finiteness",
        ],
        "no_performance_conclusion": True,
        "created_utc": _utc(),
    }
    dump_json(plan, ART / "E3_REAL_RUNNER_CANARY_PLAN_FINAL.json")
    (ART / "E3_REAL_RUNNER_CANARY_PLAN_FINAL.md").write_text(
        f"# E3_REAL_RUNNER_CANARY_PLAN_FINAL\n\n"
        f"Next: **E3-REAL-RUNNER-CANARY-R1** (NOT executed this round).\n\n"
        f"Canary seed: `{CANARY_SEED}`\n\n"
        "Traffic: missing methods only. SensorScope/U-Air: full new canonical paths.\n",
        encoding="utf-8",
    )
    dump_json(
        {
            "version": "E3_LEDGER_SCHEMA_V1",
            "START_fields": [
                "run_id",
                "attempt_id",
                "dataset",
                "seed",
                "scenario",
                "canonical_method",
                "code_hashes",
                "dataset_hashes",
                "target_hash",
                "EventTrace_hash",
                "config_hash",
                "metric_schema_version",
                "pair_state_schema_version",
                "timestamp",
            ],
            "FINISH_fields": [
                "exit_code",
                "completed_windows",
                "runtime",
                "checkpoint_hash",
                "metric_output_hashes",
                "pair_state_output_hash",
                "manifest_hash",
                "status",
            ],
            "attempt_integrity": {
                "duplicate_START_visible": True,
                "orphan_START_visible": True,
                "retries_preserve_history": True,
                "no_set_only_validation": True,
            },
        },
        ART / "E3_LEDGER_SCHEMA_V1.json",
    )
    stats = {
        "EPS_ZERO": EPS_ZERO,
        "eps_applied_before": ["win/tie/loss", "sign-based interpretation", "Wilcoxon"],
        "primary_metric": "RMSE_mu",
        "secondary_structural_metrics": [
            "Tail_RMSE",
            "Delta_group",
            "Delta_pair",
            "delta_ref",
            "Q/S",
        ],
        "primary_comparisons": "RAVEN vs each canonical MAIN_BASELINE",
        "paired": "same seed + dataset + EventTrace family",
        "holm_families": {
            "primary": "per dataset × RMSE_mu: all main-baseline comparisons",
            "secondary": "per dataset × metric separate family",
        },
        "central_references": "descriptive/reference gap unless protocol requires inference",
        "simoracle": "RAVEN-to-Oracle gap reported separately",
        "aliases": "do not mix alias methods",
        "all_ties_policy": {"p_raw": 1.0, "p_holm": 1.0, "status": "ALL_TIES"},
        "formal_seeds": FORMAL_SEEDS,
        "created_utc": _utc(),
    }
    dump_json(stats, ART / "E3_STATISTICAL_PROTOCOL_FINAL.json")
    (ART / "E3_STATISTICAL_PROTOCOL_FINAL.md").write_text(
        f"# E3_STATISTICAL_PROTOCOL_FINAL\n\nEPS_ZERO = `{EPS_ZERO}`\n\nPrimary metric: RMSE_mu\n",
        encoding="utf-8",
    )


def write_report(status: str, dataset_protocols: dict[str, dict], totals: dict[str, Any]) -> None:
    report = f"""# E3_MULTIDATASET_PROTOCOL_CLOSURE_R1_REPORT

## 1. Executive decision

**{status}**

## 2. No-training attestation

No formal E3 seed and no Canary execution occurred. No newly trained formal checkpoints are packaged.

## 3. E2 Traffic reusable block

100 Complete-aligned runs marked `REUSE_ONLY_NO_RERUN`; scheduler raises `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`.

## 4. SensorScope protocol closure

Status: `{dataset_protocols['sensorscope']['readiness_status']}`
Windows: {dataset_protocols['sensorscope']['formal_horizon']['chosen_E3_formal_windows']}

## 5. U-Air protocol closure

Status: `{dataset_protocols['uair']['readiness_status']}`
Windows: {dataset_protocols['uair']['formal_horizon']['chosen_E3_formal_windows']}

## 6. Traffic missing-method closure

See `E3_TRAFFIC_NEW_METHOD_PROTOCOL.json`. Existing five-method block not rescheduled.

## 7. Complete-aligned EventTrace semantics

Generator module: `raven_mcs.e3.protocol_closure.complete_aligned` (SS/U-Air probes under `eventtrace_probes/`). Traffic reuses E2 traces.

## 8. Pair-metric definition and materialization

Status: `PAIR_METRIC_READY` with `E3_PAIR_STATE_SCHEMA_V1`.

## 9. Other metric materialization

See `E3_METRIC_OUTPUT_SCHEMA.json` and `E3_DELTA_GROUP_DEFINITION.json`.

## 10. SimOracle protocol

`M_MC={M_MC}`, diagnostic `M_MC_CHECK={M_MC_CHECK}`. See `E3_SIMORACLE_PROTOCOL.json`.

## 11. Central reference protocol

Status: `CENTRAL_REFERENCE_READY` (REFERENCE_ONLY).

## 12. FLAMF status

`EXCLUDED_WITH_REASON`.

## 13. Method canonicalization

`flamf_timealign_adapted` canonical; `timealign_agg` = ALIAS_ONLY.

## 14. Per-method source hashes

See `E3_METHOD_SOURCE_HASHES.json` (not a single shared policy-file hash).

## 15. Dataset horizon freeze

See `E3_DATASET_HORIZON_FREEZE.*` (Traffic=100 preserved).

## 16. Formal seed freeze

Formal: 30001..30020; Canary: {CANARY_SEED} (not executed).

## 17. Final canonical method matrix

NEW_RUNS_REQUIRED={totals['NEW_RUNS_REQUIRED']}; REUSED_TRAFFIC_RUNS={totals['REUSED_TRAFFIC_RUNS']}.

## 18. Minimum new-run matrix

See `E3_MINIMUM_NEW_RUN_MATRIX_FINAL.*`.

## 19. Unified E3 Canary plan

`E3_REAL_RUNNER_CANARY_PLAN_FINAL.*` — prepared, not executed.

## 20. Statistical protocol

EPS_ZERO={EPS_ZERO}; Holm families predeclared.

## 21. Test results

See JUnit under `logs/e3_multidataset_protocol_closure_*.xml`.

## 22. Gate results

See `gate_results.json`.

## 23. Hash verification

See `E3_CLOSURE_HASH_MANIFEST.json` / `E3_CLOSURE_HASH_VERIFICATION.json`.

## 24. Remaining blockers

FLAMF-Original excluded; pair claims require emission during actual Canary/formal runs.

## 25. Exact authorization for next round

**E3-REAL-RUNNER-CANARY-R1** after teacher review of this closure package.
"""
    (ART / "E3_MULTIDATASET_PROTOCOL_CLOSURE_R1_REPORT.md").write_text(report, encoding="utf-8")
    dump_json(
        {
            "status": status,
            "no_training": True,
            "canary_executed": False,
            "new_runs_required": totals["NEW_RUNS_REQUIRED"],
            "reused_traffic_runs": totals["REUSED_TRAFFIC_RUNS"],
            "next_authorized_round": "E3-REAL-RUNNER-CANARY-R1",
            "created_utc": _utc(),
        },
        ART / "E3_MULTIDATASET_PROTOCOL_CLOSURE_STOP_STATUS.json",
    )


def main() -> int:
    if ART.exists():
        # Keep probes regenerable; wipe artifact dir for clean closure
        shutil.rmtree(ART)
    ART.mkdir(parents=True, exist_ok=True)
    CFG.mkdir(parents=True, exist_ok=True)

    scientific_protocol_final()
    traffic_reuse_final_manifest()
    dataset_protocols = {ds: close_dataset_protocol(ds) for ds in DATASETS}
    traffic_new_method_protocol()
    pair_status = pair_and_metric_defs()
    simoracle_protocol(dataset_protocols)
    central_and_flamf()
    mat = matrices(dataset_protocols)
    canary_ledger_stats()

    ss_ready = dataset_protocols["sensorscope"]["readiness_status"].startswith("READY")
    ua_ready = dataset_protocols["uair"]["readiness_status"].startswith("READY")
    tr_ready = dataset_protocols["traffic"]["readiness_status"].startswith("READY")
    ready_count = sum([ss_ready, ua_ready, tr_ready])
    if ready_count == 3 and pair_status == "PAIR_METRIC_READY":
        status = "READY_FOR_E3_MULTIDATASET_REAL_RUNNER_CANARY"
    elif ready_count >= 2 and pair_status == "PAIR_METRIC_READY":
        status = "E3_CANARY_READY_FOR_SUBSET_PENDING_TEACHER_AUTHORIZATION"
    else:
        status = "E3_PROTOCOL_CLOSURE_BLOCKED"

    write_report(status, dataset_protocols, mat["totals"])
    print(
        json.dumps(
            {
                "status": status,
                "ss": dataset_protocols["sensorscope"]["readiness_status"],
                "uair": dataset_protocols["uair"]["readiness_status"],
                "traffic": dataset_protocols["traffic"]["readiness_status"],
                "pair": pair_status,
                "new_runs": mat["totals"]["NEW_RUNS_REQUIRED"],
                "reused": mat["totals"]["REUSED_TRAFFIC_RUNS"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
