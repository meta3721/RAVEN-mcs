#!/usr/bin/env python3
"""Generate hard empirical EventTraces, select profile/window, freeze identities."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.gates import (
    PROFILES,
    SCENARIOS,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
    select_strength_profile,
    select_window_length,
    window_prefix_stable,
)
from raven_mcs.e2.empirical.sampler import generate_empirical_mother_trace
from raven_mcs.e2.empirical.schedule import build_continuous_schedule
from raven_mcs.e2.identity import (
    load_e1_atomic_target_weights,
    load_e1_head_tail_mapping,
    load_e1_target_identity,
)
from raven_mcs.e2.scenario_generator import (
    load_scenario_direction_registry,
    load_strength_profile_registry,
)
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1"
PARENT_SOFT_COMMIT = "e56687813f2bcb919a9208391f68a4db3488602e"
USABLE_PARENT = "af226e9623cd82ff0b9c1a25d7e70ffe7948ab7b"
E1_COMMIT = "e8bd1fc777431c2609def257a04fba093f0daf24"
MAX_RISK_SET = 20
REQUIRED_TRACE_FILES = (
    "manifest.json",
    "resolved_config.yaml",
    "continuous_schedule.parquet",
    "opportunity_events.parquet",
    "observation_events.parquet",
    "usable_events.parquet",
    "hard_arrival_events.parquet",
    "empirical_atomic_mass_100.parquet",
    "empirical_atomic_mass_200.parquet",
    "empirical_atomic_mass_300.parquet",
    "expected_atomic_mass_100.parquet",
    "expected_atomic_mass_200.parquet",
    "expected_atomic_mass_300.parquet",
    "group_mass_diagnostics_100.json",
    "group_mass_diagnostics_200.json",
    "group_mass_diagnostics_300.json",
    "stratum_mass_diagnostics_100.json",
    "stratum_mass_diagnostics_200.json",
    "stratum_mass_diagnostics_300.json",
    "stdout.log",
    "stderr.log",
)


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def audit_registries(root: Path) -> tuple[dict, dict]:
    strength = load_strength_profile_registry(root)
    scenario = load_scenario_direction_registry(root)
    profiles = strength["profiles"]
    expected_profiles = {
        "PROFILE-S1": {"kappa_opp": 0.5, "kappa_p": 0.5, "kappa_q": 0.5},
        "PROFILE-S2": {"kappa_opp": 1.0, "kappa_p": 1.0, "kappa_q": 1.0},
        "PROFILE-S3": {"kappa_opp": 1.5, "kappa_p": 1.5, "kappa_q": 1.5},
        "PROFILE-S4": {"kappa_opp": 1.0, "kappa_p": 1.0, "kappa_q": 1.5},
        "PROFILE-S5": {"kappa_opp": 1.0, "kappa_p": 1.0, "kappa_q": 2.0},
        "PROFILE-S6": {"kappa_opp": 1.5, "kappa_p": 1.5, "kappa_q": 2.0},
    }
    profile_ok = set(profiles) == set(expected_profiles) and all(
        float(profiles[p][k]) == float(expected_profiles[p][k])
        for p in expected_profiles
        for k in ("kappa_opp", "kappa_p", "kappa_q")
    )
    strength_audit = {
        "profile_count": len(profiles),
        "values_unchanged": profile_ok,
        "registry_hash": sha256_json(strength),
        "status": "PASS" if profile_ok else "FAIL",
    }
    dump_json(strength_audit, root / "outputs/audits/E2_STRENGTH_PROFILE_REGISTRY_AUDIT.json")

    scen = scenario["scenarios"]
    expected_dirs = {
        "balanced": (0, 0, 0),
        "opportunity_only": (-1, 0, 0),
        "observation_only": (0, -1, 0),
        "usable_only": (0, 0, -1),
        "complete_aligned": (-1, -1, -1),
        "complete_counteracting": (-1, -1, 1),
    }
    dir_ok = set(scen) == set(expected_dirs) and all(
        (int(scen[s]["d_opp"]), int(scen[s]["d_p"]), int(scen[s]["d_q"])) == expected_dirs[s]
        for s in expected_dirs
    )
    scenario_audit = {
        "scenario_count": len(scen),
        "values_unchanged": dir_ok,
        "registry_hash": sha256_json(scenario),
        "status": "PASS" if dir_ok else "FAIL",
    }
    dump_json(scenario_audit, root / "outputs/audits/E2_SCENARIO_DIRECTION_REGISTRY_AUDIT.json")
    return strength_audit, scenario_audit


def write_parent_identity(root: Path, strength_hash: str, scenario_hash: str) -> None:
    identity = load_e1_target_identity(root)
    tail_score_hash = json.loads(
        (root / "configs/frozen/e2_numeric/atomic_tail_score_manifest.json").read_text(
            encoding="utf-8"
        )
    )["score_payload_hash"]
    dump_json({
        "protocol": PACKAGE,
        "parent_soft_round_commit": PARENT_SOFT_COMMIT,
        "usable_arrival_parent_commit": USABLE_PARENT,
        "e1_formal_commit": E1_COMMIT,
        "atomic_target_weight_hash": identity["atomic_target_weight_hash"],
        "supported_test_unit_hash": identity["supported_test_unit_hash"],
        "head_tail_mapping_hash": identity["head_tail_mapping_hash"],
        "atomic_tail_score_hash": tail_score_hash,
        "scenario_direction_registry_hash": scenario_hash,
        "strength_profile_registry_hash": strength_hash,
        "validation_seeds": list(VALIDATION_SEEDS),
        "candidate_size": MAX_RISK_SET,
        "arrival_mass_mode": "event_mass",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    }, root / "configs/frozen/e2_empirical/e2_numeric_parent_identity.json")


def generate_matrix(root: Path) -> dict:
    out_root = root / "outputs/e2_empirical/traces"
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {
        "trace_count": 0,
        "trace_failure_count": 0,
        "missing_required_file_count": 0,
        "manifests": {},
        "diagnostics": {},
        "base_stream_hashes": {},
        "schedule_hashes": {},
        "schedule_audits": {},
        "opportunity_riskset_diff": {},
    }
    schedule_audits = []
    for seed in VALIDATION_SEEDS:
        streams = build_base_random_streams(
            seed, n_windows=300, n_clients=8, max_risk_set=MAX_RISK_SET,
        )
        schedule = build_continuous_schedule(
            seed,
            schedule_uniforms=streams["base_client_window_schedule"],
            root=root,
        )
        summary["base_stream_hashes"][str(seed)] = streams["base_random_stream_hash"]
        summary["schedule_hashes"][str(seed)] = schedule["schedule_hash"]
        summary["schedule_audits"][str(seed)] = schedule["audit"]
        schedule_audits.append(schedule["audit"])
        selected_sets: dict[str, set] = {}
        for profile_id in PROFILES:
            for scenario_id in SCENARIOS:
                key = f"{seed}/{profile_id}/{scenario_id}"
                dest = out_root / str(seed) / profile_id / scenario_id
                try:
                    result = generate_empirical_mother_trace(
                        seed=seed,
                        profile_id=profile_id,
                        scenario_id=scenario_id,
                        root=root,
                        output_dir=dest,
                        streams=streams,
                        schedule=schedule,
                    )
                    missing = [f for f in REQUIRED_TRACE_FILES if not (dest / f).is_file()]
                    if missing:
                        summary["missing_required_file_count"] += 1
                        raise RuntimeError(f"missing files: {missing}")
                    summary["trace_count"] += 1
                    summary["manifests"][key] = result["manifest"]
                    summary["diagnostics"][key] = result["diagnostics"]
                    if scenario_id in {"balanced", "opportunity_only"}:
                        selected_sets[scenario_id] = result["opportunity_selected_set"]
                except Exception as exc:  # noqa: BLE001
                    summary["trace_failure_count"] += 1
                    summary["diagnostics"][key] = {"error": str(exc)}
            # Per-profile balanced vs opportunity risk-set difference.
            bal = selected_sets.get("balanced", set())
            opp = selected_sets.get("opportunity_only", set())
            diff = len(bal.symmetric_difference(opp))
            summary["opportunity_riskset_diff"][f"{seed}/{profile_id}"] = {
                "balanced_selected_count": len(bal),
                "opportunity_only_selected_count": len(opp),
                "balanced_vs_opportunity_event_difference_count": diff,
                "status": "PASS" if diff > 0 else "FAIL",
            }
            selected_sets = {}

    schedule_audit = {
        "protocol": PACKAGE,
        "seeds": list(VALIDATION_SEEDS),
        "per_seed": summary["schedule_audits"],
        "block_hashes_all_equal_any": any(
            a.get("block_hashes_all_equal") for a in schedule_audits
        ),
        "min_unique_window_payload_ratio": min(
            float(a["unique_window_payload_ratio"]) for a in schedule_audits
        ),
        "schedule_uniforms_used_all": all(
            int(a["schedule_uniforms_used_count"]) > 0 for a in schedule_audits
        ),
        "chronological_order_status": (
            "PASS"
            if all(a.get("chronological_order_status") == "PASS" for a in schedule_audits)
            else "FAIL"
        ),
        "status": (
            "PASS"
            if (
                not any(a.get("block_hashes_all_equal") for a in schedule_audits)
                and min(float(a["unique_window_payload_ratio"]) for a in schedule_audits) >= 0.80
                and all(int(a["schedule_uniforms_used_count"]) > 0 for a in schedule_audits)
            )
            else "FAIL"
        ),
    }
    dump_json(schedule_audit, root / "outputs/audits/E2_300_WINDOW_SCHEDULE_NONREPETITION_AUDIT.json")
    dump_json(
        summary["opportunity_riskset_diff"],
        root / "outputs/audits/E2_OPPORTUNITY_RISKSET_DIFFERENCE_AUDIT.json",
    )
    path = root / "outputs/e2_empirical/E2_EMPIRICAL_TRACE_MATRIX_SUMMARY.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def run_profile_selection(root: Path, matrix: dict) -> dict:
    strength = load_strength_profile_registry(root)
    gate_rows = []
    profile_seed_results: dict[str, dict[int, dict]] = {p: {} for p in PROFILES}
    for profile_id in PROFILES:
        for seed in VALIDATION_SEEDS:
            by_scen = {
                scen: matrix["diagnostics"][f"{seed}/{profile_id}/{scen}"][300]
                for scen in SCENARIOS
            }
            evaluated = evaluate_seed_profile_gates(by_scen)
            profile_seed_results[profile_id][seed] = evaluated
            for scen in SCENARIOS:
                d = by_scen[scen]
                gate_rows.append({
                    "seed": seed,
                    "profile_id": profile_id,
                    "scenario_id": scen,
                    "D_TV_group": d["D_TV_group"],
                    "D_TV_stratum": d["D_TV_stratum"],
                    "tail_mass_ratio": d["tail_mass_ratio"],
                    "head_mass_ratio": d["head_mass_ratio"],
                    "D_TV_group_exp_emp": d["D_TV_group_exp_emp"],
                    "D_TV_stratum_exp_emp": d["D_TV_stratum_exp_emp"],
                    "cancellation_group_TV": d["cancellation_group_TV"],
                    "realized_observation_rate": d["realized_observation_rate"],
                    "realized_usable_rate": d["realized_usable_rate"],
                    "profile_valid_seed": evaluated["profile_valid_seed"],
                    "failures": "|".join(evaluated["failures"]),
                })
    gate_df = pd.DataFrame(gate_rows)
    out = root / "outputs/e2_empirical"
    gate_df.to_csv(out / "E2_EMPIRICAL_PROFILE_GATE_BY_SEED.csv", index=False)
    summary_rows = []
    for profile_id in PROFILES:
        valid = all(
            profile_seed_results[profile_id][s]["profile_valid_seed"]
            for s in VALIDATION_SEEDS
        )
        summary_rows.append({
            "profile_id": profile_id,
            "profile_valid": valid,
            "max_seed_aligned_dtv_group": max(
                profile_seed_results[profile_id][s]["aligned_dtv_group"]
                for s in VALIDATION_SEEDS
            ),
            "kappa_sum": (
                float(strength["profiles"][profile_id]["kappa_opp"])
                + float(strength["profiles"][profile_id]["kappa_p"])
                + float(strength["profiles"][profile_id]["kappa_q"])
            ),
        })
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(out / "E2_EMPIRICAL_PROFILE_GATE_SUMMARY.csv", index=False)
    selection = select_strength_profile(profile_seed_results, strength["profiles"])
    selection["validation_seed_list"] = list(VALIDATION_SEEDS)
    selection["profile_registry_hash"] = sha256_json(strength)
    selection["prior_PROFILE_S2_tombstoned"] = True
    selection["revalidated_on_hard_empirical"] = True
    dump_json(selection, out / "E2_EMPIRICAL_PROFILE_SELECTION.json")
    pd.DataFrame([{
        "seed": r["seed"],
        "profile_id": r["profile_id"],
        "scenario_id": r["scenario_id"],
        "D_TV_group_exp_emp": r["D_TV_group_exp_emp"],
        "D_TV_stratum_exp_emp": r["D_TV_stratum_exp_emp"],
        "D_TV_group": r["D_TV_group"],
    } for r in gate_rows]).to_csv(
        out / "E2_EXPECTED_HARD_EMPIRICAL_MASS_AUDIT.csv", index=False,
    )
    return {
        "selection": selection,
        "profile_seed_results": profile_seed_results,
        "gate_df": gate_df,
        "summary_df": summary_df,
    }


def risk_visibility_audit(root: Path, selected_profile: str) -> pd.DataFrame:
    atomic = load_e1_atomic_target_weights(root)
    head_tail = load_e1_head_tail_mapping(root)
    diff = pd.read_parquet(root / "configs/frozen/e2_numeric/group_calibration_difficulty.parquet")
    gmap = {
        int(r.target_group_main): float(r.calibration_prediction_mse)
        for r in diff.itertuples(index=False)
    }
    unit_ids = atomic["unit_id"].astype(str).tolist()
    target = atomic["target_weight"].to_numpy(dtype=np.float64)
    groups = (
        head_tail.set_index("unit_id").loc[unit_ids, "target_group_main"].to_numpy(dtype=int)
    )
    r_i = np.asarray([gmap[int(g)] for g in groups], dtype=np.float64)
    r_mu = float(np.sum(target * r_i))
    rows = []
    for seed in VALIDATION_SEEDS:
        for scen in SCENARIOS:
            emp_path = (
                root / "outputs/e2_empirical/traces" / str(seed) / selected_profile / scen
                / "empirical_atomic_mass_300.parquet"
            )
            emp = pd.read_parquet(emp_path)["empirical_arrival_mass"].to_numpy()
            r_rho = float(np.sum(emp * r_i))
            mis = r_mu - r_rho
            rows.append({
                "seed": seed,
                "profile_id": selected_profile,
                "scenario_id": scen,
                "R_mu_profile": r_mu,
                "R_rho_profile": r_rho,
                "profile_misalignment": mis,
                "sign": "positive" if mis > 0 else ("negative" if mis < 0 else "zero"),
                "used_for_selection": False,
                "uses_test_rmse": False,
            })
    frame = pd.DataFrame(rows)
    frame.to_csv(root / "outputs/e2_empirical/E2_RISK_VISIBILITY_AUDIT.csv", index=False)
    return frame


def run_window_selection(root: Path, selected_profile: str, matrix: dict) -> dict:
    stab_rows = []
    seed_stability: dict[int, dict[int, bool]] = {}
    for seed in VALIDATION_SEEDS:
        metrics_by_length = {100: {}, 200: {}, 300: {}}
        for scen in SCENARIOS:
            diag = matrix["diagnostics"][f"{seed}/{selected_profile}/{scen}"]
            for length in (100, 200, 300):
                metrics_by_length[length][scen] = diag[length]
        seed_stability[seed] = {}
        for length in (100, 200, 300):
            ok, worst = window_prefix_stable(metrics_by_length, length=length)
            seed_stability[seed][length] = ok if length != 300 else True
            stab_rows.append({
                "seed": seed,
                "profile_id": selected_profile,
                "windows": length,
                "stable": seed_stability[seed][length],
                **{f"worst_{k}": v for k, v in worst.items()},
            })
    out = root / "outputs/e2_empirical"
    pd.DataFrame(stab_rows).to_csv(out / "E2_EMPIRICAL_WINDOW_STABILITY_BY_SEED.csv", index=False)
    selection = select_window_length(seed_stability)
    pd.DataFrame([{
        "windows": length,
        "status": selection[f"candidate_status_{length}"],
        "seeds_pass": sum(1 for s in VALIDATION_SEEDS if seed_stability[s][length]),
    } for length in (100, 200, 300)]).to_csv(
        out / "E2_EMPIRICAL_WINDOW_STABILITY_SUMMARY.csv", index=False,
    )
    manifests = {
        k: v for k, v in matrix["manifests"].items() if f"/{selected_profile}/" in k
    }
    selection["validation_seed_list"] = list(VALIDATION_SEEDS)
    selection["selected_profile_id"] = selected_profile
    selection["trace_manifest_hashes"] = {k: sha256_json(v) for k, v in manifests.items()}
    dump_json(selection, out / "E2_EMPIRICAL_WINDOW_LENGTH_SELECTION.json")
    return selection


def freeze_selected(
    root: Path,
    profile_selection: dict,
    window_selection: dict,
    strength_hash: str,
) -> None:
    frozen = root / "configs/frozen/e2_empirical"
    frozen.mkdir(parents=True, exist_ok=True)
    profile_id = profile_selection["selected_profile_id"]
    profiles = load_strength_profile_registry(root)["profiles"][profile_id]
    commit = _git_head()
    yaml_profile = {
        "selected_profile_id": profile_id,
        "kappa_opp": float(profiles["kappa_opp"]),
        "kappa_p": float(profiles["kappa_p"]),
        "kappa_q": float(profiles["kappa_q"]),
        "selection_rule": profile_selection["selection_rule"],
        "validation_seed_list": list(VALIDATION_SEEDS),
        "revalidated_on_hard_empirical": True,
        "prior_soft_PROFILE_S2_not_reused_without_revalidation": True,
        "formal": False,
    }
    (frozen / "selected_strength_profile.yaml").write_text(
        yaml.safe_dump(yaml_profile, sort_keys=False), encoding="utf-8",
    )
    dump_json({
        **yaml_profile,
        "all_gate_status": "PASS",
        "profile_registry_hash": strength_hash,
        "selected_payload_hash": sha256_json(profiles),
        "frozen_at_commit": commit,
        "selection_status": "REFROZEN",
    }, frozen / "selected_strength_profile_identity.json")

    yaml_window = {
        "selected_windows": int(window_selection["selected_windows"]),
        "candidate_status_100": window_selection["candidate_status_100"],
        "candidate_status_200": window_selection["candidate_status_200"],
        "candidate_status_300": window_selection["candidate_status_300"],
        "validation_seed_list": list(VALIDATION_SEEDS),
        "selected_profile_id": profile_id,
        "prior_soft_200_not_preferred": True,
        "formal": False,
    }
    (frozen / "selected_window_length.yaml").write_text(
        yaml.safe_dump(yaml_window, sort_keys=False), encoding="utf-8",
    )
    dump_json({
        **yaml_window,
        "stability_thresholds": {
            "delta_D_TV_group": 0.02,
            "delta_D_TV_stratum": 0.03,
            "delta_tail_ratio": 0.05,
            "delta_head_ratio": 0.05,
            "delta_observation_rate": 0.02,
            "delta_usable_rate": 0.03,
            "delta_active_window_rate": 0.02,
            "delta_group_exp_emp": 0.02,
            "delta_stratum_exp_emp": 0.03,
        },
        "selected_profile_hash": sha256_json(profiles),
        "trace_manifest_hashes": window_selection.get("trace_manifest_hashes", {}),
        "frozen_at_commit": commit,
        "selection_status": "REFROZEN",
    }, frozen / "selected_window_length_identity.json")


def write_runtime_estimate(root: Path, selected_windows: int) -> dict:
    e1 = {
        "flamf_timealign_adapted": 41.5501,
        "fedavg_window": 43.7399,
        "fedasync_window": 42.3753,
    }
    e1_est = {
        "local_hajek": {"seconds_per_100": 35.0, "source": "ESTIMATED_FROM_E1_ORDER"},
        "twostage_hajek": {"seconds_per_100": 38.0, "source": "ESTIMATED_FROM_E1_ORDER"},
    }
    scale = selected_windows / 100.0
    strict_runs = 1 * 6 * 3 * 20
    extended_runs = 1 * 1 * 2 * 20
    strict_seconds = sum(e1[m] * scale * (1 * 6 * 20) for m in e1)
    extended_seconds = (e1["fedavg_window"] + e1["fedasync_window"]) * scale * 20
    total_seconds = strict_seconds + extended_seconds
    margin = 1.20
    payload = {
        "selected_windows": selected_windows,
        "strict_primary_runs": strict_runs,
        "extended_diagnostic_runs": extended_runs,
        "total_runs": strict_runs + extended_runs,
        "e1_runtime_per_100_windows_sec": e1,
        "estimated_baselines": e1_est,
        "strict_serial_cpu_hours": (strict_seconds * margin) / 3600.0,
        "extended_serial_cpu_hours": (extended_seconds * margin) / 3600.0,
        "total_serial_cpu_hours": (total_seconds * margin) / 3600.0,
        "wall_hours_2_workers": (total_seconds * margin) / 3600.0 / 2.0,
        "wall_hours_4_workers": (total_seconds * margin) / 3600.0 / 4.0,
        "wall_hours_8_workers": (total_seconds * margin) / 3600.0 / 8.0,
        "safety_margin": 0.20,
        "estimated_disk_gb": (180 * 12 + 400 * 5) / 1024.0 * margin,
        "no_runs_executed_this_round": True,
        "local_twostage_not_faked_as_fedavg": True,
    }
    dump_json(payload, root / "outputs/plans/E2_FORMAL_RUNTIME_AND_STORAGE_ESTIMATE.json")
    (root / "outputs/plans/E2_FORMAL_RUNTIME_AND_STORAGE_ESTIMATE.md").write_text(
        "\n".join([
            "# E2 Formal Runtime and Storage Estimate (Empirical Refreeze)",
            "",
            f"- selected_windows: {selected_windows}",
            f"- total serial CPU hours (20% margin): {payload['total_serial_cpu_hours']:.2f}",
            f"- 4-worker wall hours: {payload['wall_hours_4_workers']:.2f}",
            "",
            "No formal runs executed in this round.",
            "Local/TwoStage times are ESTIMATED_FROM_E1_ORDER, not copied FedAvg.",
            "",
        ]),
        encoding="utf-8",
    )
    return payload


def write_report(root: Path, ctx: dict) -> Path:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading("E2 Empirical EventTrace and Profile Refreeze R1 Report", 0)
    sections = [
        ("Executive Summary", f"Status={ctx['status']}; selected_profile={ctx['selected_profile']}; selected_windows={ctx['selected_windows']}."),
        ("Prior Soft Selection Tombstone", "PROFILE-S2 / 200 tombstoned; soft expected mislabeled as empirical."),
        ("Hard EventTrace Pipeline", "Opportunity→Observation→Usable→Hard arrival; cand=20; continuous non-repeating schedule."),
        ("180 Validation Trace Completion", f"trace_count={ctx['trace_count']}; failures={ctx['trace_failures']}."),
        ("Empirical Profile Gates H1-H6", str(ctx["profile_summary"])),
        ("Selected Strength Profile", f"{ctx['selected_profile']} kappas={ctx['kappas']}"),
        ("Selected Window Length", str(ctx["selected_windows"])),
        ("Runtime Estimate", f"serial CPU hours={ctx['runtime']['total_serial_cpu_hours']:.2f}"),
        ("Stop Position", "READY_FOR_REAL_RUNNER_CANARY; Canary 0/20; formal 0; E3-E9 NOT_STARTED."),
    ]
    for title, body in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(body)
    out = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def main() -> int:
    root = ROOT
    for d in (
        "outputs/e2_empirical",
        "outputs/audits",
        "outputs/plans",
        "configs/frozen/e2_empirical",
    ):
        (root / d).mkdir(parents=True, exist_ok=True)

    tombstone = root / "outputs/audits/E2_INVALID_PRIOR_SELECTION_TOMBSTONE.json"
    if not tombstone.is_file():
        raise SystemExit("missing prior selection tombstone")

    strength_audit, scenario_audit = audit_registries(root)
    if strength_audit["status"] != "PASS" or scenario_audit["status"] != "PASS":
        raise SystemExit("registry audit failed")
    write_parent_identity(
        root, strength_audit["registry_hash"], scenario_audit["registry_hash"],
    )
    matrix = generate_matrix(root)
    if int(matrix["trace_count"]) != 180 or int(matrix["trace_failure_count"]) != 0:
        dump_json({
            "status": "TRACE_MATRIX_FAIL",
            "trace_count": matrix["trace_count"],
            "trace_failure_count": matrix["trace_failure_count"],
        }, root / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json")
        print("TRACE_MATRIX_FAIL")
        return 2

    profile_pack = run_profile_selection(root, matrix)
    selection = profile_pack["selection"]
    if selection["status"] != "SELECTED":
        print("NO_VALID_EMPIRICAL_DISTRIBUTION_PROFILE")
        return 3

    selected_profile = selection["selected_profile_id"]
    risk_visibility_audit(root, selected_profile)
    window_selection = run_window_selection(root, selected_profile, matrix)
    freeze_selected(
        root, selection, window_selection, strength_audit["registry_hash"],
    )
    runtime = write_runtime_estimate(root, int(window_selection["selected_windows"]))
    profiles = load_strength_profile_registry(root)["profiles"][selected_profile]
    ctx = {
        "status": "PASS",
        "selected_profile": selected_profile,
        "selected_windows": window_selection["selected_windows"],
        "trace_count": matrix["trace_count"],
        "trace_failures": matrix["trace_failure_count"],
        "profile_summary": profile_pack["summary_df"].to_dict(orient="records"),
        "kappas": profiles,
        "window_status": {
            "100": window_selection["candidate_status_100"],
            "200": window_selection["candidate_status_200"],
            "300": window_selection["candidate_status_300"],
        },
        "runtime": runtime,
        "candidate_size": MAX_RISK_SET,
    }
    report = write_report(root, ctx)
    dump_json(ctx, root / "outputs/e2_empirical/E2_EMPIRICAL_CONTEXT.json")
    print(json.dumps({
        "status": "PASS",
        "selected_profile": selected_profile,
        "selected_windows": window_selection["selected_windows"],
        "trace_count": matrix["trace_count"],
        "report": str(report),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
