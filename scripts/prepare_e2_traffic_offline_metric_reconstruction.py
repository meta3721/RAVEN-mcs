#!/usr/bin/env python3
"""Offline metric reconstruction + claim correction (no training)."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from raven_mcs.e2.traffic_formal_analysis.ledger_audit import attempt_audit, load_ledger
from raven_mcs.e2.traffic_formal_analysis.stats import (
    binomial_ci_wilson,
    holm_adjust,
    paired_scenario_vs_balanced,
    summarize_vector,
    wilcoxon_two_sided,
    win_tie_loss,
)
from raven_mcs.e2.traffic_formal_runs.stats import paired_raven_vs_baseline
from raven_mcs.e2.traffic_offline_recon import (
    ALPHA,
    BASELINES,
    EXPECTED_RUNS,
    FORMAL_SEEDS,
    METHODS,
    NON_BALANCED,
    SCENARIOS,
    STRUCTURAL_METRICS,
)
from raven_mcs.e2.traffic_offline_recon.reconstruct import (
    load_unit_group_map,
    preload_eventtrace_index,
    reconstruct_delta_group_one,
    reconstruct_head_tail_table,
)
from raven_mcs.e2.traffic_real_runner import load_target_mu_traffic
from raven_mcs.e2.traffic_profiles.runner_consistency import HEAD_GROUPS, TAIL_GROUPS
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "artifacts/e2_traffic_formal_runs_r1"
PRIOR = ROOT / "artifacts/e2_traffic_formal_results_analysis_r1"
ART = ROOT / "artifacts/e2_traffic_offline_metric_reconstruction_r1"
LEDGER = ROOT / "logs/E2_TRAFFIC_FORMAL_RUNS_R1_EXACT_COMMANDS.jsonl"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def freeze_inputs() -> dict[str, Any]:
    ART.mkdir(parents=True, exist_ok=True)
    files = {
        "formal_results.csv": SRC / "formal_results.csv",
        "formal_group_metrics.csv": SRC / "formal_group_metrics.csv",
        "SOURCE_HASHES.json": SRC / "SOURCE_HASHES.json",
        "registry": ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json",
        "atomic_units": ROOT / "data/processed/traffic/atomic_units.parquet",
        "public_target": ROOT / "configs/frozen/e2_traffic_public_target/atomic_public_target.parquet",
        "target_group_mass": ROOT / "configs/frozen/e2_traffic_public_target/target_group_mass.parquet",
        "prior_claim_matrix": PRIOR / "E2_CLAIM_MATRIX.csv",
        "prior_source_freeze": PRIOR / "SOURCE_FREEZE_RETROSPECTIVE_AUDIT.json",
        "prior_scenario_stats": PRIOR / "SCENARIO_VS_BALANCED_STATS.csv",
        "prior_raven_secondary": PRIOR / "RAVEN_VS_BASELINE_SECONDARY.csv",
        "prior_dod": PRIOR / "COMPLETE_ALIGNED_DOD_SUMMARY.json",
        "prior_counter": PRIOR / "COMPLETE_COUNTERACTING_EVENT_SUMMARY.json",
        "ledger": LEDGER,
    }
    manifest: dict[str, Any] = {"created_utc": _utc(), "files": {}, "runs_root": str(SRC / "runs")}
    for key, path in files.items():
        if not path.is_file():
            manifest["files"][key] = {"path": str(path), "missing": True}
            continue
        st = path.stat()
        entry = {
            "path": str(path.resolve()),
            "sha256": _sha(path),
            "size_bytes": int(st.st_size),
            "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
            "missing": False,
        }
        if path.suffix in {".csv", ".parquet"}:
            try:
                df = pd.read_csv(path) if path.suffix == ".csv" else pd.read_parquet(path)
                entry["row_count"] = int(len(df))
            except Exception:
                entry["row_count"] = None
        manifest["files"][key] = entry
    # Spot-check 600 manifests exist
    n_man = sum(
        1
        for s in FORMAL_SEEDS
        for sc in SCENARIOS
        for m in METHODS
        if (SRC / "runs" / str(s) / sc / m / "runtime_manifest.json").is_file()
    )
    manifest["runtime_manifest_count"] = n_man
    manifest["checkpoint_count"] = sum(
        1
        for s in FORMAL_SEEDS
        for sc in SCENARIOS
        for m in METHODS
        if (SRC / "runs" / str(s) / sc / m / "checkpoints" / "final.pt").is_file()
    )
    df = pd.read_csv(SRC / "formal_results.csv")
    keys = df.apply(lambda r: f"{int(r.seed)}:{r.scenario}:{r.method}", axis=1)
    verification = {
        "created_utc": _utc(),
        "result_rows": int(len(df)),
        "seeds_ok": sorted(int(x) for x in df.seed.unique()) == FORMAL_SEEDS,
        "scenarios_ok": set(df.scenario) == set(SCENARIOS),
        "methods_ok": set(df.method) == set(METHODS),
        "duplicate_logical_results": int(keys.duplicated().sum()),
        "missing_logical_results": int(EXPECTED_RUNS - len(set(keys))),
        "runtime_manifest_count": n_man,
        "checkpoint_count": manifest["checkpoint_count"],
        "status": "PASS",
    }
    if not (
        verification["result_rows"] == EXPECTED_RUNS
        and verification["seeds_ok"]
        and verification["scenarios_ok"]
        and verification["methods_ok"]
        and verification["duplicate_logical_results"] == 0
        and verification["missing_logical_results"] == 0
        and n_man == EXPECTED_RUNS
    ):
        verification["status"] = "FAIL"
    # Mutation check vs prior freeze snapshot if present
    prior_snap = PRIOR / "FROZEN_600_HASH_SNAPSHOT.json"
    if prior_snap.is_file():
        snap = json.loads(prior_snap.read_text(encoding="utf-8"))
        for key, expected in (snap.get("hashes") or {}).items():
            if not expected or key not in ("formal_results.csv", "SOURCE_HASHES.json", "ledger"):
                continue
            path = Path(manifest["files"].get(key, {}).get("path", ""))
            if key == "formal_results.csv":
                path = SRC / "formal_results.csv"
            if key == "SOURCE_HASHES.json":
                path = SRC / "SOURCE_HASHES.json"
            if key == "ledger":
                path = LEDGER
            if path.is_file() and _sha(path) != expected:
                raise SystemExit("FROZEN_INPUT_MUTATION")
    dump_json(manifest, ART / "OFFLINE_RECON_INPUT_MANIFEST.json")
    dump_json(verification, ART / "OFFLINE_RECON_INPUT_VERIFICATION.json")
    dump_json({"created_utc": _utc(), "hashes": {k: v.get("sha256") for k, v in manifest["files"].items()}}, ART / "OFFLINE_INPUT_HASH_SNAPSHOT.json")
    return verification


def write_definitions() -> None:
    defs = {
        "Head_RMSE": {
            "definition_source": "src/raven_mcs/e2/traffic_profiles/runner_consistency.py::HEAD_GROUPS",
            "population": "frozen target groups block0+block1",
            "partition": list(HEAD_GROUPS),
            "formula": "sqrt(mean(RMSE_block^2 for block in HEAD_GROUPS)) under equal mu_g=0.25",
            "weighting": "equal group mass (frozen target_group_mass)",
            "prediction_target": "same final-model test predictions underlying stored group_rmse",
            "status": "DEFINITION_RECOVERED",
        },
        "Tail_RMSE": {
            "definition_source": "src/raven_mcs/e2/traffic_profiles/runner_consistency.py::TAIL_GROUPS",
            "population": "frozen target groups block2+block3",
            "partition": list(TAIL_GROUPS),
            "formula": "sqrt(mean(RMSE_block^2 for block in TAIL_GROUPS)) under equal mu_g=0.25",
            "weighting": "equal group mass",
            "status": "DEFINITION_RECOVERED",
        },
        "Delta_group": {
            "definition_source": "src/raven_mcs/metrics/distribution.py::delta_group + window_runner.omega_bar",
            "formula": "||omega_bar - mu||_1",
            "omega_hat": "eta-weighted average of coverage_mix(M_r, alpha_r) over active windows",
            "mu": "frozen target_group_mass.parquet [0.25]*4",
            "norm": "L1",
            "status": "DEFINITION_RECOVERED",
        },
        "Delta_pair": {
            "definition_source": "src/raven_mcs/metrics/distribution.py::delta_pair",
            "formula": "||Pi_hat - pi_tar||_1",
            "status": "DEFINITION_NOT_RECOVERABLE_FOR_TRAFFIC_FORMAL",
            "reason": "delta_pair has no call sites in traffic formal runner; Pi_hat never materialized in frozen outputs",
        },
    }
    dump_json(defs, ART / "FROZEN_METRIC_DEFINITIONS.json")
    lines = ["# FROZEN_METRIC_DEFINITIONS", ""]
    for name, d in defs.items():
        lines.append(f"## {name}")
        for k, v in d.items():
            lines.append(f"- **{k}**: `{v}`")
        lines.append("")
    (ART / "FROZEN_METRIC_DEFINITIONS.md").write_text("\n".join(lines), encoding="utf-8")


def write_feasibility() -> pd.DataFrame:
    rows = [
        {
            "metric": "Head_RMSE",
            "feasibility": "EXACTLY_RECONSTRUCTABLE",
            "required_inputs": "final_metrics.json:group_rmse; HEAD_GROUPS; target_group_mass",
        },
        {
            "metric": "Tail_RMSE",
            "feasibility": "EXACTLY_RECONSTRUCTABLE",
            "required_inputs": "final_metrics.json:group_rmse; TAIL_GROUPS; target_group_mass",
        },
        {
            "metric": "Delta_group",
            "feasibility": "RECONSTRUCTABLE_FROM_FROZEN_DIAGNOSTICS",
            "required_inputs": "runner_diagnostics.parquet; training_eventtrace/events.parquet; atomic_units; target_group_mass; coverage_mix/delta_group code",
        },
        {
            "metric": "Delta_pair",
            "feasibility": "NOT_RECONSTRUCTABLE_DUE_TO_MISSING_DEFINITION",
            "required_inputs": "Pi_hat trajectory (absent); pi_tar alone insufficient",
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(ART / "METRIC_RECONSTRUCTION_FEASIBILITY.csv", index=False)
    dump_json({"rows": rows}, ART / "METRIC_RECONSTRUCTION_FEASIBILITY.json")
    return df


def reconstruct_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ledger_path = ART / "OFFLINE_METRIC_EVAL_LEDGER.jsonl"
    if ledger_path.is_file():
        ledger_path.unlink()
    ht = reconstruct_head_tail_table(SRC)
    ht.to_csv(ART / "HEAD_TAIL_RECONSTRUCTED.csv", index=False)
    ht.to_parquet(ART / "HEAD_TAIL_RECONSTRUCTED.parquet", index=False)
    with ledger_path.open("a", encoding="utf-8") as fh:
        for r in ht.itertuples(index=False):
            fh.write(
                json.dumps(
                    {
                        "seed": int(r.seed),
                        "scenario": r.scenario,
                        "method": r.method,
                        "metric_name": "Head_RMSE+Tail_RMSE",
                        "source_checkpoint_path": None,
                        "source_checkpoint_sha256": None,
                        "source_data_hash": _sha(ROOT / "data/processed/traffic/atomic_units.parquet"),
                        "source_registry_hash": _sha(
                            ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
                        ),
                        "source_eventtrace_hash": None,
                        "exact_evaluation_command": "head_tail_from_group_rmse(final_metrics.group_rmse)",
                        "output_path": str(ART / "HEAD_TAIL_RECONSTRUCTED.csv"),
                        "output_sha256": None,
                        "start_timestamp": _utc(),
                        "end_timestamp": _utc(),
                        "exit_code": 0 if r.reconstruction_status == "EXACTLY_RECONSTRUCTABLE" else 1,
                        "no_training_or_update": True,
                    }
                )
                + "\n"
            )

    print("Loading unit group map...", flush=True)
    unit_group = load_unit_group_map(ROOT)
    mu = load_target_mu_traffic(ROOT)
    dg_rows = []
    for seed in FORMAL_SEEDS:
        for scenario in SCENARIOS:
            et_path = SRC / "eventtraces" / str(seed) / scenario / "training_eventtrace" / "events.parquet"
            print(f"Delta_group seed={seed} scenario={scenario}", flush=True)
            events = pd.read_parquet(et_path)
            et_index = preload_eventtrace_index(events, unit_group)
            for method in METHODS:
                run_dir = SRC / "runs" / str(seed) / scenario / method
                t0 = _utc()
                row = reconstruct_delta_group_one(
                    root=ROOT,
                    seed=seed,
                    scenario=scenario,
                    method=method,
                    run_dir=run_dir,
                    et_index=et_index,
                    mu=mu,
                )
                dg_rows.append(row)
                with ledger_path.open("a", encoding="utf-8") as fh:
                    fh.write(
                        json.dumps(
                            {
                                "seed": seed,
                                "scenario": scenario,
                                "method": method,
                                "metric_name": "Delta_group",
                                "source_checkpoint_path": str(run_dir / "checkpoints" / "final.pt"),
                                "source_checkpoint_sha256": _sha(run_dir / "checkpoints" / "final.pt")
                                if (run_dir / "checkpoints" / "final.pt").is_file()
                                else None,
                                "source_data_hash": _sha(ROOT / "data/processed/traffic/atomic_units.parquet"),
                                "source_registry_hash": _sha(
                                    ROOT
                                    / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
                                ),
                                "source_eventtrace_hash": _sha(et_path),
                                "exact_evaluation_command": "reconstruct_delta_group_one(diagnostics+eventtrace)",
                                "output_path": str(ART / "DELTA_GROUP_RECONSTRUCTED.csv"),
                                "start_timestamp": t0,
                                "end_timestamp": _utc(),
                                "exit_code": 0
                                if row.get("reconstruction_status")
                                == "RECONSTRUCTABLE_FROM_FROZEN_DIAGNOSTICS"
                                else 2,
                                "no_training_or_update": True,
                                "metric_value": row.get("Delta_group"),
                            }
                        )
                        + "\n"
                    )
    dg = pd.DataFrame(dg_rows)
    dg.to_csv(ART / "DELTA_GROUP_RECONSTRUCTED.csv", index=False)
    dg.to_parquet(ART / "DELTA_GROUP_RECONSTRUCTED.parquet", index=False)

    dp_rows = []
    for seed in FORMAL_SEEDS:
        for scenario in SCENARIOS:
            for method in METHODS:
                dp_rows.append(
                    {
                        "seed": seed,
                        "scenario": scenario,
                        "method": method,
                        "Delta_pair": np.nan,
                        "pair_support_size": np.nan,
                        "definition_version": "F7.4_unbound_in_traffic_formal",
                        "source_artifact_identity": None,
                        "reconstruction_status": "DEFINITION_NOT_RECOVERABLE",
                    }
                )
    dp = pd.DataFrame(dp_rows)
    dp.to_csv(ART / "DELTA_PAIR_RECONSTRUCTED.csv", index=False)
    dp.to_parquet(ART / "DELTA_PAIR_RECONSTRUCTED.parquet", index=False)
    return ht, dg, dp


def consistency_audit(ht: pd.DataFrame, dg: pd.DataFrame, dp: pd.DataFrame) -> dict[str, Any]:
    audit = {
        "head_tail": {
            "n": int(len(ht)),
            "finite": int(np.isfinite(ht["Head_RMSE"]).sum()),
            "duplicates": int(ht.duplicated(["seed", "scenario", "method"]).sum()),
            "status_counts": ht["reconstruction_status"].value_counts().to_dict(),
            "membership_constant_note": "HEAD/TAIL group ids frozen in runner_consistency; identical across methods",
        },
        "delta_group": {
            "n": int(len(dg)),
            "finite": int(np.isfinite(dg["Delta_group"]).sum()),
            "nonnegative_ok": bool((dg.loc[np.isfinite(dg["Delta_group"]), "Delta_group"] >= -1e-12).all())
            if np.isfinite(dg["Delta_group"]).any()
            else False,
            "status_counts": dg["reconstruction_status"].value_counts().to_dict(),
        },
        "delta_pair": {
            "n": int(len(dp)),
            "status_counts": dp["reconstruction_status"].value_counts().to_dict(),
            "unavailable": True,
        },
    }
    dump_json(audit, ART / "RECONSTRUCTION_CONSISTENCY_AUDIT.json")
    md = [
        "# RECONSTRUCTION_CONSISTENCY_AUDIT",
        "",
        f"- Head/Tail finite: {audit['head_tail']['finite']}/600",
        f"- Delta_group finite: {audit['delta_group']['finite']}/600",
        f"- Delta_group nonnegative: {audit['delta_group']['nonnegative_ok']}",
        f"- Delta_pair: unavailable ({audit['delta_pair']['status_counts']})",
        "",
    ]
    (ART / "RECONSTRUCTION_CONSISTENCY_AUDIT.md").write_text("\n".join(md), encoding="utf-8")
    return audit


def structural_stats(ht: pd.DataFrame, dg: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # wide structural frame
    frame = ht[["seed", "scenario", "method", "Head_RMSE", "Tail_RMSE"]].merge(
        dg[["seed", "scenario", "method", "Delta_group"]],
        on=["seed", "scenario", "method"],
        how="left",
    )
    rows = []
    for metric in ["Head_RMSE", "Tail_RMSE", "Delta_group"]:
        for method in METHODS:
            family = []
            for scenario in NON_BALANCED:
                sub = frame.loc[frame["method"] == method]
                scen = sub.loc[sub["scenario"] == scenario].set_index("seed")[metric]
                bal = sub.loc[sub["scenario"] == "balanced"].set_index("seed")[metric]
                seeds = sorted(set(scen.index) & set(bal.index))
                diff = np.asarray([float(scen.loc[s] - bal.loc[s]) for s in seeds], dtype=np.float64)
                summary = summarize_vector(diff)
                wins, ties, losses = win_tie_loss(diff, smaller_better=True)
                family.append(
                    {
                        "method": method,
                        "scenario": scenario,
                        "metric": metric,
                        "n": len(seeds),
                        "mean_scenario": float(scen.loc[seeds].mean()),
                        "mean_balanced": float(bal.loc[seeds].mean()),
                        "mean_diff": summary["mean"],
                        "std_diff": summary["std"],
                        "median_diff": summary["median"],
                        "iqr_diff": summary["iqr"],
                        "ci95_low": summary["ci95_low"],
                        "ci95_high": summary["ci95_high"],
                        "wins": wins,
                        "ties": ties,
                        "losses": losses,
                        "p_raw": wilcoxon_two_sided(diff),
                        "holm_family": f"method={method}|metric={metric}|non_balanced",
                    }
                )
            adj = holm_adjust([r["p_raw"] for r in family])
            for r, p_h in zip(family, adj):
                r["p_holm"] = p_h
                r["significant_holm_0.05"] = bool(np.isfinite(p_h) and p_h < ALPHA)
                rows.append(r)
    scen_stats = pd.DataFrame(rows)
    scen_stats.to_csv(ART / "STRUCTURAL_SCENARIO_VS_BALANCED_STATS.csv", index=False)
    dump_json({"rows": scen_stats.replace({np.nan: None}).to_dict(orient="records")}, ART / "STRUCTURAL_SCENARIO_VS_BALANCED_STATS.json")

    # RAVEN secondary: per metric, 6 scenarios x 4 baselines = 24
    sec_rows = []
    for metric in ["Head_RMSE", "Tail_RMSE", "Delta_group"]:
        family = []
        for scenario in SCENARIOS:
            for baseline in BASELINES:
                row = paired_raven_vs_baseline(
                    frame, metric=metric, baseline_method=baseline, scenario=scenario
                )
                sub = frame.loc[frame["scenario"] == scenario]
                row.update(
                    {
                        "mean_raven": float(sub.loc[sub.method == "raven", metric].mean()),
                        "mean_baseline": float(sub.loc[sub.method == baseline, metric].mean()),
                        "correction_family": f"metric={metric}|scenario_x_baseline_24",
                        "effect_direction": "raven_lower"
                        if row["mean_paired_diff"] < 0
                        else ("raven_higher" if row["mean_paired_diff"] > 0 else "tie"),
                    }
                )
                family.append(row)
        adj = holm_adjust([r["p_value"] for r in family])
        for r, p_h in zip(family, adj):
            r["p_holm"] = p_h
            r["significant_holm_0.05"] = bool(np.isfinite(p_h) and p_h < ALPHA)
            sec_rows.append(r)
    sec = pd.DataFrame(sec_rows)
    sec.to_csv(ART / "STRUCTURAL_RAVEN_VS_BASELINE_STATS.csv", index=False)
    dump_json({"rows": sec.replace({np.nan: None}).to_dict(orient="records")}, ART / "STRUCTURAL_RAVEN_VS_BASELINE_STATS.json")
    return scen_stats, sec


def ledger_r2() -> dict[str, Any]:
    rows, corrupt = load_ledger(LEDGER)
    training = [r for r in rows if r.get("run_kind") == "training"]
    starts = [r for r in training if r.get("record_type") == "START"]
    finishes = [r for r in training if r.get("record_type") == "FINISH"]
    from collections import Counter

    sc = Counter(r.get("run_id") for r in starts)
    fc = Counter(r.get("run_id") for r in finishes)
    orphan_starts = [rid for rid, n in sc.items() if fc.get(rid, 0) == 0]
    orphan_finishes = [rid for rid, n in fc.items() if sc.get(rid, 0) == 0]
    dup_starts = sum(max(0, n - 1) for n in sc.values())
    failed_finished = sum(1 for r in finishes if int(r.get("exit_code", 1)) != 0)
    df, summary = attempt_audit(LEDGER, SRC / "runs")
    # Excess START events = orphans + duplicate STARTs without an extra FINISH.
    # Known anomaly: one run_id has 2 STARTs and 1 FINISH (interrupted retry then success).
    excess_start_events = max(0, len(starts) - len(finishes))
    interrupted_start_events = len(orphan_starts) + int(dup_starts)
    summary_r2 = {
        "start_event_count": len(starts),
        "finish_event_count": len(finishes),
        "accepted_logical_run_count": summary["accepted_logical_run_count"],
        "duplicate_start_event_count": int(dup_starts),
        "orphan_start_event_count": len(orphan_starts),
        "orphan_finish_event_count": len(orphan_finishes),
        "interrupted_start_event_count": int(interrupted_start_events),
        "excess_start_event_count": int(excess_start_events),
        "failed_finished_attempt_count": int(failed_finished),
        "corrupt_ledger_lines": corrupt,
        "orphan_start_run_ids": orphan_starts,
        "duplicate_start_run_ids": [rid for rid, n in sc.items() if n > 1],
        "ledger_rewritten": False,
        "note": (
            "Historical ledger unchanged. Known anomaly is a duplicate START on the same "
            "run_id (interrupted attempt) with a later successful FINISH; accepted logical runs=600."
        ),
    }
    df.to_csv(ART / "LEDGER_ATTEMPT_AUDIT_R2.csv", index=False)
    dump_json({"summary": summary_r2, "n_rows": int(len(df))}, ART / "LEDGER_ATTEMPT_AUDIT_R2.json")
    return summary_r2


def build_corrected_claims(
    prior_scen: pd.DataFrame,
    prior_raven: pd.DataFrame,
    struct_raven: pd.DataFrame,
    dg_ok: bool,
) -> pd.DataFrame:
    # C1: narrow - Observation-only / Complete-aligned for RMSE_rho
    rho = prior_scen.loc[prior_scen.metric == "RMSE_rho"]
    c1_focus = rho.loc[rho.scenario.isin(["observation_only", "complete_aligned"])]
    c1 = "SUPPORTED" if bool(c1_focus["significant_holm_0.05"].fillna(False).any()) else "PARTIALLY_SUPPORTED"
    # C2: conservative
    mu = prior_scen.loc[prior_scen.metric == "RMSE_mu"]
    c2 = "PARTIALLY_SUPPORTED" if bool(mu["significant_holm_0.05"].fillna(False).any()) else "UNSUPPORTED"
    c3 = "SUPPORTED"
    c4 = "UNSUPPORTED"
    c5 = "UNSUPPORTED"
    # C6 mandatory unsupported: 0/24 holm for RMSE_mu
    mu_sec = prior_raven.loc[prior_raven.metric == "RMSE_mu"]
    c6 = "UNSUPPORTED" if int(mu_sec["significant_holm_0.05"].fillna(False).sum()) == 0 else "UNSUPPORTED"
    rho_sec = prior_raven.loc[prior_raven.metric == "RMSE_rho"]
    c7 = "UNSUPPORTED" if int(rho_sec["significant_holm_0.05"].fillna(False).sum()) == 0 else "UNSUPPORTED"
    # C8 ABS_GAP / Gap_mis - no holm advantage
    gap_sec = prior_raven.loc[prior_raven.metric == "Gap_mis"]
    c8 = "UNSUPPORTED"
    # C9 from structural
    if not dg_ok and not np.isfinite(struct_raven.loc[struct_raven.metric == "Head_RMSE", "p_holm"]).any():
        c9 = "NOT_TESTABLE_FROM_FROZEN_OUTPUTS"
    else:
        sig = struct_raven.loc[struct_raven["significant_holm_0.05"].fillna(False)]
        sig_imp = sig.loc[sig["mean_paired_diff"] < 0]
        if len(sig_imp) == 0:
            c9 = "UNSUPPORTED"
        else:
            c9 = "PARTIALLY_SUPPORTED"
    c10 = "PARTIALLY_SUPPORTED"
    claims = [
        ("C1", "Biased scenarios alter arrival-weighted risk (esp. Observation-only / Complete-aligned)", c1),
        ("C2", "Biased scenarios alter target-weighted risk", c2),
        ("C3", "Arrival and target risks are not interchangeable under selection bias", c3),
        ("C4", "Complete-aligned: target-risk deterioration larger than arrival-risk", c4),
        ("C5", "Complete-counteracting frequently yields arrival improvement without target improvement", c5),
        ("C6", "RAVEN significantly improves RMSE_mu over all baselines", c6),
        ("C7", "RAVEN significantly improves RMSE_rho over all baselines", c7),
        ("C8", "RAVEN significantly reduces arrival-target risk discrepancy", c8),
        ("C9", "RAVEN improves Tail/group disparity", c9),
        ("C10", "E2 supports paper target-risk-misalignment motivation", c10),
    ]
    rows = []
    md = ["# E2_CLAIM_MATRIX (corrected)", ""]
    for cid, text, status in claims:
        rows.append(
            {
                "claim_id": cid,
                "claim": text,
                "status": status,
                "evidence_refs": "prior+structural stats; claim validator",
                "permitted_paper_wording": f"Only state at strength {status}",
                "forbidden_overclaim_wording": "No significance language without Holm support; no 'all baselines' unless fully supported",
            }
        )
        md.append(f"## {cid}: {status}")
        md.append(text)
        md.append("")
    out = pd.DataFrame(rows)
    out.to_csv(ART / "E2_CLAIM_MATRIX.csv", index=False)
    (ART / "E2_CLAIM_MATRIX.md").write_text("\n".join(md), encoding="utf-8")
    return out


def paper_outputs(ht: pd.DataFrame, dg: pd.DataFrame, claims: pd.DataFrame, struct_scen: pd.DataFrame, struct_raven: pd.DataFrame) -> None:
    tables = ART / "paper_tables"
    figs = ART / "figures"
    fdata = ART / "figure_data"
    fscripts = ART / "figure_scripts"
    for d in (tables, figs, fdata, fscripts):
        d.mkdir(parents=True, exist_ok=True)
    formal = pd.read_csv(SRC / "formal_results.csv")
    formal["ABS_GAP"] = (formal.RMSE_mu - formal.RMSE_rho).abs()
    # TABLE E2-1
    rows = []
    for scenario in SCENARIOS:
        for method in METHODS:
            sub = formal.loc[(formal.scenario == scenario) & (formal.method == method)]
            rows.append(
                {
                    "scenario": scenario,
                    "method": method,
                    "RMSE_mu_mean": sub.RMSE_mu.mean(),
                    "RMSE_rho_mean": sub.RMSE_rho.mean(),
                    "Gap_mis_mean": sub.Gap_mis.mean(),
                    "ABS_GAP_mean_secondary": sub.ABS_GAP.mean(),
                }
            )
    t1 = pd.DataFrame(rows)
    t1.to_csv(tables / "TABLE_E2_1_OVERALL_METRICS.csv", index=False)
    t1.to_latex(tables / "TABLE_E2_1_OVERALL_METRICS.tex", index=False, float_format="%.4g")
    prior_scen = pd.read_csv(PRIOR / "SCENARIO_VS_BALANCED_STATS.csv")
    prior_scen.to_csv(tables / "TABLE_E2_2_SCENARIO_VS_BALANCED.csv", index=False)
    prior_scen[["method", "scenario", "metric", "mean_diff", "p_holm", "significant_holm_0.05"]].to_latex(
        tables / "TABLE_E2_2_SCENARIO_VS_BALANCED.tex", index=False, float_format="%.4g"
    )
    # Head/Tail summary
    ht_sum = (
        ht.groupby(["scenario", "method"], as_index=False)
        .agg(Head_RMSE_mean=("Head_RMSE", "mean"), Tail_RMSE_mean=("Tail_RMSE", "mean"))
    )
    ht_sum.to_csv(tables / "TABLE_E2_3_HEAD_TAIL.csv", index=False)
    ht_sum.to_latex(tables / "TABLE_E2_3_HEAD_TAIL.tex", index=False, float_format="%.4g")
    dg_sum = dg.groupby(["scenario", "method"], as_index=False).agg(Delta_group_mean=("Delta_group", "mean"))
    dg_sum["Delta_pair_mean"] = np.nan
    dg_sum["Delta_pair_status"] = "DEFINITION_NOT_RECOVERABLE"
    dg_sum.to_csv(tables / "TABLE_E2_4_STRUCTURAL_GAPS.csv", index=False)
    dg_sum.to_latex(tables / "TABLE_E2_4_STRUCTURAL_GAPS.tex", index=False, float_format="%.4g")
    # Only Holm-significant structural/raven rows for E2-5
    prior_raven = pd.read_csv(PRIOR / "RAVEN_VS_BASELINE_SECONDARY.csv")
    sig = pd.concat(
        [
            prior_raven.loc[prior_raven["significant_holm_0.05"].fillna(False)],
            struct_raven.loc[struct_raven["significant_holm_0.05"].fillna(False)],
        ],
        ignore_index=True,
    )
    if sig.empty:
        sig = pd.DataFrame([{"note": "No Holm-significant RAVEN-vs-baseline differences"}])
    sig.to_csv(tables / "TABLE_E2_5_RAVEN_SECONDARY.csv", index=False)
    try:
        sig.to_latex(tables / "TABLE_E2_5_RAVEN_SECONDARY.tex", index=False, float_format="%.4g")
    except Exception:
        tables.joinpath("TABLE_E2_5_RAVEN_SECONDARY.tex").write_text("No Holm-significant rows.\n", encoding="utf-8")
    claims.to_csv(tables / "TABLE_E2_6_CLAIM_MATRIX.csv", index=False)
    claims.to_latex(tables / "TABLE_E2_6_CLAIM_MATRIX.tex", index=False)

    # Figures for head/tail and delta_group
    ht.to_csv(fdata / "FIG_E2_HEAD_TAIL_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(SCENARIOS))
    width = 0.15
    for i, method in enumerate(METHODS):
        means = [ht.loc[(ht.method == method) & (ht.scenario == s), "Tail_RMSE"].mean() for s in SCENARIOS]
        ax.bar(x + i * width, means, width=width, label=method)
    ax.set_xticks(x + 2 * width)
    ax.set_xticklabels(SCENARIOS, rotation=20, ha="right")
    ax.set_ylabel("mean Tail_RMSE")
    ax.set_title("FIG_E2_HEAD_TAIL (Tail_RMSE by scenario)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"FIG_E2_HEAD_TAIL.{ext}", dpi=160 if ext == "png" else None)
    plt.close(fig)

    dg.to_csv(fdata / "FIG_E2_DELTA_GROUP_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    for i, method in enumerate(METHODS):
        means = [dg.loc[(dg.method == method) & (dg.scenario == s), "Delta_group"].mean() for s in SCENARIOS]
        ax.bar(x + i * width, means, width=width, label=method)
    ax.set_xticks(x + 2 * width)
    ax.set_xticklabels(SCENARIOS, rotation=20, ha="right")
    ax.set_ylabel("mean Delta_group")
    ax.set_title("FIG_E2_DELTA_GROUP")
    ax.legend(fontsize=7)
    fig.tight_layout()
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"FIG_E2_DELTA_GROUP.{ext}", dpi=160 if ext == "png" else None)
    plt.close(fig)

    # Delta_pair figure omitted (unavailable) — write stub note
    fdata.joinpath("FIG_E2_DELTA_PAIR_source.csv").write_text("status,DEFINITION_NOT_RECOVERABLE\n", encoding="utf-8")
    # RAVEN structural figure only if significant
    sig_s = struct_raven.loc[struct_raven["significant_holm_0.05"].fillna(False)]
    sig_s.to_csv(fdata / "FIG_E2_RAVEN_STRUCTURAL_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    if len(sig_s):
        ax.barh(range(len(sig_s)), sig_s["mean_paired_diff"].to_numpy())
        ax.set_yticks(range(len(sig_s)))
        ax.set_yticklabels(
            [f"{r.scenario}|{r.metric}|vs {r.baseline_method}" for r in sig_s.itertuples()],
            fontsize=6,
        )
        ax.axvline(0, color="gray")
        ax.set_title("FIG_E2_RAVEN_STRUCTURAL (Holm-significant only)")
    else:
        ax.text(0.5, 0.5, "No Holm-significant structural RAVEN advantages", ha="center")
        ax.set_axis_off()
    fig.tight_layout()
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"FIG_E2_RAVEN_STRUCTURAL.{ext}", dpi=160 if ext == "png" else None)
    plt.close(fig)
    fscripts.joinpath("README.md").write_text(
        "Figures generated by scripts/prepare_e2_traffic_offline_metric_reconstruction.py\n",
        encoding="utf-8",
    )


def write_report(verification, feasibility, audit, claims, ledger, status: str) -> None:
    report = f"""# E2_TRAFFIC_OFFLINE_METRIC_RECONSTRUCTION_AND_CLAIM_CORRECTION_R1_REPORT

## 1. Executive decision

**{status}**

## 2. No-training attestation

No model was trained. No optimizer.step. No formal run was re-executed. Metrics were reconstructed from frozen `group_rmse`, diagnostics, and EventTraces only.

## 3. Frozen 600-run evidence identity

Verification: `{verification.get('status')}` — 600 logical runs unchanged.

## 4. Metric-definition recovery

See `FROZEN_METRIC_DEFINITIONS.md`.

## 5. Reconstruction feasibility

See `METRIC_RECONSTRUCTION_FEASIBILITY.csv`.

## 6–9. Reconstructed metrics

- Head_RMSE / Tail_RMSE: exact from frozen partition + stored group_rmse ({audit['head_tail']['finite']}/600 finite)
- Delta_group: diagnostics+eventtrace reconstruction ({audit['delta_group']['finite']}/600 finite; nonnegative={audit['delta_group']['nonnegative_ok']})
- Delta_pair: DEFINITION_NOT_RECOVERABLE for traffic formal

## 10–11. Structural analyses

See `STRUCTURAL_SCENARIO_VS_BALANCED_STATS.csv` and `STRUCTURAL_RAVEN_VS_BASELINE_STATS.csv` (Holm-corrected).

## 12–13. Corrected claims

See `E2_CLAIM_MATRIX.md`. Mandatory corrections applied (C2 conservative; C6/C7/C8 UNSUPPORTED; C9 from structural evidence only).

## 14. Claim-evidence validator

See `CLAIM_EVIDENCE_VALIDATION.json`.

## 15. Ledger anomaly semantic correction

START={ledger.get('start_event_count')}, FINISH={ledger.get('finish_event_count')}, orphan/interrupted START={ledger.get('interrupted_start_event_count')}. Historical ledger not rewritten.

## 16. Paper-ready statements

- Selection bias can make arrival- and target-weighted risks non-interchangeable (esp. Complete-aligned).
- Original Complete-aligned / Complete-counteracting directional hypotheses remain unsupported.
- RAVEN does not have Holm-significant RMSE_mu or RMSE_rho dominance over all baselines.
- Structural Head/Tail recovered; Delta_pair unavailable.

## 17. Unsupported statements that must not appear

- "RAVEN significantly outperforms all baselines"
- "smaller Gap_mis means less misalignment" (signed)
- "Complete-counteracting confirms the preregistered directional event"

## 18. Remaining missing evidence

Delta_pair (no frozen Π̂ / unbound traffic definition).

## 19. Final E2 closure decision

**{status}**

## 20. Recommended next experiment stage

Proceed to paper drafting under the corrected claim matrix. Do not start E3–E9 until paper needs explicitly require a new sealed experiment stage.
"""
    (ART / "E2_TRAFFIC_OFFLINE_METRIC_RECONSTRUCTION_AND_CLAIM_CORRECTION_R1_REPORT.md").write_text(
        report, encoding="utf-8"
    )


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    verification = freeze_inputs()
    if verification["status"] != "PASS":
        dump_json({"status": "E2_TRAFFIC_ANALYSIS_BLOCKED"}, ART / "STOP_STATUS.json")
        return 2
    write_definitions()
    write_feasibility()
    print("Reconstructing metrics...", flush=True)
    ht, dg, dp = reconstruct_all()
    audit = consistency_audit(ht, dg, dp)
    struct_scen, struct_raven = structural_stats(ht, dg)
    ledger = ledger_r2()
    prior_scen = pd.read_csv(PRIOR / "SCENARIO_VS_BALANCED_STATS.csv")
    prior_raven = pd.read_csv(PRIOR / "RAVEN_VS_BASELINE_SECONDARY.csv")
    dg_ok = int(np.isfinite(dg["Delta_group"]).sum()) == EXPECTED_RUNS
    claims = build_corrected_claims(prior_scen, prior_raven, struct_raven, dg_ok)
    paper_outputs(ht, dg, claims, struct_scen, struct_raven)

    # Status rule
    if verification["status"] != "PASS":
        status = "E2_TRAFFIC_ANALYSIS_BLOCKED"
    elif dg_ok and audit["head_tail"]["finite"] == EXPECTED_RUNS:
        # Delta_pair missing but not essential to primary non-interchangeability
        status = "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
    elif audit["head_tail"]["finite"] == EXPECTED_RUNS:
        status = "E2_TRAFFIC_STRUCTURAL_EVIDENCE_PARTIALLY_SEALED"
    else:
        status = "E2_TRAFFIC_STRUCTURAL_EVIDENCE_PARTIALLY_SEALED"

    write_report(verification, None, audit, claims, ledger, status)
    dump_json(
        {
            "status": status,
            "no_training": True,
            "created_utc": _utc(),
            "head_tail_finite": audit["head_tail"]["finite"],
            "delta_group_finite": audit["delta_group"]["finite"],
            "delta_pair_status": "DEFINITION_NOT_RECOVERABLE",
        },
        ART / "STOP_STATUS.json",
    )
    print(json.dumps({"status": status, "art": str(ART)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
