#!/usr/bin/env python3
"""Legal 100-window freeze + Balanced opportunity calibration + conditional matrix."""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.legal_horizon.calibrate import (
    run_balanced_calibration_for_seed,
)
from raven_mcs.e2.legal_horizon.sampler import generate_legal_horizon_mother_trace
from raven_mcs.e2.legal_horizon.schedule100 import (
    audit_source_uniqueness,
    build_legal_100_schedule,
    freeze_legal_horizon,
)
from raven_mcs.e2.legal_horizon.stratum100 import (
    build_merged_true_stratum_100,
    raw_schedule_exposure,
)
from raven_mcs.e2.scenario_generator import load_strength_profile_registry
from raven_mcs.e2.stage2.gates import (
    PROFILES,
    SCENARIOS,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
    select_strength_profile,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_LEGAL_HORIZON_AND_BALANCED_OPPORTUNITY_CALIBRATION_R1"
NUM_WINDOWS = 100
NON_BALANCED = (
    "opportunity_only",
    "observation_only",
    "usable_only",
    "complete_aligned",
    "complete_counteracting",
)
NEUTRAL_PROFILE = "PROFILE-S1"  # kappa unused for balanced directions


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _balanced_hard_pass(diag: dict) -> tuple[bool, list[str]]:
    fails = []
    if float(diag["D_TV_group"]) > 0.03:
        fails.append("D_TV_group")
    if float(diag.get("D_TV_true_stratum", diag["D_TV_stratum"])) > 0.05:
        fails.append("D_TV_true_stratum")
    if not (0.95 <= float(diag["tail_mass_ratio"]) <= 1.05):
        fails.append("tail_mass_ratio")
    if not (0.95 <= float(diag["head_mass_ratio"]) <= 1.05):
        fails.append("head_mass_ratio")
    if float(diag["D_TV_group_exp_emp"]) > 0.03:
        fails.append("D_TV_group_exp_emp")
    if float(diag.get("D_TV_true_stratum_exp_emp", diag["D_TV_stratum_exp_emp"])) > 0.05:
        fails.append("D_TV_true_stratum_exp_emp")
    if not (0.18 <= float(diag["realized_observation_rate"]) <= 0.22):
        fails.append("obs_rate")
    if not (0.57 <= float(diag["realized_usable_rate"]) <= 0.63):
        fails.append("use_rate")
    if int(diag["unsupported_arrival_count"]) != 0:
        fails.append("unsupported")
    if float(diag["total_hard_arrival_mass"]) <= 0:
        fails.append("arrival_mass")
    return (not fails), fails


def _write_report(root: Path, ctx: dict) -> Path:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading(PACKAGE, level=0)
    # Front table
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Metric"
    hdr[1].text = "Value"
    for k, v in ctx.get("front_table", []):
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    for title, body in ctx.get("sections", []):
        doc.add_heading(title, level=1)
        doc.add_paragraph(str(body)[:5000])
    out = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def main() -> int:
    root = ROOT
    for d in (
        "outputs/e2_balanced_calibration",
        "outputs/audits",
        "configs/frozen/e2_legal_horizon",
        "configs/frozen/e2_balanced_calibration",
        f"deliverables/TO_SUBMIT_{PACKAGE}",
        "logs",
    ):
        (root / d).mkdir(parents=True, exist_ok=True)

    if not (root / "outputs/audits/E2_ILLEGAL_300_AND_UNCALIBRATED_BALANCED_TOMBSTONE.json").is_file():
        raise SystemExit("missing illegal-300 tombstone")

    horizon = freeze_legal_horizon(root)

    # Schedules
    schedules = {}
    for seed in VALIDATION_SEEDS:
        streams = build_base_random_streams(
            seed, n_windows=NUM_WINDOWS, n_clients=8, max_risk_set=20,
        )
        schedules[seed] = build_legal_100_schedule(
            seed, schedule_uniforms=streams["base_client_window_schedule"], root=root,
        )
        # persist schedule
        sched_dir = root / "outputs/e2_balanced_calibration/schedules" / str(seed)
        sched_dir.mkdir(parents=True, exist_ok=True)
        dump_json({
            "seed": seed,
            "schedule_hash": schedules[seed]["schedule_hash"],
            "audit": schedules[seed]["audit"],
            "clients": schedules[seed]["clients"],
        }, sched_dir / "schedule_meta.json")

    uniq = audit_source_uniqueness(schedules, root)
    if uniq["status"] != "PASS":
        dump_json({
            "status": "BLOCKED_INSUFFICIENT_NONREUSED_SOURCE",
            "uniqueness": uniq,
        }, root / "outputs/e2_balanced_calibration/E2_STOP_STATUS.json")
        return 2

    # Stratum merge using schedule exposure
    exp = raw_schedule_exposure(schedules, root)
    stratum = build_merged_true_stratum_100(root, schedule_exposure=exp)

    # Soft calibration per seed (must all pass)
    soft_rows = []
    calibrated = {}
    gamma_ref = None
    residuals = []
    for seed in VALIDATION_SEEDS:
        result = run_balanced_calibration_for_seed(seed, schedules[seed], root=root)
        calibrated[seed] = result
        sol = result["solved"]
        soft_rows.append({
            "seed": seed,
            "D_TV_group_soft": sol["D_TV_group_soft"],
            "D_TV_stratum_soft": sol["D_TV_stratum_soft"],
            "D_TV_client_stratum_soft": sol["D_TV_client_stratum_soft"],
            "max_marginal_residual": sol["max_marginal_residual"],
            "unsupported_target_cell_count": sol["unsupported_target_cell_count"],
            "solver_converged": sol["solver_converged"],
            "status": sol["status"],
        })
        result["C_ks"].assign(seed=seed).to_csv(
            root / f"outputs/e2_balanced_calibration/E2_RAW_CANDIDATE_EXPOSURE_BY_CLIENT_STRATUM_{seed}.csv",
            index=False,
        )
        if gamma_ref is None:
            gamma_ref = sol["gamma"]
        for key, val in sol["rho_ks"].items():
            residuals.append({
                "seed": seed, "cell": key, "rho": val,
                "gamma": sol["gamma"].get(key),
            })

    # Combined exposure CSV
    pd.concat([
        calibrated[s]["C_ks"].assign(seed=s) for s in VALIDATION_SEEDS
    ]).to_csv(
        root / "outputs/e2_balanced_calibration/E2_RAW_CANDIDATE_EXPOSURE_BY_CLIENT_STRATUM.csv",
        index=False,
    )
    pd.DataFrame(residuals).to_csv(
        root / "outputs/e2_balanced_calibration/E2_BALANCED_CALIBRATION_RESIDUALS.csv",
        index=False,
    )
    soft_df = pd.DataFrame(soft_rows)
    soft_pass = bool((soft_df["status"] == "PASS").all())
    soft_audit = {
        "status": "PASS" if soft_pass else "BLOCKED_BALANCED_CALIBRATION_INFEASIBLE",
        "per_seed": soft_rows,
        "max_D_TV_group_soft": float(soft_df["D_TV_group_soft"].max()),
        "max_D_TV_stratum_soft": float(soft_df["D_TV_stratum_soft"].max()),
        "max_D_TV_client_stratum_soft": float(soft_df["D_TV_client_stratum_soft"].max()),
        "max_marginal_residual": float(soft_df["max_marginal_residual"].max()),
        "unsupported_target_cell_count": int(soft_df["unsupported_target_cell_count"].sum()),
        "pi_identity_hash": calibrated[VALIDATION_SEEDS[0]]["pi_meta"]["hash"],
        "stratum_mapping_hash": stratum["identity"]["mapping_hash"],
    }
    dump_json(soft_audit, root / "outputs/e2_balanced_calibration/E2_BALANCED_SOFT_CALIBRATION_AUDIT.json")

    if not soft_pass:
        dump_json({
            "status": "BLOCKED_BALANCED_CALIBRATION_INFEASIBLE",
            "soft_audit": soft_audit,
        }, root / "outputs/e2_balanced_calibration/E2_STOP_STATUS.json")
        _finalize_blocked(root, horizon, uniq, stratum, soft_audit, None, None)
        return 0

    # Balanced hard pre-gate: 5 seeds × balanced × neutral profile, shared
    pre_rows = []
    balanced_diags = {}
    for seed in VALIDATION_SEEDS:
        streams = build_base_random_streams(
            seed, n_windows=NUM_WINDOWS, n_clients=8, max_risk_set=20,
        )
        cal_sched = calibrated[seed]["calibrated_schedule"]
        dest = root / "outputs/e2_balanced_calibration/traces" / str(seed) / "SHARED_BALANCED" / "balanced"
        result = generate_legal_horizon_mother_trace(
            seed=seed,
            profile_id=NEUTRAL_PROFILE,
            scenario_id="balanced",
            schedule=cal_sched,
            root=root,
            output_dir=dest,
            streams=streams,
        )
        diag = result["diagnostics"][100]
        ok, fails = _balanced_hard_pass(diag)
        balanced_diags[seed] = diag
        pre_rows.append({
            "seed": seed,
            "pass": ok,
            "failures": "|".join(fails),
            "D_TV_group": diag["D_TV_group"],
            "D_TV_true_stratum": diag["D_TV_true_stratum"],
            "tail_mass_ratio": diag["tail_mass_ratio"],
            "head_mass_ratio": diag["head_mass_ratio"],
        })
    pre_df = pd.DataFrame(pre_rows)
    pre_df.to_csv(root / "outputs/e2_balanced_calibration/E2_BALANCED_PRE_GATE_BY_SEED.csv", index=False)
    pre_pass = bool(pre_df["pass"].all())
    pre_summary = {
        "status": "PASS" if pre_pass else "BALANCED_PRE_GATE_FAIL",
        "pass_count": int(pre_df["pass"].sum()),
        "required": 5,
        "unique_balanced_traces": 5,
        "rows": pre_rows,
    }
    dump_json(pre_summary, root / "outputs/e2_balanced_calibration/E2_BALANCED_PRE_GATE_SUMMARY.json")

    if not pre_pass:
        dump_json({
            "status": "BALANCED_PRE_GATE_FAIL",
            "pre_summary": pre_summary,
        }, root / "outputs/e2_balanced_calibration/E2_STOP_STATUS.json")
        _finalize_blocked(root, horizon, uniq, stratum, soft_audit, pre_summary, None)
        return 0

    # Conditional 150 non-balanced traces
    matrix_status = "EXECUTED"
    unique_traces = 5
    gate_rows = []
    by_profile: dict[str, dict] = {p: {} for p in PROFILES}
    diagnostics_store: dict[str, dict] = {}

    for seed in VALIDATION_SEEDS:
        streams = build_base_random_streams(
            seed, n_windows=NUM_WINDOWS, n_clients=8, max_risk_set=20,
        )
        cal_sched = calibrated[seed]["calibrated_schedule"]
        shared_bal = balanced_diags[seed]
        for profile_id in PROFILES:
            # alias balanced
            diagnostics_store[f"{seed}/{profile_id}/balanced"] = shared_bal
            diags = {"balanced": shared_bal}
            for scenario_id in NON_BALANCED:
                dest = (
                    root / "outputs/e2_balanced_calibration/traces"
                    / str(seed) / profile_id / scenario_id
                )
                result = generate_legal_horizon_mother_trace(
                    seed=seed,
                    profile_id=profile_id,
                    scenario_id=scenario_id,
                    schedule=cal_sched,
                    root=root,
                    output_dir=dest,
                    streams=streams,
                )
                diags[scenario_id] = result["diagnostics"][100]
                diagnostics_store[f"{seed}/{profile_id}/{scenario_id}"] = diags[scenario_id]
                unique_traces += 1
            # symlink/copy shared balanced manifest pointer
            bal_dest = (
                root / "outputs/e2_balanced_calibration/traces"
                / str(seed) / profile_id / "balanced"
            )
            bal_dest.mkdir(parents=True, exist_ok=True)
            dump_json({
                "shared_balanced_trace": True,
                "source": f"{seed}/SHARED_BALANCED/balanced",
                "seed": seed,
                "profile_id": profile_id,
                "scenario_id": "balanced",
                "windows": NUM_WINDOWS,
            }, bal_dest / "manifest.json")
            dump_json(shared_bal, bal_dest / "group_mass_diagnostics_100.json")
            dump_json({
                "D_TV_true_stratum": shared_bal["D_TV_true_stratum"],
                "D_TV_true_stratum_exp_emp": shared_bal["D_TV_true_stratum_exp_emp"],
            }, bal_dest / "true_stratum_mass_diagnostics_100.json")
            evaluated = evaluate_seed_profile_gates(diags)
            by_profile[profile_id][seed] = evaluated
            gate_rows.append({
                "seed": seed,
                "profile_id": profile_id,
                "all_pass": bool(evaluated.get("profile_valid_seed")),
                "failures": "|".join(evaluated.get("failures") or []),
            })

    pd.DataFrame(gate_rows).to_csv(
        root / "outputs/e2_balanced_calibration/E2_PROFILE_GATE_BY_SEED.csv", index=False,
    )
    summary_rows = []
    valid = []
    registry = load_strength_profile_registry(root)["profiles"]
    for profile_id in PROFILES:
        ok = all(
            bool(by_profile[profile_id][s].get("profile_valid_seed"))
            for s in VALIDATION_SEEDS
        )
        if ok:
            valid.append(profile_id)
        summary_rows.append({
            "profile_id": profile_id,
            "seeds_pass_count": sum(
                1 for s in VALIDATION_SEEDS
                if by_profile[profile_id][s].get("profile_valid_seed")
            ),
            "all_seeds_pass": ok,
        })
    pd.DataFrame(summary_rows).to_csv(
        root / "outputs/e2_balanced_calibration/E2_PROFILE_GATE_SUMMARY.csv", index=False,
    )

    if not valid:
        selection = {
            "status": "NO_VALID_PROFILE_AFTER_BALANCED_CALIBRATION",
            "selected_profile_id": None,
            "valid_profiles": [],
            "unique_trace_count": unique_traces,
            "unique_balanced_traces": 5,
            "aliased_balanced_matrix_rows": 30,
        }
    else:
        selection = select_strength_profile(by_profile, registry)
        selection["unique_trace_count"] = unique_traces
        selection["unique_balanced_traces"] = 5
        selection["aliased_balanced_matrix_rows"] = 30
        if selection.get("status") == "SELECTED":
            selection["status"] = "PASS"
        pid = selection["selected_profile_id"]
        freeze = root / "configs/frozen/e2_balanced_calibration"
        freeze.mkdir(parents=True, exist_ok=True)
        prof = registry[pid]
        (freeze / "selected_strength_profile.yaml").write_text(
            yaml.safe_dump({"profile_id": pid, **prof}, sort_keys=False), encoding="utf-8",
        )
        dump_json({
            "profile_id": pid,
            "kappas": prof,
            "selection_hash": sha256_json(selection),
        }, freeze / "selected_strength_profile_identity.json")

    dump_json(selection, root / "outputs/e2_balanced_calibration/E2_PROFILE_SELECTION.json")

    window_sel = {
        "selected_windows": 100,
        "selection_basis": "LEGAL_CONTINUOUS_HORIZON",
        "statistical_stability_selection": "NOT_APPLICABLE",
        "candidate_200": "ILLEGAL",
        "candidate_300": "ILLEGAL",
        "window_selection_mode": "LEGALITY_FREEZE",
        "status": "PASS",
    }
    dump_json(window_sel, root / "outputs/e2_balanced_calibration/E2_WINDOW_SELECTION.json")
    (root / "configs/frozen/e2_legal_horizon/selected_window_length.yaml").write_text(
        yaml.safe_dump(window_sel, sort_keys=False), encoding="utf-8",
    )

    # Runtime plan
    runtime = {
        "selected_windows": 100,
        "strict_runs": 360,
        "extended_runs": 40,
        "total_runs": 400,
        "note": "Uses E1 100-window measured runtime; no x2/x3 for illegal 200/300.",
        "extended_methods": ["Local-Hajek", "TwoStage-Hajek"],
        "status": "PLANNED",
    }
    dump_json(runtime, root / "outputs/plans/E2_100_WINDOW_FORMAL_RUNTIME_ESTIMATE.json")
    (root / "outputs/plans/E2_100_WINDOW_FORMAL_RUNTIME_ESTIMATE.md").write_text(
        "# E2 100-Window Formal Runtime Estimate\n\n"
        f"- selected_windows: 100\n- total_runs: 400\n- strict: 360\n- extended: 40\n"
        f"- extended_methods: Local-Hajek, TwoStage-Hajek\n",
        encoding="utf-8",
    )

    dump_json({
        "status": selection.get("status"),
        "matrix_status": matrix_status,
        "unique_trace_count": unique_traces,
        "soft_status": soft_audit["status"],
        "pre_gate_status": pre_summary["status"],
    }, root / "outputs/e2_balanced_calibration/E2_STOP_STATUS.json")

    _finalize_blocked(
        root, horizon, uniq, stratum, soft_audit, pre_summary, selection,
        matrix_status=matrix_status, unique_traces=unique_traces, window_sel=window_sel,
    )
    print(json.dumps({
        "soft_status": soft_audit["status"],
        "pre_gate": pre_summary["status"],
        "selection": selection.get("status"),
        "unique_traces": unique_traces,
        "merged_strata": stratum["identity"]["stratum_count_merged"],
    }, indent=2))
    return 0


def _finalize_blocked(
    root, horizon, uniq, stratum, soft_audit, pre_summary, selection,
    matrix_status="BLOCKED", unique_traces=0, window_sel=None,
):
    window_sel = window_sel or {
        "selected_windows": 100,
        "selection_basis": "LEGAL_CONTINUOUS_HORIZON",
        "candidate_200": "ILLEGAL",
        "candidate_300": "ILLEGAL",
        "status": "PASS",
    }
    dump_json(window_sel, root / "outputs/e2_balanced_calibration/E2_WINDOW_SELECTION.json")
    if selection is None:
        selection = {
            "status": soft_audit.get("status") if soft_audit["status"] != "PASS"
            else (pre_summary or {}).get("status", "BLOCKED"),
            "selected_profile_id": None,
        }
        dump_json(selection, root / "outputs/e2_balanced_calibration/E2_PROFILE_SELECTION.json")
    front = [
        ("maximum legal windows", 105),
        ("selected legal windows", 100),
        ("source reuse count", uniq.get("source_reuse_count")),
        ("raw stratum count", stratum["identity"]["raw_stratum_count"]),
        ("merged stratum count", stratum["identity"]["stratum_count_merged"]),
        ("mixed-day count", stratum["identity"]["mixed_day_stratum_count"]),
        ("Balanced soft group TV", soft_audit.get("max_D_TV_group_soft")),
        ("Balanced soft stratum TV", soft_audit.get("max_D_TV_stratum_soft")),
        ("Balanced soft client-stratum TV", soft_audit.get("max_D_TV_client_stratum_soft")),
        ("Balanced 5-seed pass count", (pre_summary or {}).get("pass_count", 0)),
        ("profile matrix", matrix_status),
        ("selected profile", selection.get("selected_profile_id")),
        ("real Canary", "0/20"),
        ("formal runs", 0),
    ]
    report = _write_report(root, {
        "front_table": front,
        "sections": [
            ("1. Executive Summary", json.dumps(front, indent=2)),
            ("2. Invalid 300-Window Tombstone", "See E2_ILLEGAL_300_AND_UNCALIBRATED_BALANCED_TOMBSTONE.json"),
            ("3. Legal Horizon Audit", json.dumps(horizon, indent=2)),
            ("4. Source Uniqueness", json.dumps(uniq, indent=2)),
            ("5. Stratum Merge 100", json.dumps(stratum["summary"], indent=2)),
            ("6. Soft Calibration", json.dumps(soft_audit, indent=2)),
            ("7. Hard Pre-Gate", json.dumps(pre_summary or {}, indent=2)),
            ("8. Profile Selection", json.dumps(selection, indent=2)),
            ("9. Window Selection", json.dumps(window_sel, indent=2)),
            ("10. Stop Position", "seed 29001=0; canary=0/20; formal=0; E3-E9=NOT_STARTED"),
        ],
    })
    readme = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt"
    readme.write_text(
        "\n".join([
            PACKAGE,
            f"runtime_commit={_git_head()}",
            f"selected_windows=100",
            f"soft_status={soft_audit.get('status')}",
            f"pre_gate={(pre_summary or {}).get('status')}",
            f"profile_status={selection.get('status')}",
            f"unique_traces={unique_traces}",
            "real canary=0/20",
            "E3-E9=NOT_STARTED",
            "",
        ]),
        encoding="utf-8",
    )
    dump_json({
        "package": PACKAGE,
        "report": str(report.relative_to(root)),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }, root / "outputs/e2_balanced_calibration/E2_CONTEXT.json")


if __name__ == "__main__":
    raise SystemExit(main())
