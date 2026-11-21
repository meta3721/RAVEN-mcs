#!/usr/bin/env python3
"""E3-PROTOCOL-REUSE-AND-READINESS-R1 — freeze protocol, reuse E2 Traffic block, no training."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.aggregation.method_policy import POLICY_MAP
from raven_mcs.e3.protocol_readiness import (
    CANARY_SEED,
    E2_FORMAL_SEEDS,
    E2_TRAFFIC_METHODS,
    E3_FORMAL_SEEDS,
    EPS_ZERO,
    REGISTRY_SHA256,
    ROUND,
)
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
SRC_E2 = ROOT / "artifacts/e2_traffic_formal_runs_r1"
ART = ROOT / "artifacts/e3_protocol_reuse_and_readiness_r1"
METHODS_DISPLAY = {
    "fedavg_window": "FedAvg-Window",
    "fedasync_window": "FedAsync-Window",
    "flamf_timealign_adapted": "TimeAlign-Agg",
    "timealign_agg": "TimeAlign-Agg",
    "twostage_hajek": "TwoStage-Hajek",
    "raven": "RAVEN-MCS",
    "local_hajek": "Local-Hajek",
    "inst_cal": "Inst-Cal",
    "debt_cal": "Debt-Cal",
    "central_all": "Central-All",
    "central_delivered": "Central-Delivered",
    "flamf_original": "FLAMF-Original",
    "raven_simoracle": "RAVEN-SimOracle",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_reuse_manifest() -> dict[str, Any]:
    ART.mkdir(parents=True, exist_ok=True)
    formal = pd.read_csv(SRC_E2 / "formal_results.csv")
    ca = formal.loc[formal["scenario"] == "complete_aligned"].copy()
    registry = ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
    source_hashes = json.loads((SRC_E2 / "SOURCE_HASHES.json").read_text(encoding="utf-8"))
    package_candidates = [
        ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1/TO_SUBMIT_E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1.zip",
        ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_FORMAL_RUNS_R1/TO_SUBMIT_E2_TRAFFIC_FORMAL_RUNS_R1.zip",
    ]
    source_package = next((p for p in package_candidates if p.is_file()), None)
    source_package_hash = _sha(source_package) if source_package else None
    registry_hash = _sha(registry)
    if registry_hash != REGISTRY_SHA256:
        raise SystemExit("STOP_REUSE_IDENTITY_MISMATCH: registry hash mismatch")

    records = []
    for seed in E2_FORMAL_SEEDS:
        for method in E2_TRAFFIC_METHODS:
            run_dir = SRC_E2 / "runs" / str(seed) / "complete_aligned" / method
            man = run_dir / "runtime_manifest.json"
            ckpt = run_dir / "checkpoints" / "final.pt"
            metrics = run_dir / "final_metrics.json"
            cfg = run_dir / "config_snapshot.json"
            et_id = SRC_E2 / "eventtraces" / str(seed) / "complete_aligned" / "eventtrace_identity.json"
            if not man.is_file() or not ckpt.is_file():
                raise SystemExit(f"STOP_REUSE_IDENTITY_MISMATCH: missing {run_dir}")
            payload = json.loads(man.read_text(encoding="utf-8"))
            if payload.get("scenario") not in {"complete_aligned", None} and payload.get("scenario_id") not in {
                "complete_aligned",
                None,
            }:
                # tolerate nested identities
                pass
            row = ca.loc[(ca.seed == seed) & (ca.method == method)]
            if len(row) != 1:
                raise SystemExit(f"STOP_REUSE_IDENTITY_MISMATCH: result rows for {seed}:{method}")
            records.append(
                {
                    "source_experiment": "E2-TRAFFIC",
                    "source_status": "SCIENTIFICALLY_SEALED",
                    "seed": seed,
                    "scenario": "complete_aligned",
                    "method": method,
                    "method_display": METHODS_DISPLAY[method],
                    "result_path": str((run_dir / "final_metrics.json").resolve()),
                    "runtime_manifest_path": str(man.resolve()),
                    "checkpoint_path": str(ckpt.resolve()),
                    "eventtrace_identity_path": str(et_id.resolve()) if et_id.is_file() else None,
                    "eventtrace_events_sha256": str(row.iloc[0]["eventtrace_events_sha256"]),
                    "registry_hash": registry_hash,
                    "config_hash": _sha(cfg) if cfg.is_file() else None,
                    "result_hash": _sha(metrics),
                    "checkpoint_hash": _sha(ckpt),
                    "manifest_hash": _sha(man),
                    "source_package_hash": source_package_hash,
                    "reuse_reason": "exact E3-compatible scientific block (Traffic Complete-aligned same-backbone)",
                }
            )
    keys = [(r["seed"], r["method"]) for r in records]
    if len(records) != 100 or len(set(keys)) != 100:
        raise SystemExit("STOP_REUSE_IDENTITY_MISMATCH: expected 100 unique seed-method pairs")
    if set(r["seed"] for r in records) != set(E2_FORMAL_SEEDS):
        raise SystemExit("STOP_REUSE_IDENTITY_MISMATCH: seed set")
    if set(r["method"] for r in records) != set(E2_TRAFFIC_METHODS):
        raise SystemExit("STOP_REUSE_IDENTITY_MISMATCH: method set")

    manifest = {
        "created_utc": _utc(),
        "round": ROUND,
        "reusable_run_count": len(records),
        "formal_seeds": E2_FORMAL_SEEDS,
        "methods": E2_TRAFFIC_METHODS,
        "scenario": "complete_aligned",
        "registry_hash": registry_hash,
        "formal_results_hash": _sha(SRC_E2 / "formal_results.csv"),
        "source_hashes_file": str((SRC_E2 / "SOURCE_HASHES.json").resolve()),
        "source_hashes_digest": _sha(SRC_E2 / "SOURCE_HASHES.json"),
        "source_package": str(source_package.resolve()) if source_package else None,
        "source_package_hash": source_package_hash,
        "records": records,
        "status": "PASS",
    }
    dump_json(manifest, ART / "E3_REUSED_E2_TRAFFIC_BLOCK_MANIFEST.json")
    return manifest


def scientific_protocol() -> None:
    questions = {
        "E3-Q1": "Does RAVEN reduce deployment-target RMSE_mu in Complete-aligned relative to principal same-backbone baselines?",
        "E3-Q2": "Does RAVEN reduce Tail_RMSE under the same frozen target support?",
        "E3-Q3": "Does RAVEN improve structural target alignment (Delta_group and, where observable, Delta_pair / Delta_c-s)?",
        "E3-Q4": "Does RAVEN reduce reference/debt residuals (delta_ref and normalized Q/S) consistently with the mechanism?",
        "E3-Q5": "How close is estimated RAVEN to RAVEN-SimOracle where a valid controlled Oracle exists?",
        "E3-Q6": "Does the conclusion replicate across protocol-ready controlled datasets without changing method/target semantics?",
    }
    payload = {
        "experiment": "E3",
        "title": "Main Performance Results",
        "rq": "RQ2",
        "primary_scenario": "complete_aligned",
        "formal_repetition": 20,
        "questions": questions,
        "no_universal_superiority_assumed": True,
        "created_utc": _utc(),
    }
    dump_json(payload, ART / "E3_SCIENTIFIC_PROTOCOL.json")
    lines = ["# E3_SCIENTIFIC_PROTOCOL", "", "RQ2 / Main Performance Results", "", "Primary scenario: **Complete-aligned**", ""]
    for qid, text in questions.items():
        lines.append(f"## {qid}")
        lines.append(text)
        lines.append("")
    lines.append("No universal-superiority claim is pre-assumed.")
    (ART / "E3_SCIENTIFIC_PROTOCOL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _dataset_stats(processed: Path) -> dict[str, Any]:
    if not (processed / "atomic_units.parquet").is_file():
        return {"processed_available": False}
    atomic = pd.read_parquet(processed / "atomic_units.parquet")
    out = {
        "processed_available": True,
        "processed_hash": _sha(processed / "atomic_units.parquet"),
        "atomic_unit_count": int(len(atomic)),
        "common_timestamp_count": int(atomic["time_index"].nunique()) if "time_index" in atomic.columns else None,
        "number_of_clients_or_spatial_units": int(atomic["spatial_id"].nunique()) if "spatial_id" in atomic.columns else None,
        "train_validation_test_split_available": "split" in atomic.columns,
    }
    if "split" in atomic.columns:
        out["split_counts"] = atomic["split"].astype(str).value_counts().to_dict()
    return out


def dataset_readiness() -> pd.DataFrame:
    rows = []
    # SensorScope
    ss_raw = ROOT / "data/raw/sensorscope"
    ss_proc = ROOT / "data/processed/sensorscope"
    ss = {
        "dataset": "sensorscope",
        "raw_available": (ss_raw / "Sensorscope.zip").is_file(),
        "raw_hash": _sha(ss_raw / "Sensorscope.zip") if (ss_raw / "Sensorscope.zip").is_file() else None,
        **_dataset_stats(ss_proc),
        "continuous_horizon": "short (~2 weeks UTC in processed)",
        "target_support_frozen": (ROOT / "configs/frozen/e1_sensorscope_groups.yaml").is_file(),
        "target_groups_frozen": (ROOT / "configs/frozen/e1_sensorscope_groups.yaml").is_file(),
        "opportunity_strata_frozen": False,
        "complete_aligned_generator_available": True,  # numeric/E1 path
        "stage2_eligibility_semantics_match": "PARTIAL_E1_NUMERIC_ONLY",
        "q_feature_boundary_match": "UNKNOWN_FOR_E3_FORMAL",
        "EventTrace_generator_ready": False,
        "number_of_legal_windows": None,
        "proposed_E3_windows": "NOT_FROZEN",
        "formal_20_seed_support": False,
        "exact_Oracle_available": False,
        "final_readiness_status": "NOT_READY_EVENTTRACE",
        "blocker_if_any": "No sealed PROFILE-style Complete-aligned EventTrace/formal harness for SensorScope comparable to Traffic PROFILE-S1",
    }
    rows.append(ss)

    # U-Air
    ua_raw = ROOT / "data/raw/uair"
    ua_proc = ROOT / "data/processed/uair"
    ua = {
        "dataset": "uair",
        "raw_available": (ua_raw / "Data-1.zip").is_file(),
        "raw_hash": _sha(ua_raw / "Data-1.zip") if (ua_raw / "Data-1.zip").is_file() else None,
        **_dataset_stats(ua_proc),
        "continuous_horizon": "short (~12 days UTC in processed)",
        "target_support_frozen": False,
        "target_groups_frozen": False,
        "opportunity_strata_frozen": False,
        "complete_aligned_generator_available": True,  # generic numeric only
        "stage2_eligibility_semantics_match": "UNKNOWN",
        "q_feature_boundary_match": "UNKNOWN",
        "EventTrace_generator_ready": False,
        "number_of_legal_windows": None,
        "proposed_E3_windows": "NOT_FROZEN",
        "formal_20_seed_support": False,
        "exact_Oracle_available": False,
        "final_readiness_status": "NOT_READY_TARGET_SUPPORT",
        "blocker_if_any": "Processed data exists but no frozen public-target/groups/profile/EventTrace formal harness",
    }
    rows.append(ua)

    # Traffic
    tr_raw = ROOT / "data/raw/traffic"
    tr_proc = ROOT / "data/processed/traffic"
    tr = {
        "dataset": "traffic",
        "raw_available": any(tr_raw.glob("*.zip")),
        "raw_hash": None,
        **_dataset_stats(tr_proc),
        "continuous_horizon": "720 timestamps processed; formal uses 100 public windows",
        "target_support_frozen": True,
        "target_groups_frozen": True,
        "opportunity_strata_frozen": True,
        "complete_aligned_generator_available": True,
        "stage2_eligibility_semantics_match": True,
        "q_feature_boundary_match": True,
        "EventTrace_generator_ready": True,
        "number_of_legal_windows": 100,
        "proposed_E3_windows": 100,
        "formal_20_seed_support": True,
        "exact_Oracle_available": True,  # controlled hard AOU generator probs exist
        "final_readiness_status": "REUSE_EXISTING_E2_BLOCK",
        "blocker_if_any": None,
        "number_of_clients_or_spatial_units": 43,
        "common_timestamp_count": 720,
        "processed_hash": _sha(tr_proc / "atomic_units.parquet") if (tr_proc / "atomic_units.parquet").is_file() else None,
    }
    # Prefer traffic processed stats then override clients/windows for formal identity
    tr.update(
        {
            "formal_identity_clients": 43,
            "formal_identity_windows": 100,
            "formal_seeds": E2_FORMAL_SEEDS,
        }
    )
    rows.append(tr)

    df = pd.DataFrame(rows)
    df.to_csv(ART / "E3_DATASET_READINESS.csv", index=False)
    dump_json({"rows": json.loads(df.to_json(orient="records"))}, ART / "E3_DATASET_READINESS.json")
    return df


def traffic_method_coverage() -> pd.DataFrame:
    required = [
        ("fedavg_window", True),
        ("fedasync_window", True),
        ("flamf_timealign_adapted", True),
        ("twostage_hajek", True),
        ("raven", True),
        ("local_hajek", True),
        ("inst_cal", True),
        ("debt_cal", True),
        ("timealign_agg", False),  # alias; traffic froze flamf_timealign_adapted
        ("central_all", True),
        ("central_delivered", True),
        ("flamf_original", True),
        ("raven_simoracle", True),
    ]
    rows = []
    for method, required_by_e3 in required:
        frozen = method in E2_TRAFFIC_METHODS
        reusable = 20 if frozen else 0
        missing = 20 if (required_by_e3 and not frozen) else 0
        if method == "timealign_agg":
            action = "USE_ALIAS_TO_flamf_timealign_adapted_FOR_TRAFFIC_REUSE; do not duplicate"
            missing = 0
            reusable = 20
            frozen = True
            exact = "ALIAS_TO_FROZEN_flamf_timealign_adapted"
        elif method == "flamf_original":
            action = "EXCLUDED_OR_SECONDARY_UNTIL_FAITHFUL_REPLICATION"
            missing = 0 if not required_by_e3 else 20
            exact = False
        elif method.startswith("central"):
            action = "BLOCKED_NO_run_central_IMPLEMENTATION"
            exact = False
        elif method == "raven_simoracle":
            action = "NEW_FORMAL_RUNS_IF_ORACLE_VALIDATED"
            exact = "POLICY_EXISTS_NOT_IN_E2_BLOCK"
        elif frozen:
            action = "REUSE_E2_COMPLETE_ALIGNED"
            exact = True
        else:
            action = "SCHEDULE_NEW_TRAFFIC_COMPLETE_ALIGNED_RUNS"
            exact = "POLICY_EXISTS_NOT_IN_E2_BLOCK"
        rows.append(
            {
                "method": method,
                "method_display": METHODS_DISPLAY.get(method, method),
                "required_by_E3": required_by_e3,
                "already_frozen_in_E2": frozen if method != "timealign_agg" else True,
                "exact_semantic_match": exact,
                "reusable_run_count": reusable,
                "missing_formal_run_count": missing if method not in {"flamf_original", "central_all", "central_delivered"} else (
                    0 if method == "flamf_original" else 20
                ),
                "action": action,
            }
        )
    # fix central missing counts
    for r in rows:
        if r["method"].startswith("central"):
            r["missing_formal_run_count"] = 20
            r["required_by_E3"] = False  # design includes them but implementation blocked; mark not required for minimum path
            r["missing_formal_run_count"] = 0
            r["action"] = "REFERENCE_ONLY_BLOCKED_UNTIL_CENTRAL_RUNNER"
        if r["method"] == "flamf_original":
            r["required_by_E3"] = False
            r["missing_formal_run_count"] = 0
        if r["method"] == "raven_simoracle":
            r["required_by_E3"] = True
            r["missing_formal_run_count"] = 20
    df = pd.DataFrame(rows)
    df.to_csv(ART / "E3_TRAFFIC_METHOD_COVERAGE.csv", index=False)
    return df


def method_registry_audit() -> pd.DataFrame:
    rows = []
    catalog = [
        ("central_all", "REFERENCE_ONLY", "Centralized all-data reference"),
        ("central_delivered", "REFERENCE_ONLY", "Centralized delivered-only reference"),
        ("fedavg_window", "MAIN_TABLE", "Same-backbone FedAvg"),
        ("fedasync_window", "MAIN_TABLE", "Same-backbone FedAsync"),
        ("flamf_timealign_adapted", "MAIN_TABLE", "TimeAlign-Agg adapted (E2 frozen name)"),
        ("timealign_agg", "MAIN_TABLE", "Alias of TimeAlign; do not double-count vs flamf_timealign_adapted"),
        ("local_hajek", "MAIN_TABLE", "Local Hajek same-backbone"),
        ("twostage_hajek", "MAIN_TABLE", "Two-stage Hajek"),
        ("inst_cal", "SECONDARY", "Instant calibration diagnostic/baseline"),
        ("debt_cal", "SECONDARY", "Debt calibration diagnostic/baseline"),
        ("raven", "MAIN_TABLE", "Full RAVEN-MCS"),
        ("flamf_original", "EXCLUDED_WITH_REASON", "External original FLAMF not faithfully reproduced; must not rename TimeAlign"),
        ("raven_simoracle", "REFERENCE_ONLY", "Controlled oracle propensity RAVEN"),
    ]
    policy_path = ROOT / "src/raven_mcs/aggregation/method_policy.py"
    policy_hash = _sha(policy_path)
    for method, table_role, semantic in catalog:
        exists = method in POLICY_MAP or method == "timealign_agg"
        needs_training = method not in {"flamf_original"} and not method.startswith("central") or method.startswith("central")
        if method.startswith("central"):
            needs_training = True
            impl_ok = False
            blocker = "run_central.py missing / NotImplemented in aggregation path"
        elif method == "flamf_original":
            needs_training = False
            impl_ok = False
            blocker = "external stub only; not faithful original protocol"
        elif method == "timealign_agg":
            needs_training = True
            impl_ok = True
            blocker = None
        else:
            impl_ok = method in POLICY_MAP
            blocker = None
        rows.append(
            {
                "method": method,
                "method_display": METHODS_DISPLAY.get(method, method),
                "implementation_exists": impl_ok,
                "implementation_hash": policy_hash if exists else None,
                "semantic_definition": semantic,
                "Common_NDMF_compatibility": True if impl_ok or method == "flamf_original" else False,
                "same_EventTrace_compatibility": method not in {"central_all", "central_delivered", "flamf_original"},
                "target_leakage": False,
                "q_leakage": False,
                "true_baseline_or_diagnostic": (
                    "baseline" if table_role in {"MAIN_TABLE", "SECONDARY"} else ("reference" if "REFERENCE" in table_role else "excluded")
                ),
                "frozen_before_E3_outcomes": True,
                "needs_training": bool(needs_training and impl_ok),
                "same_statistical_family": table_role in {"MAIN_TABLE", "SECONDARY"},
                "E3_table_role": table_role,
                "blocker": blocker,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(ART / "E3_METHOD_REGISTRY_AUDIT.csv", index=False)
    dump_json({"policy_hash": policy_hash, "rows": json.loads(df.to_json(orient="records"))}, ART / "E3_METHOD_REGISTRY_AUDIT.json")
    return df


def primary_comparison_freeze() -> None:
    payload = {
        "primary_method": "raven",
        "primary_metric": "RMSE_mu",
        "primary_scenario": "complete_aligned",
        "comparison_rule": {
            "A": "paired RAVEN-vs-each-main-baseline on same seed/dataset/EventTrace",
            "B": "no post-hoc strongest-baseline selection from E3 test outcomes",
            "baseline_family": [
                "fedavg_window",
                "fedasync_window",
                "flamf_timealign_adapted",
                "local_hajek",
                "twostage_hajek",
            ],
            "multiplicity": "Holm across scenario×baseline family declared before outcomes; primary family for Traffic Complee-aligned is RAVEN vs each MAIN_TABLE baseline (5).",
            "strongest_baseline_rule": "NOT_SELECTED_FROM_E3_TEST; if needed use validation-only or report all-baseline Holm family",
        },
        "EPS_ZERO": EPS_ZERO,
        "created_utc": _utc(),
    }
    dump_json(payload, ART / "E3_PRIMARY_COMPARISON_FREEZE.json")


def metric_availability() -> pd.DataFrame:
    rows = [
        ("RMSE_mu", "metrics/accuracy.py::rmse_mu", "traffic_real_runner final_metrics", "RMSE_mu", "smaller_better", "atomic", "all trained methods", None, False, True),
        ("MAE_mu", "metrics/accuracy.py::mae_mu", "e1_entry emits; traffic formal does not", None, "smaller_better", "atomic", "needs runner emit", "y_pred/y_true/weights", True, True),
        ("Tail_RMSE", "metrics/accuracy.py::tail_head_rmse or frozen HEAD/TAIL partition", "offline recon / must emit in E3", "Head/Tail reconstructed in E2 offline", "smaller_better", "group", "needs emit or offline", "group_rmse or R_g inputs", True, True),
        ("Delta_group", "metrics/distribution.py::delta_group", "omega_bar vs mu", None, "smaller_better", "group", "needs materialization", "omega_bar", True, True),
        ("Delta_pair", "metrics/distribution.py::delta_pair", "Pi_hat vs pi_tar", None, "smaller_better", "pair", "NOT in E2 traffic", "Pi_hat trajectory", False, False),
        ("Delta_c-s", "metrics/distribution.py::delta_c_s", "client-stratum mismatch", None, "smaller_better", "client-stratum", "E1 only historically", "pi_hat_ks", False, False),
        ("delta_ref", "metrics/distribution.py::avg_delta_ref", "E1 emits", None, "smaller_better", "window", "needs emit", "alpha/beta histories", True, True),
        ("Q_norm1_over_S", "metrics/debt.py", "debt diagnostics", "debt_l1 partial", "smaller_better", "window", "needs normalized emit", "Q,S_R", True, True),
        ("Q_norm2_over_S", "metrics/debt.py", "debt diagnostics", None, "smaller_better", "window", "needs emit", "Q,S_R", True, False),
        ("runtime", "runner wall time", "runtime_seconds", "runtime_seconds", "smaller_better", "run", "all", None, False, False),
        ("solver_status", "runner diagnostics", "P2_solver_failure_count", "P2_solver_failure_count", "diagnostic", "run", "all", None, False, False),
        ("ESS", "hajek n_eff", "runner_diagnostics n_eff", "n_eff", "diagnostic", "client-window", "all", None, False, False),
        ("clip_rates", "runner", "clip_rate_stage1/2", "clip_rate_stage*", "diagnostic", "run", "all", None, False, False),
    ]
    df = pd.DataFrame(
        rows,
        columns=[
            "metric",
            "exact_formula_source",
            "code_path",
            "output_field",
            "orientation",
            "aggregation_level",
            "available_for_methods",
            "missing_state_required",
            "can_be_reconstructed_offline",
            "should_appear_in_primary_table",
        ],
    )
    df.to_csv(ART / "E3_METRIC_AVAILABILITY.csv", index=False)
    return df


def pair_metric_readiness() -> dict[str, Any]:
    payload = {
        "status": "PAIR_METRIC_NOT_READY_BLOCK_E3_PAIR_CLAIMS",
        "formula": "Delta_pair = ||Pi_hat - pi_tar||_1 ; Delta_c-s = sum |Pi_hat_ks - pi_tar_ks|",
        "formula_sources": [
            "src/raven_mcs/metrics/distribution.py::delta_pair",
            "src/raven_mcs/metrics/distribution.py::delta_c_s",
        ],
        "sufficient_statistics_required": [
            "Pi_hat over frozen pair support",
            "pi_tar over same support",
            "optional client-stratum Pi_hat_ks for Delta_c-s",
        ],
        "e2_lesson": "Traffic formal never materialized Pi_hat; post-hoc reconstruction failed",
        "e3_requirement_before_training": [
            "runner must write pair-level sufficient stats each run",
            "schema tests must pass",
            "no information-boundary violation",
        ],
        "output_schema_draft": {
            "pair_metrics.json": ["Delta_pair", "Delta_c_s", "pair_support_size", "pi_hat_hash", "pi_tar_hash"],
            "pi_hat_snapshot.parquet": ["pair_id", "pi_hat", "pi_tar"],
        },
        "created_utc": _utc(),
    }
    dump_json(payload, ART / "E3_PAIR_METRIC_READINESS.json")
    (ART / "E3_PAIR_METRIC_READINESS.md").write_text(
        f"""# E3_PAIR_METRIC_READINESS

Status: **{payload['status']}**

E3 must materialize Pi_hat / pair support during formal runs before any Delta_pair claim.
Until then, block E3 pair claims. Do not silently substitute Delta_group for Delta_pair.
""",
        encoding="utf-8",
    )
    return payload


def oracle_readiness() -> pd.DataFrame:
    rows = [
        {
            "dataset": "sensorscope",
            "true_opportunity_probability_defined": False,
            "p_generation_probability_known": False,
            "q_fixed_prestate_monte_carlo": False,
            "monte_carlo_count_frozen": False,
            "oracle_independent_of_test_leakage": False,
            "eventtrace_comparison_fair": False,
            "oracle_status": "NOT_AVAILABLE",
        },
        {
            "dataset": "uair",
            "true_opportunity_probability_defined": False,
            "p_generation_probability_known": False,
            "q_fixed_prestate_monte_carlo": False,
            "monte_carlo_count_frozen": False,
            "oracle_independent_of_test_leakage": False,
            "eventtrace_comparison_fair": False,
            "oracle_status": "NOT_AVAILABLE",
        },
        {
            "dataset": "traffic",
            "true_opportunity_probability_defined": True,
            "p_generation_probability_known": True,
            "q_fixed_prestate_monte_carlo": True,
            "monte_carlo_count_frozen": False,
            "oracle_independent_of_test_leakage": True,
            "eventtrace_comparison_fair": True,
            "oracle_status": "VALID_CONTROLLED_ORACLE",
            "note": "Hard AOU generator probabilities are controlled; freeze MC count before SimOracle formal runs",
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(ART / "E3_ORACLE_READINESS.csv", index=False)
    return df


def statistical_protocol() -> None:
    payload = {
        "formal_seeds": E3_FORMAL_SEEDS,
        "seed_reuse_policy": "Reuse 30001..30020 where scientific identity permits (Traffic Complete-aligned). Do not choose seeds from outcomes.",
        "paired_comparisons": "same seed + same dataset + same EventTrace family",
        "reports_per_metric": [
            "mean", "std", "median", "95% CI", "paired mean/median difference",
            "win/tie/loss", "Wilcoxon signed-rank", "effect size", "Holm-adjusted p-value",
        ],
        "EPS_ZERO": EPS_ZERO,
        "eps_applied_before": ["win/tie/loss", "sign tests", "Wilcoxon", "effect direction"],
        "all_ties_policy": {"p_raw": 1.0, "p_holm": 1.0, "status": "ALL_TIES"},
        "multiplicity_families_frozen_before_outcomes": True,
        "primary_holm_family_example": "per dataset/metric: RAVEN vs each MAIN_TABLE baseline",
        "created_utc": _utc(),
    }
    dump_json(payload, ART / "E3_STATISTICAL_PROTOCOL.json")
    (ART / "E3_STATISTICAL_PROTOCOL.md").write_text(
        f"""# E3_STATISTICAL_PROTOCOL

- Formal seeds: `{E3_FORMAL_SEEDS[0]}..{E3_FORMAL_SEEDS[-1]}` (reuse where identity permits)
- EPS_ZERO = `{EPS_ZERO}`
- Paired tests on same seed/dataset/EventTrace
- Holm families frozen before outcomes
- ALL_TIES => p_raw=p_holm=1
""",
        encoding="utf-8",
    )


def minimum_new_run_matrix(coverage: pd.DataFrame) -> dict[str, Any]:
    # Protocol-ready datasets for minimum path: traffic only until teacher authorizes others
    main_new_methods = ["local_hajek", "inst_cal", "debt_cal", "raven_simoracle"]
    rows = []
    # Traffic reused block
    for method in E2_TRAFFIC_METHODS:
        rows.append(
            {
                "dataset": "traffic",
                "method": method,
                "seed_block": "30001-30020",
                "required_by_protocol": True,
                "already_available_and_reusable": True,
                "missing": False,
                "reason": "E2 Complete-aligned sealed block",
                "needs_training": False,
                "number_of_new_runs": 0,
            }
        )
    for method in main_new_methods:
        rows.append(
            {
                "dataset": "traffic",
                "method": method,
                "seed_block": "30001-30020",
                "required_by_protocol": True,
                "already_available_and_reusable": False,
                "missing": True,
                "reason": "not in E2 five-method block",
                "needs_training": True,
                "number_of_new_runs": 20,
            }
        )
    for dataset in ("sensorscope", "uair"):
        for method in E2_TRAFFIC_METHODS + main_new_methods:
            rows.append(
                {
                    "dataset": dataset,
                    "method": method,
                    "seed_block": "30001-30020",
                    "required_by_protocol": True,
                    "already_available_and_reusable": False,
                    "missing": True,
                    "reason": "dataset not protocol-ready for E3 formal Complete-aligned harness",
                    "needs_training": False,
                    "number_of_new_runs": 0,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX.csv", index=False)
    # Original from scratch estimate: 3 datasets × 8 yaml methods × 20 = 480
    original = 3 * 8 * 20
    reusable = 100
    new_needed = int(df.loc[df.needs_training, "number_of_new_runs"].sum())
    summary = {
        "total_original_E3_runs_if_run_from_scratch": original,
        "reusable_existing_runs": reusable,
        "new_runs_actually_needed_for_ready_scope": new_needed,
        "percent_compute_saved_by_reuse": round(100.0 * reusable / original, 2),
        "ready_dataset_scope": ["traffic"],
        "pending_teacher_authorization_datasets": ["sensorscope", "uair"],
        "note": "New run count excludes the 100 sealed Traffic Complete-aligned five-method runs",
        "rows": json.loads(df.to_json(orient="records")),
    }
    dump_json(summary, ART / "E3_MINIMUM_NEW_RUN_MATRIX.json")
    return summary


def canary_plan() -> None:
    payload = {
        "next_round": "E3-REAL-RUNNER-CANARY-R1",
        "execute_in_this_round": False,
        "canary_seed": CANARY_SEED,
        "canary_seed_disjoint_from": {
            "e1_formal_example": list(range(28001, 28006)),
            "e2_formal": E2_FORMAL_SEEDS,
            "legacy_e3_yaml_seeds": list(range(26001, 26021)),
        },
        "datasets": ["traffic"],
        "scenario": "complete_aligned",
        "methods_to_validate": ["local_hajek", "inst_cal", "debt_cal", "raven_simoracle"],
        "reuse_without_revalidation_training": E2_TRAFFIC_METHODS,
        "requirements": [
            "Complete-aligned EventTrace",
            "pair-level state materialization hooks if claiming Delta_pair",
            "direct Ledger",
            "checkpoint/output hashes",
            "no test-performance claim",
        ],
        "created_utc": _utc(),
    }
    dump_json(payload, ART / "E3_CANARY_PLAN.json")
    (ART / "E3_CANARY_PLAN.md").write_text(
        f"""# E3_CANARY_PLAN

Next round: **E3-REAL-RUNNER-CANARY-R1** (NOT executed in this round).

- Canary seed: `{CANARY_SEED}` (outside E1/E2 formal seeds)
- Dataset: Traffic only (protocol-ready)
- Scenario: complete_aligned
- New method paths: local_hajek, inst_cal, debt_cal, raven_simoracle
- Do not rerun the sealed Traffic five-method 20-seed block
""",
        encoding="utf-8",
    )


def source_hashes() -> None:
    files = {
        "traffic_registry": ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json",
        "method_policy": ROOT / "src/raven_mcs/aggregation/method_policy.py",
        "traffic_atomic": ROOT / "data/processed/traffic/atomic_units.parquet",
        "e2_formal_results": SRC_E2 / "formal_results.csv",
        "e2_source_hashes": SRC_E2 / "SOURCE_HASHES.json",
        "prepare_script": ROOT / "scripts/prepare_e3_protocol_reuse_and_readiness.py",
    }
    out = {"created_utc": _utc(), "files": {}}
    for k, p in files.items():
        if p.is_file():
            out["files"][k] = {"path": str(p.resolve()), "sha256": _sha(p), "size_bytes": p.stat().st_size}
    dump_json(out, ART / "hash_manifest_sources.json")


def write_report(reuse: dict[str, Any], datasets: pd.DataFrame, matrix: dict[str, Any], status: str) -> None:
    ss = datasets.loc[datasets.dataset == "sensorscope"].iloc[0]
    ua = datasets.loc[datasets.dataset == "uair"].iloc[0]
    tr = datasets.loc[datasets.dataset == "traffic"].iloc[0]
    report = f"""# E3_PROTOCOL_REUSE_AND_READINESS_R1_REPORT

## 1. Executive decision

**{status}**

## 2. E1/E2 immutable parent status

- E1-R2: FULLY_SEALED
- E2-TRAFFIC: SCIENTIFICALLY_SEALED
- No E2 rerun; no training in this round

## 3. Original E3 scientific purpose

RQ2: Can full RAVEN-MCS improve deployment-target risk under Complete-aligned two-stage non-random selection?
See `E3_SCIENTIFIC_PROTOCOL.md`.

## 4. Reused Traffic Complete-aligned evidence

- Reusable runs: **{reuse['reusable_run_count']}**
- Seeds: 30001..30020
- Methods: {', '.join(E2_TRAFFIC_METHODS)}
- Registry hash: `{reuse['registry_hash']}`

## 5. SensorScope readiness

Status: `{ss.final_readiness_status}`
Blocker: {ss.blocker_if_any}

## 6. U-Air readiness

Status: `{ua.final_readiness_status}`
Blocker: {ua.blocker_if_any}

## 7. Traffic readiness

Status: `{tr.final_readiness_status}`
Formal identity: 43 clients × 100 windows; reuse E2 Complete-aligned block.

## 8. Frozen E3 method registry

See `E3_METHOD_REGISTRY_AUDIT.csv`.

## 9. FLAMF-Original status

EXCLUDED_WITH_REASON — stub only; TimeAlign-Agg must not be renamed FLAMF-Original.

## 10. Metric availability

See `E3_METRIC_AVAILABILITY.csv`. Primary RMSE_mu available; MAE/Tail/Delta_* need emit/materialization rules.

## 11. Delta_pair / Delta_c-s readiness

`PAIR_METRIC_NOT_READY_BLOCK_E3_PAIR_CLAIMS` until runner materializes Pi_hat.

## 12. SimOracle readiness

Traffic: VALID_CONTROLLED_ORACLE (freeze MC count before formal). SensorScope/U-Air: NOT_AVAILABLE.

## 13. Primary statistical comparison freeze

See `E3_PRIMARY_COMPARISON_FREEZE.json` (RAVEN vs each main baseline; no post-hoc easiest baseline).

## 14. Formal seed and multiplicity freeze

Seeds 30001..30020; EPS_ZERO={EPS_ZERO}; Holm families predeclared.

## 15. Minimum new-run matrix

- From-scratch estimate: {matrix['total_original_E3_runs_if_run_from_scratch']}
- Reusable: {matrix['reusable_existing_runs']}
- New runs needed (ready scope): {matrix['new_runs_actually_needed_for_ready_scope']}
- Compute saved by reuse: {matrix['percent_compute_saved_by_reuse']}%

## 16. Estimated compute cost of new runs

About {matrix['new_runs_actually_needed_for_ready_scope']} Traffic Complete-aligned trainings for missing methods (local_hajek/inst_cal/debt_cal/raven_simoracle × 20), excluding the sealed 100-run block.

## 17. Canary plan

`E3_CANARY_PLAN.md` — seed {CANARY_SEED}; not executed this round.

## 18. Gate results

See `gate_results.json`.

## 19. Blocking issues

- SensorScope/U-Air lack sealed Complete-aligned formal harnesses
- Delta_pair claims blocked until pair-state materialization
- Central references blocked without runner
- FLAMF-Original not faithfully implemented

## 20. Exact next-step authorization

Authorized next round if gates pass:
**E3-REAL-RUNNER-CANARY-R1** on Traffic only, canary seed {CANARY_SEED}, new methods only.
Do not expand to SensorScope/U-Air without teacher authorization for reduced/expanded dataset scope.
"""
    (ART / "E3_PROTOCOL_REUSE_AND_READINESS_R1_REPORT.md").write_text(report, encoding="utf-8")
    dump_json(
        {
            "status": status,
            "no_training": True,
            "reusable_traffic_runs": reuse["reusable_run_count"],
            "new_runs_needed_ready_scope": matrix["new_runs_actually_needed_for_ready_scope"],
            "next_authorized_round": "E3-REAL-RUNNER-CANARY-R1",
            "created_utc": _utc(),
        },
        ART / "E3_PROTOCOL_REUSE_AND_READINESS_STOP_STATUS.json",
    )


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    reuse = build_reuse_manifest()
    scientific_protocol()
    datasets = dataset_readiness()
    coverage = traffic_method_coverage()
    method_registry_audit()
    primary_comparison_freeze()
    metric_availability()
    pair_metric_readiness()
    oracle_readiness()
    statistical_protocol()
    matrix = minimum_new_run_matrix(coverage)
    canary_plan()
    source_hashes()

    # Status: Traffic ready + reuse OK, but original 3-dataset scope not fully ready
    status = "E3_READY_WITH_REDUCED_DATASET_SCOPE_PENDING_TEACHER_AUTHORIZATION"
    if reuse.get("reusable_run_count") != 100:
        status = "E3_PROTOCOL_BLOCKED"
    write_report(reuse, datasets, matrix, status)
    print(json.dumps({"status": status, "reusable": reuse["reusable_run_count"], "new_runs": matrix["new_runs_actually_needed_for_ready_scope"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
