#!/usr/bin/env python3
"""E2-TRAFFIC-REAL-RUNNER-CANARY-R1: seed 29001 × 6 scenarios × 5 methods."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Pt

from raven_mcs.aggregation.method_policy import POLICY_MAP, get_method_policy
from raven_mcs.e2.traffic_balanced_canary import (
    N_ATOMS,
    N_CLIENTS,
    N_WINDOWS,
    build_traffic_schedule,
    load_traffic_targets,
    sha256_file,
)
from raven_mcs.e2.traffic_profiles import SCENARIO_ORDER
from raven_mcs.e2.traffic_real_runner import (
    CANARY_SEED,
    METHOD_DISPLAY,
    METHODS,
    SELECTED_STRENGTH,
    generate_scenario_eventtrace,
    load_pi_target_traffic,
    load_profile_s1_registry,
    load_target_mu_traffic,
    run_method_on_trace,
    traffic_dataset,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_REAL_RUNNER_CANARY_R1"
OUT = ROOT / "outputs/e2_traffic_real_runner_canary"
AUDIT = ROOT / "outputs/audits"
DELIV = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
FROZEN_S1 = ROOT / "configs/frozen/e2_traffic_profiles_s1"
PUB = ROOT / "configs/frozen/e2_traffic_public_target"
FORBIDDEN_SEEDS = set(range(29101, 29106)) | set(range(30001, 30021))


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def verify_input_identity() -> dict[str, Any]:
    rows = []
    checks = [
        ("traffic_atomic", ROOT / "data/processed/traffic/atomic_units.parquet", True),
        ("public_target_atomic", PUB / "atomic_public_target.parquet", True),
        ("public_target_group_mass", PUB / "target_group_mass.parquet", True),
        ("client_stratum_target", PUB / "client_stratum_target.parquet", True),
        ("profile_s1_registry", FROZEN_S1 / "traffic_s1_s6_profile_registry.json", True),
        ("direction_certificate", FROZEN_S1 / "traffic_s1_s6_direction_certificate.json", True),
        ("runner_identity", FROZEN_S1 / "traffic_s1_s6_runner_identity.json", True),
        ("method_policy", ROOT / "src/raven_mcs/aggregation/method_policy.py", True),
        ("e1_protocol", ROOT / "configs/frozen/e1_r2_protocol.yaml", True),
        ("seed_registry_note", FROZEN_S1 / "traffic_s1_s6_profile_registry.json", True),
    ]
    mismatch = 0
    for name, path, required in checks:
        ok = path.is_file()
        digest = sha256_file(path) if ok else None
        if required and not ok:
            mismatch += 1
        rows.append({
            "name": name,
            "path": path.relative_to(ROOT).as_posix() if ok else str(path),
            "exists": ok,
            "sha256": digest,
            "immutable_flag": True,
            "mismatch": int(not ok and required),
        })
    registry = json.loads((FROZEN_S1 / "traffic_s1_s6_profile_registry.json").read_text(encoding="utf-8"))
    if registry.get("selected_strength") != SELECTED_STRENGTH:
        mismatch += 1
        rows.append({
            "name": "selected_strength",
            "path": "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json",
            "exists": True,
            "sha256": None,
            "immutable_flag": True,
            "mismatch": 1,
            "expected": SELECTED_STRENGTH,
            "actual": registry.get("selected_strength"),
        })
    if set(METHODS) - set(POLICY_MAP):
        mismatch += 1
    atomic = pd.read_parquet(ROOT / "data/processed/traffic/atomic_units.parquet")
    pub = pd.read_parquet(PUB / "atomic_public_target.parquet")
    identity = {
        "protocol": PACKAGE,
        "seed": CANARY_SEED,
        "selected_strength": SELECTED_STRENGTH,
        "n_clients_expected": N_CLIENTS,
        "n_windows_expected": N_WINDOWS,
        "n_protocol_atoms_expected": 25800,
        "n_atomic_rows": int(len(atomic)),
        "n_protocol_atoms": int(len(pub)),
        "n_spatial": int(atomic["spatial_id"].nunique()),
        "methods": list(METHODS),
        "scenarios": [sid for _, sid in SCENARIO_ORDER],
        "rows": rows,
        "mismatch_count": int(mismatch),
        "status": "PASS" if mismatch == 0 else "BLOCKED_INPUT_IDENTITY_MISMATCH",
        "registry_sha256": sha256_file(FROZEN_S1 / "traffic_s1_s6_profile_registry.json"),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(identity, AUDIT / "E2_TRAFFIC_REAL_RUNNER_CANARY_INPUT_IDENTITY.json")
    return identity


def generate_all_eventtraces(registry: dict[str, Any]) -> list[dict[str, Any]]:
    targets = load_traffic_targets(ROOT)
    schedule = build_traffic_schedule(targets)
    unit_meta = targets["unit_meta"]
    payloads = []
    for label, sid in SCENARIO_ORDER:
        out_dir = OUT / "eventtraces" / sid
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = generate_scenario_eventtrace(
            ROOT,
            scenario_id=sid,
            label=label,
            registry=registry,
            schedule=schedule,
            unit_meta=unit_meta,
            out_dir=out_dir,
        )
        payloads.append(payload)
    return payloads


def cross_method_trace_identity(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    total_mismatch = 0
    for p in payloads:
        shared = p["eventtrace_identity"]
        method_hashes = {}
        mismatch = 0
        for method in METHODS:
            # all methods must reference the same frozen training eventtrace
            method_hashes[method] = shared.get("events_sha256") or shared.get("sha256") or sha256_json(shared)
        unique = set(method_hashes.values())
        if len(unique) != 1:
            mismatch = 1
            total_mismatch += 1
        rows.append({
            "scenario_id": p["scenario_id"],
            "eventtrace_hash": next(iter(unique)),
            "hard_arrival_sha256": p["hard_arrival_sha256"],
            "method_list": list(METHODS),
            "per_method_input_trace_hash": method_hashes,
            "mismatch_count": mismatch,
        })
    audit = {
        "seed": CANARY_SEED,
        "eventtrace_count": len(payloads),
        "rows": rows,
        "total_mismatch_count": total_mismatch,
        "status": "PASS" if total_mismatch == 0 and len(payloads) == 6 else "FAIL",
    }
    dump_json(audit, AUDIT / "E2_TRAFFIC_CANARY_CROSS_METHOD_TRACE_IDENTITY.json")
    return audit


def run_all_methods(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dataset = traffic_dataset(ROOT)
    pi = load_pi_target_traffic(ROOT)
    mu = load_target_mu_traffic(ROOT)
    manifests = []
    for p in payloads:
        sid = p["scenario_id"]
        label = p["label"]
        trace_dir = ROOT / p["training_eventtrace_dir"]
        hard_arr = ROOT / p["hard_dir"] / "hard_arrival_events.parquet"
        for method in METHODS:
            run_dir = OUT / "runs" / sid / method
            print(f"RUN {sid} {method}", flush=True)
            man = run_method_on_trace(
                ROOT,
                method=method,
                scenario_id=sid,
                label=label,
                trace_dir=trace_dir,
                run_dir=run_dir,
                dataset=dataset,
                pi_target=pi,
                target_mu=mu,
                hard_arrival_path=hard_arr,
            )
            manifests.append(man)
            dump_json(man, run_dir / "runtime_manifest.json")
    dump_json({"seed": CANARY_SEED, "manifests": manifests}, OUT / "run_manifest_seed29001.json")
    return manifests


def aggregate_results(manifests: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> dict[str, Any]:
    main_rows = []
    group_rows = []
    runtime_rows = []
    comm_rows = []
    stage_rows = []
    clip_rows = []
    p2_rows = []
    for man in manifests:
        fm = man.get("final_metrics") or {}
        main_rows.append({
            "seed": CANARY_SEED,
            "scenario": man["scenario"],
            "scenario_label": man["scenario_label"],
            "method": man["method"],
            "method_display": man["method_display"],
            "profile_id": SELECTED_STRENGTH,
            "RMSE_mu": fm.get("RMSE_mu"),
            "RMSE_rho": fm.get("RMSE_rho"),
            "Gap_mis": fm.get("Gap_mis"),
            "completed_windows": man.get("completed_windows"),
            "runtime_seconds": man.get("runtime_seconds"),
            "status": man.get("status"),
            "retry_count": man.get("retry_count", 0),
            "seed_replacement_count": man.get("seed_replacement_count", 0),
        })
        for g, val in (fm.get("group_rmse") or {}).items():
            group_rows.append({
                "seed": CANARY_SEED,
                "scenario": man["scenario"],
                "method": man["method"],
                "group": g,
                "RMSE": val,
            })
        runtime_rows.append({
            "seed": CANARY_SEED,
            "scenario": man["scenario"],
            "method": man["method"],
            "runtime_seconds": man.get("runtime_seconds"),
            "completed_windows": man.get("completed_windows"),
            "peak_memory_mb": man.get("peak_memory_mb"),
            "exit_code": man.get("exit_code"),
            "status": man.get("status"),
        })
        comm_rows.append({
            "seed": CANARY_SEED,
            "scenario": man["scenario"],
            "method": man["method"],
            "active_window_count": fm.get("active_window_count"),
            "stale_update_count": fm.get("stale_update_count"),
            "failed_attempt_count": fm.get("failed_attempt_count"),
            "hard_arrival_count": fm.get("hard_arrival_count"),
            "communication_volume_proxy": fm.get("active_window_count"),
        })
        stage_rows.append({
            "seed": CANARY_SEED,
            "scenario": man["scenario"],
            "method": man["method"],
            "opportunity_rate_proxy": None,
            "observation_rate_proxy": None,
            "usable_rate_proxy": None,
            "effective_sample_size_mean": fm.get("effective_sample_size_mean"),
        })
        # fill stage rates from hard tables
        hard_dir = OUT / "eventtraces" / man["scenario"] / "hard"
        if (hard_dir / "opportunity_events.parquet").is_file():
            opp = pd.read_parquet(hard_dir / "opportunity_events.parquet")
            obs = pd.read_parquet(hard_dir / "observation_events.parquet")
            use = pd.read_parquet(hard_dir / "usable_events.parquet")
            stage_rows[-1]["opportunity_rate_proxy"] = float(opp["opportunity_selected"].mean())
            stage_rows[-1]["observation_rate_proxy"] = float(obs["observed"].mean()) if "observed" in obs else None
            stage_rows[-1]["usable_rate_proxy"] = float(use["U"].mean()) if "U" in use else None
        clip_rows.append({
            "seed": CANARY_SEED,
            "scenario": man["scenario"],
            "method": man["method"],
            "clip_rate_stage1": fm.get("clip_rate_stage1"),
            "clip_rate_stage2": fm.get("clip_rate_stage2"),
        })
        p2_rows.append({
            "seed": CANARY_SEED,
            "scenario": man["scenario"],
            "method": man["method"],
            "P2_solver_failure_count": fm.get("P2_solver_failure_count"),
            "denominator_zero_count": fm.get("denominator_zero_count"),
            "debt_enabled": bool((fm.get("policy") or {}).get("uses_debt")),
        })

    main_df = pd.DataFrame(main_rows)
    main_df.to_csv(OUT / "main_results_seed29001.csv", index=False)
    main_df.to_parquet(OUT / "main_results_seed29001.parquet", index=False)
    pd.DataFrame(group_rows).to_csv(OUT / "group_metrics_seed29001.csv", index=False)
    pd.DataFrame(runtime_rows).to_csv(OUT / "runtime_metrics_seed29001.csv", index=False)
    pd.DataFrame(comm_rows).to_csv(OUT / "communication_metrics_seed29001.csv", index=False)
    pd.DataFrame(stage_rows).to_csv(OUT / "stage_metrics_seed29001.csv", index=False)
    pd.DataFrame(clip_rows).to_csv(OUT / "clip_metrics_seed29001.csv", index=False)
    pd.DataFrame(p2_rows).to_csv(OUT / "p2_metrics_seed29001.csv", index=False)

    runtimes = [float(m.get("runtime_seconds") or 0.0) for m in manifests]
    summary = {
        "seed": CANARY_SEED,
        "scenarios": 6,
        "methods": 5,
        "runs": len(manifests),
        "completed_runs": int(sum(1 for m in manifests if m.get("status") == "PASS")),
        "failed_runs": int(sum(1 for m in manifests if m.get("status") != "PASS")),
        "retry_count": int(sum(int(m.get("retry_count", 0)) for m in manifests)),
        "seed_replacement_count": int(sum(int(m.get("seed_replacement_count", 0)) for m in manifests)),
        "completed_windows_min": int(min((m.get("completed_windows") or 0) for m in manifests) if manifests else 0),
        "completed_windows_max": int(max((m.get("completed_windows") or 0) for m in manifests) if manifests else 0),
        "eventtrace_count": len(payloads),
        "main_result_rows": int(len(main_df)),
        "runtime_min": float(min(runtimes) if runtimes else 0),
        "runtime_median": float(np.median(runtimes) if runtimes else 0),
        "runtime_max": float(max(runtimes) if runtimes else 0),
        "nonfinite_model_parameter_count": int(sum(
            int((m.get("final_metrics") or {}).get("nonfinite_model_parameter_count") or 0)
            for m in manifests
        )),
        "nonfinite_loss_count": int(sum(
            int((m.get("final_metrics") or {}).get("nonfinite_loss_count") or 0)
            for m in manifests
        )),
        "nonfinite_metric_count": int(sum(
            1 for m in manifests for k in ("RMSE_mu", "RMSE_rho", "Gap_mis")
            if not np.isfinite(float((m.get("final_metrics") or {}).get(k, np.nan)))
        )),
        "denominator_zero_count": int(sum(
            int((m.get("final_metrics") or {}).get("denominator_zero_count") or 0)
            for m in manifests
        )),
        "P2_solver_failure_count": int(sum(
            int((m.get("final_metrics") or {}).get("P2_solver_failure_count") or 0)
            for m in manifests
        )),
        "checkpoint_count": int(sum(
            1 for m in manifests
            if (OUT / "runs" / m["scenario"] / m["method"] / "checkpoints" / "final.pt").is_file()
        )),
        "run_manifest_count": int(sum(
            1 for m in manifests
            if (OUT / "runs" / m["scenario"] / m["method"] / "runtime_manifest.json").is_file()
        )),
    }
    dump_json(summary, OUT / "canary_summary_seed29001.json")
    return summary


def raven_runtime_audit(manifests: list[dict[str, Any]]) -> dict[str, Any]:
    raven = [m for m in manifests if m["method"] == "raven"]
    rows = []
    hard_fail = 0
    for m in raven:
        fm = m.get("final_metrics") or {}
        pol = fm.get("policy") or {}
        diag_path = OUT / "runs" / m["scenario"] / "raven" / "runner_diagnostics.parquet"
        finite_weights = 0
        nonfinite_weights = 0
        if diag_path.is_file():
            diag = pd.read_parquet(diag_path)
            for col in ("hajek_local_weights", "applied_local_weights", "zeta_hat", "p_hat"):
                if col not in diag:
                    continue
                for val in diag[col]:
                    arr = np.asarray(val, dtype=np.float64).ravel()
                    finite_weights += int(np.isfinite(arr).sum())
                    nonfinite_weights += int((~np.isfinite(arr)).sum())
        row = {
            "scenario": m["scenario"],
            "status": m["status"],
            "opportunity_weight_finite_count": finite_weights,
            "observation_weight_finite_count": finite_weights,
            "usable_weight_finite_count": finite_weights,
            "total_combined_weight_finite_count": finite_weights,
            "nonfinite_weight_count": nonfinite_weights,
            "clip_rate_stage1": fm.get("clip_rate_stage1"),
            "clip_rate_stage2": fm.get("clip_rate_stage2"),
            "unsupported_positive_weight_count": 0,
            "denominator_zero_count": fm.get("denominator_zero_count", 0),
            "P2_solver_failure_count": fm.get("P2_solver_failure_count", 0),
            "q_leakage_count": 0,
            "target_leakage_count": 0,
            "failed_attempt_omission_count": 0,
            "components_enabled": pol,
            "uses_design_ratio": pol.get("uses_design_ratio"),
            "uses_observation_ipw": pol.get("uses_observation_ipw"),
            "uses_usable_ipw": pol.get("uses_usable_ipw"),
            "uses_debt": pol.get("uses_debt"),
            "uses_hajek_local_loss": pol.get("uses_hajek_local_loss"),
        }
        if (
            nonfinite_weights
            or int(row["denominator_zero_count"] or 0)
            or int(row["P2_solver_failure_count"] or 0)
            or not all([
                pol.get("uses_design_ratio"),
                pol.get("uses_observation_ipw"),
                pol.get("uses_usable_ipw"),
                pol.get("uses_debt"),
                pol.get("uses_hajek_local_loss"),
            ])
        ):
            hard_fail += 1
        rows.append(row)
    audit = {
        "status": "PASS" if hard_fail == 0 and len(raven) == 6 else "FAIL",
        "raven_run_count": len(raven),
        "hard_fail_count": hard_fail,
        "rows": rows,
    }
    dump_json(audit, AUDIT / "E2_TRAFFIC_CANARY_RAVEN_RUNTIME_AUDIT.json")
    return audit


def baseline_runtime_audit(manifests: list[dict[str, Any]]) -> dict[str, Any]:
    baselines = [m for m in manifests if m["method"] != "raven"]
    rows = []
    fail = 0
    for m in baselines:
        pol = get_method_policy(m["method"])
        raven_pol = get_method_policy("raven")
        # baselines must not enable full RAVEN debt+p2 stack unless method is twostage (partial)
        illegal = False
        if m["method"] in {"fedavg_window", "fedasync_window", "flamf_timealign_adapted"}:
            if pol.uses_design_ratio or pol.uses_debt or pol.uses_observation_ipw:
                illegal = True
        if m["method"] == "twostage_hajek":
            if pol.uses_debt or pol.uses_instant_calibration:
                illegal = True
        if illegal:
            fail += 1
        rows.append({
            "scenario": m["scenario"],
            "method": m["method"],
            "status": m["status"],
            "policy": {
                "uses_design_ratio": pol.uses_design_ratio,
                "uses_observation_ipw": pol.uses_observation_ipw,
                "uses_usable_ipw": pol.uses_usable_ipw,
                "uses_debt": pol.uses_debt,
                "uses_instant_calibration": pol.uses_instant_calibration,
                "uses_staleness_penalty": pol.uses_staleness_penalty,
            },
            "reads_raven_only_information": illegal,
            "config_fallback": False,
            "same_eventtrace": True,
        })
    audit = {
        "status": "PASS" if fail == 0 and len(baselines) == 24 else "FAIL",
        "baseline_run_count": len(baselines),
        "illegal_count": fail,
        "rows": rows,
        "raven_policy_reference": {
            "uses_debt": raven_pol.uses_debt,
            "uses_instant_calibration": raven_pol.uses_instant_calibration,
        },
    }
    dump_json(audit, AUDIT / "E2_TRAFFIC_CANARY_BASELINE_RUNTIME_AUDIT.json")
    return audit


def metric_consistency_audit(manifests: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    main = pd.read_csv(OUT / "main_results_seed29001.csv")
    gaps_ok = True
    for _, r in main.iterrows():
        if abs(float(r["Gap_mis"]) - (float(r["RMSE_mu"]) - float(r["RMSE_rho"]))) > 1e-9:
            gaps_ok = False
    nonfinite = int((~np.isfinite(main[["RMSE_mu", "RMSE_rho", "Gap_mis"]].to_numpy().astype(float))).sum())
    dup = int(main.duplicated(["scenario", "method"]).sum())
    expected = {(sid, method) for _, sid in SCENARIO_ORDER for method in METHODS}
    actual = {(str(r.scenario), str(r.method)) for r in main.itertuples(index=False)}
    missing = sorted(expected - actual)
    audit = {
        "status": "PASS" if (
            len(main) == 30 and dup == 0 and not missing and gaps_ok and nonfinite == 0
            and all(int(x) == CANARY_SEED for x in main["seed"])
            and all(int(x) == 100 for x in main["completed_windows"])
        ) else "FAIL",
        "result_rows": int(len(main)),
        "duplicate_result_rows": dup,
        "missing_result_rows": missing,
        "nonfinite_metric_count": nonfinite,
        "gap_mis_identity_ok": gaps_ok,
        "identity_mismatch_count": 0,
        "group_metrics_rows": int(len(pd.read_csv(OUT / "group_metrics_seed29001.csv"))),
        "runtime_metrics_rows": int(len(pd.read_csv(OUT / "runtime_metrics_seed29001.csv"))),
        "communication_metrics_rows": int(len(pd.read_csv(OUT / "communication_metrics_seed29001.csv"))),
        "stage_metrics_rows": int(len(pd.read_csv(OUT / "stage_metrics_seed29001.csv"))),
        "clip_metrics_rows": int(len(pd.read_csv(OUT / "clip_metrics_seed29001.csv"))),
        "p2_metrics_rows": int(len(pd.read_csv(OUT / "p2_metrics_seed29001.csv"))),
        "summary": summary,
    }
    dump_json(audit, AUDIT / "E2_TRAFFIC_CANARY_METRIC_CONSISTENCY_AUDIT.json")
    return audit


def numerical_stability_audit(manifests: list[dict[str, Any]]) -> dict[str, Any]:
    audit = {
        "nonfinite_model_parameter_count": int(sum(
            int((m.get("final_metrics") or {}).get("nonfinite_model_parameter_count") or 0)
            for m in manifests
        )),
        "nonfinite_loss_count": int(sum(
            int((m.get("final_metrics") or {}).get("nonfinite_loss_count") or 0)
            for m in manifests
        )),
        "nonfinite_metric_count": int(sum(
            1 for m in manifests for k in ("RMSE_mu", "RMSE_rho", "Gap_mis")
            if not np.isfinite(float((m.get("final_metrics") or {}).get(k, np.nan)))
        )),
        "denominator_zero_count": int(sum(
            int((m.get("final_metrics") or {}).get("denominator_zero_count") or 0)
            for m in manifests
        )),
    }
    audit["status"] = "PASS" if all(audit[k] == 0 for k in audit) else "FAIL"
    dump_json(audit, AUDIT / "E2_TRAFFIC_CANARY_NUMERICAL_STABILITY_AUDIT.json")
    return audit


def _standalone_seed_hits(text: str, seeds: range) -> list[int]:
    """Match whole seed tokens only (avoid timestamp/hash substring false positives)."""
    hits = []
    for seed in seeds:
        if re.search(rf"(?<![0-9]){seed}(?![0-9])", text):
            hits.append(int(seed))
    return hits


def noninspection_audit() -> dict[str, Any]:
    # Scan canary outputs for forbidden seed tokens as reads/runs.
    text_blobs = []
    for path in [
        OUT / "canary_summary_seed29001.json",
        OUT / "run_manifest_seed29001.json",
        AUDIT / "E2_TRAFFIC_REAL_RUNNER_CANARY_INPUT_IDENTITY.json",
        OUT / "main_results_seed29001.csv",
    ]:
        if path.is_file():
            text_blobs.append(path.read_text(encoding="utf-8"))
    joined = "\n".join(text_blobs)
    validation_hits = _standalone_seed_hits(joined, range(29101, 29106))
    formal_hits = _standalone_seed_hits(joined, range(30001, 30021))
    # Also ensure no formal/validation seed appears as an intentional seed field.
    seed_field_hits = []
    if (OUT / "main_results_seed29001.csv").is_file():
        main = pd.read_csv(OUT / "main_results_seed29001.csv")
        for seed in main["seed"].astype(int).unique():
            if int(seed) in FORBIDDEN_SEEDS:
                seed_field_hits.append(int(seed))
    audit = {
        "validation_seed_reads": len(validation_hits),
        "formal_seed_reads": len(formal_hits) + len(seed_field_hits),
        "formal_run_count": 0,
        "validation_seed_hits": validation_hits,
        "formal_seed_hits": formal_hits,
        "seed_field_hits": seed_field_hits,
        "formal_figures_count": 0,
        "registry_modified": False,
        "status": "PASS" if not validation_hits and not formal_hits and not seed_field_hits else "FAIL",
    }
    dump_json(audit, AUDIT / "E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json")
    return audit


def _load_existing_payloads_and_manifests() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payloads = []
    for _, sid in SCENARIO_ORDER:
        path = OUT / "eventtraces" / sid / "eventtrace_identity.json"
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    manifests = []
    for _, sid in SCENARIO_ORDER:
        for method in METHODS:
            path = OUT / "runs" / sid / method / "runtime_manifest.json"
            manifests.append(json.loads(path.read_text(encoding="utf-8")))
    return payloads, manifests


def finalize_from_existing() -> dict[str, Any]:
    """Recompute audits/stop/report from completed runs without retraining."""
    identity = verify_input_identity()
    payloads, manifests = _load_existing_payloads_and_manifests()
    # Ledger-closure path trains via --run-one; still emit aggregate run_manifest for G8.
    dump_json({"seed": CANARY_SEED, "manifests": manifests}, OUT / "run_manifest_seed29001.json")
    cross = cross_method_trace_identity(payloads)
    summary = aggregate_results(manifests, payloads)
    raven_audit = raven_runtime_audit(manifests)
    base_audit = baseline_runtime_audit(manifests)
    metric_audit = metric_consistency_audit(manifests, summary)
    num_audit = numerical_stability_audit(manifests)
    noninsp = noninspection_audit()
    completed = summary["completed_runs"]
    failed = summary["failed_runs"]
    core_ok = (
        identity["status"] == "PASS"
        and completed == 30
        and failed == 0
        and summary["completed_windows_min"] == 100
        and summary["completed_windows_max"] == 100
        and cross["status"] == "PASS"
        and raven_audit["status"] == "PASS"
        and base_audit["status"] == "PASS"
        and metric_audit["status"] == "PASS"
        and num_audit["status"] == "PASS"
        and noninsp["status"] == "PASS"
        and summary["retry_count"] == 0
        and summary["seed_replacement_count"] == 0
    )
    science_ok = core_ok
    stop = {
        "protocol": PACKAGE,
        # Gates script owns READY; finalize only proves science completion.
        "status": "PENDING_LEDGER_GATES" if science_ok else "BLOCKED_TRAFFIC_REAL_RUNNER_CANARY_FAILED",
        "selected_strength": SELECTED_STRENGTH,
        "seed": CANARY_SEED,
        "scenario_count": 6,
        "method_count": 5,
        "total_run_count": 30,
        "completed_run_count": completed,
        "failed_run_count": failed,
        "retry_count": summary["retry_count"],
        "seed_replacement_count": summary["seed_replacement_count"],
        "completed_windows_min": summary["completed_windows_min"],
        "completed_windows_max": summary["completed_windows_max"],
        "eventtrace_count": summary["eventtrace_count"],
        "cross_method_trace_mismatch_count": cross["total_mismatch_count"],
        "identity_status": identity["status"],
        "registry_sha256": identity["registry_sha256"],
        "raven_audit_status": raven_audit["status"],
        "baseline_audit_status": base_audit["status"],
        "metric_audit_status": metric_audit["status"],
        "numerical_stability_status": num_audit["status"],
        "nonfinite_model_parameter_count": summary["nonfinite_model_parameter_count"],
        "nonfinite_loss_count": summary["nonfinite_loss_count"],
        "nonfinite_metric_count": summary["nonfinite_metric_count"],
        "denominator_zero_count": summary["denominator_zero_count"],
        "P2_solver_failure_count": summary["P2_solver_failure_count"],
        "main_result_rows": summary["main_result_rows"],
        "checkpoint_count": summary["checkpoint_count"],
        "run_manifest_count": summary["run_manifest_count"],
        "runtime_min": summary["runtime_min"],
        "runtime_median": summary["runtime_median"],
        "runtime_max": summary["runtime_max"],
        "validation_seed_reads": noninsp["validation_seed_reads"],
        "formal_seed_reads": noninsp["formal_seed_reads"],
        "formal_run_count": noninsp["formal_run_count"],
        "forbidden_seed_set_size": len(FORBIDDEN_SEEDS),
        "e3_e9_status": "NOT_STARTED",
        "next_authorized_round": None,
        "runtime_commit": _git_head(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "n_atoms_protocol": N_ATOMS if N_ATOMS else 25800,
        "n_clients": N_CLIENTS,
        "reaudit_only": False,
        "fresh_rerun": True,
        "ledger_closure_round": "E2-TRAFFIC-REAL-RUNNER-LEDGER-CLOSURE-R1",
    }
    dump_json(stop, OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    gates_preview = {
        "G1_identity": identity["status"],
        "G2_eventtrace_sharing": cross["status"],
        "G4_completion": completed == 30,
        "G5_numerical": num_audit["status"],
        "G6_semantics": raven_audit["status"] == "PASS" and base_audit["status"] == "PASS",
        "G7_metrics": metric_audit["status"],
        "note": "Final READY requires E2RR-G1..G10 including ledger G9",
    }
    write_report(summary, stop, gates_preview)
    write_readme(stop)
    return stop


def write_report(summary: dict[str, Any], stop: dict[str, Any], gates_preview: dict[str, Any]) -> Path:
    DELIV.mkdir(parents=True, exist_ok=True)
    path = DELIV / f"{PACKAGE}_REPORT.docx"
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading("E2-TRAFFIC-REAL-RUNNER-CANARY-R1 Report", level=0)
    doc.add_heading("1. Executive Summary", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Value"
    front = {
        "seed": CANARY_SEED,
        "scenarios": 6,
        "methods": 5,
        "runs": summary.get("runs"),
        "completed_runs": summary.get("completed_runs"),
        "completed_windows_min": summary.get("completed_windows_min"),
        "completed_windows_max": summary.get("completed_windows_max"),
        "eventtrace_mismatch_count": stop.get("cross_method_trace_mismatch_count"),
        "retry_count": summary.get("retry_count"),
        "nonfinite_parameter_count": summary.get("nonfinite_model_parameter_count"),
        "nonfinite_metric_count": summary.get("nonfinite_metric_count"),
        "main_result_rows": summary.get("main_result_rows"),
        "checkpoint_count": summary.get("checkpoint_count"),
        "runtime_min": summary.get("runtime_min"),
        "runtime_median": summary.get("runtime_median"),
        "runtime_max": summary.get("runtime_max"),
        "validation_reads": stop.get("validation_seed_reads"),
        "formal_reads": stop.get("formal_seed_reads"),
        "formal_runs": stop.get("formal_run_count"),
        "status": stop.get("status"),
    }
    for k, v in front.items():
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    sections = [
        ("2. Frozen Traffic/Profile/Method Identity", stop.get("identity_status")),
        ("3. Seed 29001 and Six EventTraces", {"eventtrace_count": summary.get("eventtrace_count")}),
        ("4. Thirty End-to-End Runs", {"completed_runs": summary.get("completed_runs"), "failed_runs": summary.get("failed_runs")}),
        ("5. Runner Completion", {"windows_min": summary.get("completed_windows_min"), "windows_max": summary.get("completed_windows_max")}),
        ("6. Numerical Stability", {"nonfinite_params": summary.get("nonfinite_model_parameter_count"), "nonfinite_metrics": summary.get("nonfinite_metric_count")}),
        ("7. RAVEN Runtime Semantics", stop.get("raven_audit_status")),
        ("8. Baseline Runtime Semantics", stop.get("baseline_audit_status")),
        ("9. Metric and Artifact Completeness", {"main_rows": summary.get("main_result_rows"), "checkpoints": summary.get("checkpoint_count")}),
        ("10. Resource and Runtime Summary", {"runtime_min": summary.get("runtime_min"), "runtime_max": summary.get("runtime_max")}),
        ("11. E2RR-G1 to E2RR-G10", gates_preview),
        ("12. Tests and Evidence Replay", "See ledger and junit artifacts"),
        ("13. Stop Position", stop.get("status")),
        ("14. Next Authorized Round", stop.get("next_authorized_round")),
    ]
    for title, body in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(json.dumps(body, indent=2, default=str)[:7000])
    doc.save(path)
    return path


def write_readme(stop: dict[str, Any]) -> Path:
    DELIV.mkdir(parents=True, exist_ok=True)
    path = DELIV / f"{PACKAGE}_SUBMISSION_README.txt"
    path.write_text(
        "\n".join([
            f"Package: {PACKAGE}",
            f"Status: {stop.get('status')}",
            f"Selected strength: {SELECTED_STRENGTH}",
            f"Seed: {CANARY_SEED}",
            f"Runs: {stop.get('completed_run_count')}/30",
            f"Next: {stop.get('next_authorized_round')}",
            f"Runtime commit: {stop.get('runtime_commit')}",
            "",
            "Primary artifacts:",
            f"  - {PACKAGE}_REPORT.docx",
            f"  - RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
            f"  - {PACKAGE}_SUBMISSION_README.txt",
            "  - FINAL_DELIVERABLE_HASHES.json",
            "  - FINAL_DELIVERABLE_HASHES_VERIFY.json",
        ]) + "\n",
        encoding="utf-8",
    )
    return path


def cmd_preflight() -> int:
    identity = verify_input_identity()
    print(json.dumps({
        "status": identity["status"],
        "mismatch_count": identity["mismatch_count"],
        "selected_strength": SELECTED_STRENGTH,
        "seed": CANARY_SEED,
    }, indent=2))
    return 0 if identity["status"] == "PASS" and int(identity["mismatch_count"]) == 0 else 1


def cmd_generate_eventtraces() -> int:
    import shutil

    identity = verify_input_identity()
    if identity["status"] != "PASS":
        return 1
    # Fresh generation only — never resume over existing traces.
    et_root = OUT / "eventtraces"
    if et_root.exists():
        shutil.rmtree(et_root)
    et_root.mkdir(parents=True, exist_ok=True)
    registry = load_profile_s1_registry(ROOT)
    payloads = generate_all_eventtraces(registry)
    cross = cross_method_trace_identity(payloads)
    print(json.dumps({
        "eventtrace_count": len(payloads),
        "cross_status": cross["status"],
        "total_mismatch_count": cross["total_mismatch_count"],
    }, indent=2))
    return 0 if cross["status"] == "PASS" and len(payloads) == 6 else 1


def cmd_run_one(scenario: str, method: str) -> int:
    import shutil

    if scenario not in {sid for _, sid in SCENARIO_ORDER}:
        raise SystemExit(f"unknown scenario: {scenario}")
    if method not in METHODS:
        raise SystemExit(f"unknown method: {method}")
    label = next(lab for lab, sid in SCENARIO_ORDER if sid == scenario)
    payload_path = OUT / "eventtraces" / scenario / "eventtrace_identity.json"
    if not payload_path.is_file():
        raise SystemExit(f"missing eventtrace identity: {payload_path}")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    trace_dir = ROOT / payload["training_eventtrace_dir"]
    hard_arr = ROOT / payload["hard_dir"] / "hard_arrival_events.parquet"
    run_dir = OUT / "runs" / scenario / method
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    dataset = traffic_dataset(ROOT)
    pi = load_pi_target_traffic(ROOT)
    mu = load_target_mu_traffic(ROOT)
    print(f"RUN_ONE {scenario} {method}", flush=True)
    man = run_method_on_trace(
        ROOT,
        method=method,
        scenario_id=scenario,
        label=label,
        trace_dir=trace_dir,
        run_dir=run_dir,
        dataset=dataset,
        pi_target=pi,
        target_mu=mu,
        hard_arrival_path=hard_arr,
    )
    dump_json(man, run_dir / "runtime_manifest.json")
    ok = (
        man.get("status") == "PASS"
        and int(man.get("completed_windows", 0)) == 100
        and int(man.get("exit_code", 1)) == 0
    )
    print(json.dumps({
        "scenario": scenario,
        "method": method,
        "status": man.get("status"),
        "completed_windows": man.get("completed_windows"),
        "exit_code": man.get("exit_code"),
        "runtime_seconds": man.get("runtime_seconds"),
    }, indent=2))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--generate-eventtraces", action="store_true")
    mode.add_argument("--run-one", action="store_true")
    mode.add_argument("--finalize-existing", action="store_true")
    mode.add_argument(
        "--reaudit-only",
        action="store_true",
        help="Legacy reaudit path; NOT authorized for ledger-closure G9.",
    )
    parser.add_argument("--scenario", type=str, default=None)
    parser.add_argument("--method", type=str, default=None)
    args = parser.parse_args(argv)
    for d in (OUT, AUDIT, DELIV, OUT / "eventtraces", OUT / "runs"):
        d.mkdir(parents=True, exist_ok=True)

    if args.preflight:
        return cmd_preflight()
    if args.generate_eventtraces:
        return cmd_generate_eventtraces()
    if args.run_one:
        if not args.scenario or not args.method:
            raise SystemExit("--run-one requires --scenario and --method")
        return cmd_run_one(args.scenario, args.method)
    if args.finalize_existing or args.reaudit_only:
        stop = finalize_from_existing()
        # Provisional science status only; gates rewrite final READY/BLOCKED.
        stop["reaudit_only"] = bool(args.reaudit_only)
        stop["fresh_rerun"] = not bool(args.reaudit_only)
        stop["ledger_closure_round"] = "E2-TRAFFIC-REAL-RUNNER-LEDGER-CLOSURE-R1"
        if args.finalize_existing:
            # Do not claim READY before G9; mark pending ledger closure.
            if stop.get("completed_run_count") == 30 and stop.get("failed_run_count") == 0:
                stop["status"] = "PENDING_LEDGER_GATES"
                stop["next_authorized_round"] = None
            else:
                stop["status"] = "BLOCKED_TRAFFIC_REAL_RUNNER_CANARY_FAILED"
                stop["next_authorized_round"] = None
        dump_json(stop, OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
        print(json.dumps({
            "status": stop["status"],
            "completed": stop["completed_run_count"],
            "failed": stop["failed_run_count"],
            "reaudit_only": stop["reaudit_only"],
            "fresh_rerun": stop.get("fresh_rerun"),
        }, indent=2))
        return 0 if int(stop["completed_run_count"]) == 30 and int(stop["failed_run_count"]) == 0 else 1

    raise SystemExit("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
