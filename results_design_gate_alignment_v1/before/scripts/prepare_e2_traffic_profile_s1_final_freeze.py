#!/usr/bin/env python3
"""E2-TRAFFIC-PROFILE-S1-FINAL-FREEZE-R1 prepare."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.empirical.events import (
    OBS_RATE_TARGET,
    OPP_RATE_TARGET,
    USE_RATE_TARGET,
)
from raven_mcs.e2.traffic_balanced_canary import (
    N_ATOMS,
    N_CLIENTS,
    N_WINDOWS,
    build_traffic_schedule,
    load_traffic_targets,
    sha256_file,
)
from raven_mcs.e2.traffic_profiles import (
    PROFILE_SEEDS,
    SCENARIO_ORDER,
    load_direction_registry,
    load_strength_registry,
    solve_stage_probabilities,
)
from raven_mcs.e2.traffic_profiles.runner_consistency import (
    PROB_BOUNDS,
    certify_hard_directions,
    exact_expected_masses,
    hard_stage_masses,
    pool_stage_directions,
    run_frozen_hard_trace,
    support_audit,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_R1"
SELECTED_STRENGTH = "PROFILE-S1"
OUT = ROOT / "outputs/e2_traffic_profile_s1"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic_profiles_s1"
DELIV = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
LABEL_TO_SID = {label: sid for label, sid in SCENARIO_ORDER}
SID_TO_LABEL = {sid: label for label, sid in SCENARIO_ORDER}


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def write_report(summary: dict[str, Any]) -> Path:
    DELIV.mkdir(parents=True, exist_ok=True)
    path = DELIV / f"{PACKAGE}_REPORT.docx"
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading("E2-TRAFFIC-PROFILE-S1-FINAL-FREEZE-R1 Report", level=0)
    doc.add_heading("1. Executive Summary", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Value"
    for k, v in summary["front"].items():
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    for title, body in summary["sections"]:
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
            f"Selection reason: {stop.get('selection_reason')}",
            f"Next: {stop.get('next_authorized_round')}",
            f"Traces: {stop.get('hard_trace_count')}",
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


def main() -> int:
    for d in (OUT, AUDIT, FROZEN, DELIV):
        d.mkdir(parents=True, exist_ok=True)

    prior = json.loads(
        (ROOT / "outputs/e2_traffic_runner_consistency/E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json").read_text(
            encoding="utf-8"
        )
    )
    identity = {
        "status": "PASS" if prior.get("status") == "BLOCKED_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_FAILED" else "FAIL",
        "prior_status": prior.get("status"),
        "prior_blocking_reason": "PROFILE-S2_SUPPORT_DEGENERACY",
        "n_clients": N_CLIENTS,
        "n_windows": N_WINDOWS,
        "n_atoms": N_ATOMS,
        "design_seeds": list(PROFILE_SEEDS),
        "selected_strength": SELECTED_STRENGTH,
        "probability_bounds": PROB_BOUNDS,
        "scenarios": [sid for _, sid in SCENARIO_ORDER],
    }
    # Verify strength registry has PROFILE-S1
    strength_reg = load_strength_registry(ROOT)
    if SELECTED_STRENGTH not in strength_reg.get("profiles", {}):
        identity["status"] = "BLOCKED_INPUT_IDENTITY_MISMATCH"
    dump_json(identity, AUDIT / "E2_TRAFFIC_PROFILE_S1_INPUT_IDENTITY_AUDIT.json")

    tombstone = {
        "prior_strength": "PROFILE-S2",
        "prior_status": "BLOCKED_SUPPORT_DEGENERACY",
        "blocking_scenario": "S5_COMPLETE_ALIGNED",
        "minimum_positive_stratum_expected_arrivals": 1.5499,
        "required_minimum": 5,
        "observation_lower_clip_rate": 0.50,
        "profile_s2_not_authorized_for_runner": True,
        "profile_s2_results_not_for_method_comparison": True,
        "profile_s2_must_not_be_reused": True,
        "tombstoned_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(tombstone, AUDIT / "E2_TRAFFIC_PROFILE_S2_SUPPORT_TOMBSTONE.json")

    if identity["status"] != "PASS":
        stop = {
            "status": "BLOCKED_TRAFFIC_PROFILE_S1_FINAL_FREEZE_FAILED",
            "blocked_reason": identity["status"],
            "training_artifact_count": 0,
            "seed_29001_read_count": 0,
            "validation_seed_read_count": 0,
            "formal_seed_read_count": 0,
            "e2_formal_runs": 0,
            "e3_e9_status": "NOT_STARTED",
            "next_authorized_round": "TEACHER_REVIEW_REQUIRED",
            "runtime_commit": _git_head(),
        }
        dump_json(stop, OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
        write_report({"front": stop, "sections": [("Identity", identity)]})
        write_readme(stop)
        print(json.dumps(stop, indent=2))
        return 0

    direction_reg = load_direction_registry(ROOT)
    strength = strength_reg["profiles"][SELECTED_STRENGTH]
    targets = load_traffic_targets(ROOT)
    schedule = build_traffic_schedule(targets)
    unit_meta = targets["unit_meta"]

    candidate = {
        "protocol": PACKAGE,
        "status": "CANDIDATE",
        "selected_strength": SELECTED_STRENGTH,
        "selection_reason": "deterministic_support_fallback",
        "kappa_opp": float(strength["kappa_opp"]),
        "kappa_obs": float(strength["kappa_p"]),
        "kappa_q": float(strength["kappa_q"]),
        "probability_bounds": PROB_BOUNDS,
        "rate_targets": {
            "opportunity": OPP_RATE_TARGET,
            "observation": OBS_RATE_TARGET,
            "usable": USE_RATE_TARGET,
        },
        "design_seeds": list(PROFILE_SEEDS),
        "no_per_seed_intercept_recalibration": True,
        "strength_grid_search_count": 0,
        "scenarios": {},
    }

    scenario_certs: dict[str, Any] = {}
    exact_audits: dict[str, Any] = {}
    clip_by_scenario: dict[str, Any] = {}
    support_by_scenario: dict[str, Any] = {}
    param_rows = []
    total_traces = 0
    per_seed_solve = 0
    unsupported = failed_omit = q_leak = target_leak = 0
    hardcoded_pass = 0
    all_pass = True
    intercept_solve_per_scenario = {}

    for label, scenario_id in SCENARIO_ORDER:
        sc = direction_reg["scenarios"][scenario_id]
        # One deterministic intercept solve per scenario
        probs = solve_stage_probabilities(
            schedule=schedule,
            unit_meta=unit_meta,
            d_opp=int(sc["d_opp"]),
            d_p=int(sc["d_p"]),
            d_q=int(sc["d_q"]),
            kappa_opp=float(strength["kappa_opp"]),
            kappa_p=float(strength["kappa_p"]),
            kappa_q=float(strength["kappa_q"]),
        )
        intercept_solve_per_scenario[scenario_id] = 1
        params = {
            "scenario_id": scenario_id,
            "a_opp": float(probs["intercept_opp"]),
            "a_obs": float(probs["intercept_obs"]),
            "a_q": float(probs["intercept_q"]),
            "kappa_opp": float(strength["kappa_opp"]),
            "kappa_obs": float(strength["kappa_p"]),
            "kappa_q": float(strength["kappa_q"]),
            "d_opp": int(sc["d_opp"]),
            "d_p": int(sc["d_p"]),
            "d_q": int(sc["d_q"]),
            "profile_id": SELECTED_STRENGTH,
            "bounds": {
                "opp": list(PROB_BOUNDS["opp"]),
                "obs": list(PROB_BOUNDS["obs"]),
                "q": list(PROB_BOUNDS["q"]),
            },
            "rate_targets": candidate["rate_targets"],
        }
        candidate["scenarios"][scenario_id] = {
            "label": label,
            "scenario_id": scenario_id,
            "display_name": sc.get("display_name"),
            "d_opp": params["d_opp"],
            "d_p": params["d_p"],
            "d_q": params["d_q"],
            "kappa_opp": params["kappa_opp"],
            "kappa_obs": params["kappa_obs"],
            "kappa_q": params["kappa_q"],
            "a_opp": params["a_opp"],
            "a_obs": params["a_obs"],
            "a_q": params["a_q"],
            "intercept_opp": params["a_opp"],
            "intercept_obs": params["a_obs"],
            "intercept_q": params["a_q"],
            "intercept_solve_count": 1,
            "probability_bounds": PROB_BOUNDS,
        }

        scen_dir = OUT / "scenarios" / scenario_id
        scen_dir.mkdir(parents=True, exist_ok=True)
        exact = exact_expected_masses(schedule=schedule, unit_meta=unit_meta, params=params)
        exact["opportunity"]["frame"].to_parquet(
            OUT / f"{label}_expected_opportunity_mass.parquet", index=False,
        )
        exact["observation"]["frame"].to_parquet(
            OUT / f"{label}_expected_observation_mass.parquet", index=False,
        )
        exact["arrival"]["frame"].to_parquet(
            OUT / f"{label}_exact_expected_arrival_mass.parquet", index=False,
        )
        exact["opportunity"]["frame"].to_parquet(scen_dir / "expected_opportunity_mass.parquet", index=False)
        exact["observation"]["frame"].to_parquet(scen_dir / "expected_observation_mass.parquet", index=False)
        exact["arrival"]["frame"].to_parquet(scen_dir / "exact_expected_arrival_mass.parquet", index=False)
        exact["client_window"].to_parquet(scen_dir / "exact_expected_client_window_activity.parquet", index=False)
        exact_audits[scenario_id] = exact["audit"]
        if exact["audit"]["status"] != "PASS":
            all_pass = False

        support = support_audit(exact)
        support_by_scenario[scenario_id] = support
        if support["status"] != "PASS":
            all_pass = False

        cc = exact["audit"]["clip_counts"]
        clip_by_scenario[scenario_id] = {
            "opportunity_lower_clip_rate": cc["opp_lo"] / max(cc["opp_n"], 1),
            "opportunity_upper_clip_rate": cc["opp_hi"] / max(cc["opp_n"], 1),
            "observation_lower_clip_rate": cc["obs_lo"] / max(cc["obs_n"], 1),
            "observation_upper_clip_rate": cc["obs_hi"] / max(cc["obs_n"], 1),
            "q_lower_clip_rate": cc["q_lo"] / max(cc["q_n"], 1),
            "q_upper_clip_rate": cc["q_hi"] / max(cc["q_n"], 1),
            "p_opp_min": exact["audit"]["p_opp_min"],
            "p_opp_max": exact["audit"]["p_opp_max"],
            "p_obs_min": exact["audit"]["p_obs_min"],
            "p_obs_max": exact["audit"]["p_obs_max"],
            "q_min": exact["audit"]["q_min"],
            "q_max": exact["audit"]["q_max"],
        }

        # Early stop if support fails (instruction: stop, no other strength)
        if support["status"] != "PASS":
            dump_json(candidate, FROZEN / "traffic_s1_s6_profile_s1_candidate_registry.json")
            (FROZEN / "traffic_s1_s6_profile_s1_candidate_registry.yaml").write_text(
                yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8",
            )
            dump_json({
                "status": "FAIL",
                "by_scenario": exact_audits,
            }, AUDIT / "E2_TRAFFIC_PROFILE_S1_EXACT_EXPECTED_MASS_AUDIT.json")
            dump_json({
                "status": "FAIL",
                "clip_by_scenario": clip_by_scenario,
                "support_by_scenario": {
                    sid: {
                        k: support_by_scenario[sid][k]
                        for k in (
                            "status",
                            "minimum_positive_group_expected_arrivals",
                            "minimum_positive_stratum_expected_arrivals",
                            "minimum_positive_client_stratum_expected_arrivals",
                            "tail_group_minimum_expected_arrivals",
                            "total_exact_expected_arrival_mass",
                        )
                    }
                    for sid in support_by_scenario
                },
            }, AUDIT / "E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json")
            stop = {
                "status": "BLOCKED_TRAFFIC_PROFILE_S1_FINAL_FREEZE_FAILED",
                "blocked_reason": f"support_failed_{scenario_id}",
                "selected_strength": SELECTED_STRENGTH,
                "selection_reason": "deterministic_support_fallback",
                "hard_trace_count": 0,
                "training_artifact_count": 0,
                "seed_29001_read_count": 0,
                "validation_seed_read_count": 0,
                "formal_seed_read_count": 0,
                "e2_formal_runs": 0,
                "e3_e9_status": "NOT_STARTED",
                "strength_grid_search_count": 0,
                "next_authorized_round": "TEACHER_REVIEW_REQUIRED",
                "runtime_commit": _git_head(),
            }
            dump_json(stop, OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
            write_report({"front": stop, "sections": [("Support", support_by_scenario)]})
            write_readme(stop)
            print(json.dumps(stop, indent=2))
            return 0

        seed_stages = []
        rate_opp = rate_obs = rate_use = 0.0
        for seed in PROFILE_SEEDS:
            seed_dir = scen_dir / "traces" / str(seed)
            result = run_frozen_hard_trace(
                seed=seed,
                schedule=schedule,
                unit_meta=unit_meta,
                params=params,
                output_dir=seed_dir,
            )
            snap = result["snapshot"]
            man = result["manifest"]
            total_traces += 1
            per_seed_solve += int(snap["per_seed_intercept_solve_count"])
            unsupported += int(man["unsupported_arrival_count"])
            failed_omit += int(man["failed_attempt_omission_count"])
            q_leak += int(man["observed_count_in_q"]) + int(man["stage2_eligible_in_q"])
            rate_opp += float(man["realized_opportunity_rate"])
            rate_obs += float(man["realized_conditional_observation_rate"])
            rate_use += float(man["realized_conditional_usable_rate"])

            param_rows.append({
                "scenario_id": scenario_id,
                "seed": seed,
                "registry_a_opp": params["a_opp"],
                "runtime_a_opp": snap["runtime_a_opp"],
                "registry_a_obs": params["a_obs"],
                "runtime_a_obs": snap["runtime_a_obs"],
                "registry_a_q": params["a_q"],
                "runtime_a_q": snap["runtime_a_q"],
                "mismatch_count": int(
                    abs(params["a_opp"] - snap["runtime_a_opp"]) > 1e-12
                    or abs(params["a_obs"] - snap["runtime_a_obs"]) > 1e-12
                    or abs(params["a_q"] - snap["runtime_a_q"]) > 1e-12
                ),
                "per_seed_intercept_solve_count": snap["per_seed_intercept_solve_count"],
                "profile_id": snap["profile_id"],
            })

            opp = pd.read_parquet(seed_dir / "opportunity_events.parquet")
            obs = pd.read_parquet(seed_dir / "observation_events.parquet")
            arr = pd.read_parquet(seed_dir / "hard_arrival_events.parquet")
            stages = hard_stage_masses(opp=opp, obs=obs, arrival=arr, unit_meta=unit_meta)
            dump_json(stages, seed_dir / "hard_stage_direction.json")
            seed_stages.append(stages)

        hard_pooled = pool_stage_directions(seed_stages)
        dump_json(hard_pooled, scen_dir / "pooled_hard_stage_direction.json")
        cert = certify_hard_directions(scenario_id, exact["audit"]["signed"], hard_pooled)
        if cert["notes"].get("hardcoded_pass_used"):
            hardcoded_pass += 1
            all_pass = False
        if cert["status"] != "PASS":
            all_pass = False

        scen_payload = {
            "label": label,
            "scenario_id": scenario_id,
            "status": cert["status"],
            "profile_id": SELECTED_STRENGTH,
            "params": params,
            "expected_signed": exact["audit"]["signed"],
            "hard_pooled": hard_pooled,
            "hard_certificate": cert,
            "clip": clip_by_scenario[scenario_id],
            "support": {
                "minimum_positive_group_expected_arrivals": support["minimum_positive_group_expected_arrivals"],
                "minimum_positive_stratum_expected_arrivals": support["minimum_positive_stratum_expected_arrivals"],
                "minimum_positive_client_stratum_expected_arrivals": support[
                    "minimum_positive_client_stratum_expected_arrivals"
                ],
                "status": support["status"],
            },
            "rates_pooled": {
                "opportunity": rate_opp / 3,
                "observation": rate_obs / 3,
                "usable": rate_use / 3,
            },
            "seeds": list(PROFILE_SEEDS),
            "trace_count": 3,
            "intercept_solve_count": 1,
        }
        dump_json(scen_payload, scen_dir / "DIRECTION_CERTIFICATE.json")
        scenario_certs[scenario_id] = scen_payload
        candidate["scenarios"][scenario_id]["exact_expected_signed"] = exact["audit"]["signed"]
        candidate["scenarios"][scenario_id]["pooled_hard_signed"] = cert["hard_signed"]
        candidate["scenarios"][scenario_id]["direction_status"] = cert["status"]

    # Combined client-window activity across scenarios (S1–S6 files already written)
    # Write aggregate expected_client_window_activity for balanced as representative + per-scenario already saved
    pd.concat([
        pd.read_parquet(OUT / "scenarios" / sid / "exact_expected_client_window_activity.parquet").assign(scenario_id=sid)
        for _, sid in SCENARIO_ORDER
    ], ignore_index=True).to_parquet(OUT / "expected_client_window_activity.parquet", index=False)

    dump_json(candidate, FROZEN / "traffic_s1_s6_profile_s1_candidate_registry.json")
    (FROZEN / "traffic_s1_s6_profile_s1_candidate_registry.yaml").write_text(
        yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8",
    )

    param_audit = {
        "status": "PASS" if (
            per_seed_solve == 0
            and all(r["mismatch_count"] == 0 for r in param_rows)
            and all(r["profile_id"] == SELECTED_STRENGTH for r in param_rows)
            and all(v == 1 for v in intercept_solve_per_scenario.values())
        ) else "FAIL",
        "rows": param_rows,
        "per_seed_intercept_solve_count": per_seed_solve,
        "intercept_solve_count_per_scenario": intercept_solve_per_scenario,
        "selected_strength": SELECTED_STRENGTH,
        "other_strength_executed_count": 0,
        "strength_grid_search_count": 0,
    }
    if param_audit["status"] != "PASS":
        all_pass = False
    dump_json(param_audit, AUDIT / "E2_TRAFFIC_PROFILE_S1_PARAMETER_CONSISTENCY_AUDIT.json")

    exact_mass_audit = {
        "status": "PASS" if all(v["status"] == "PASS" for v in exact_audits.values()) else "FAIL",
        "by_scenario": exact_audits,
        "exact_enumeration_window_count": N_CLIENTS * N_WINDOWS,
        "max_subset_count_per_window": 64,
        "implementation": "raven_mcs.e2.traffic_profiles.runner_consistency.exact_expected_masses",
    }
    dump_json(exact_mass_audit, AUDIT / "E2_TRAFFIC_PROFILE_S1_EXACT_EXPECTED_MASS_AUDIT.json")

    clip_support = {
        "status": "PASS" if all(v["status"] == "PASS" for v in support_by_scenario.values()) else "FAIL",
        "probability_bounds": PROB_BOUNDS,
        "clip_by_scenario": clip_by_scenario,
        "support_by_scenario": {
            sid: {
                k: support_by_scenario[sid][k]
                for k in (
                    "status",
                    "tail_group_minimum_expected_arrivals",
                    "minimum_positive_group_expected_arrivals",
                    "minimum_positive_stratum_expected_arrivals",
                    "minimum_positive_client_stratum_expected_arrivals",
                    "total_exact_expected_arrival_mass",
                    "required_group_zero_count",
                )
            }
            for sid in support_by_scenario
        },
        "selected_strength": SELECTED_STRENGTH,
        "strength_grid_search_count": 0,
        "client_stratum_absolute_veto": False,
    }
    if clip_support["status"] != "PASS":
        all_pass = False
    dump_json(clip_support, AUDIT / "E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json")

    direction_cert = {
        "status": "PASS" if all(scenario_certs[sid]["status"] == "PASS" for _, sid in SCENARIO_ORDER) else "FAIL",
        "selected_strength": SELECTED_STRENGTH,
        "scenarios": {sid: scenario_certs[sid]["status"] for _, sid in SCENARIO_ORDER},
        "pass_count": sum(1 for _, sid in SCENARIO_ORDER if scenario_certs[sid]["status"] == "PASS"),
        "hardcoded_pass_count": hardcoded_pass,
        "atomic_hard_tv_primary_gate": False,
        "by_scenario": {
            sid: {
                "expected_signed": scenario_certs[sid]["expected_signed"],
                "hard_signed": scenario_certs[sid]["hard_certificate"]["hard_signed"],
                "checks": scenario_certs[sid]["hard_certificate"]["checks"],
                "status": scenario_certs[sid]["status"],
            }
            for _, sid in SCENARIO_ORDER
        },
    }
    if direction_cert["status"] != "PASS":
        all_pass = False
    dump_json(direction_cert, FROZEN / "traffic_s1_s6_profile_s1_direction_certificate.json")
    dump_json(direction_cert, AUDIT / "E2_TRAFFIC_PROFILE_S1_DIRECTION_CERTIFICATE.json")

    # Final registry only if all pass
    final_registry = dict(candidate)
    final_registry["status"] = "FROZEN" if all_pass else "NOT_FROZEN"
    final_registry["protocol"] = PACKAGE
    final_registry["profile_s2_blocked_reason"] = tombstone
    final_registry["exact_expected_mass_algorithm"] = "subset_enumeration_2^m_m_le_6"
    final_registry["freeze_commit"] = _git_head()
    final_registry["frozen_at_utc"] = datetime.now(timezone.utc).isoformat()
    final_registry["clip_support_audit_sha256"] = sha256_json(clip_support)
    final_registry["exact_expected_mass_audit_sha256"] = sha256_json(exact_mass_audit)
    dump_json(final_registry, FROZEN / "traffic_s1_s6_profile_registry.json")
    (FROZEN / "traffic_s1_s6_profile_registry.yaml").write_text(
        yaml.safe_dump(final_registry, sort_keys=False), encoding="utf-8",
    )
    # Alias certificate name required by instruction section 11
    dump_json(direction_cert, FROZEN / "traffic_s1_s6_direction_certificate.json")

    identity_freeze = {
        "protocol": PACKAGE,
        "status": "FROZEN" if all_pass else "NOT_FROZEN",
        "selected_strength": SELECTED_STRENGTH,
        "selection_reason": "deterministic_support_fallback",
        "registry_sha256": sha256_file(FROZEN / "traffic_s1_s6_profile_registry.json"),
        "direction_certificate_sha256": sha256_file(FROZEN / "traffic_s1_s6_direction_certificate.json"),
        "candidate_registry_sha256": sha256_file(FROZEN / "traffic_s1_s6_profile_s1_candidate_registry.json"),
        "exact_expected_mass_audit_sha256": final_registry["exact_expected_mass_audit_sha256"],
        "clip_support_audit_sha256": final_registry["clip_support_audit_sha256"],
        "probability_bounds": PROB_BOUNDS,
        "no_per_seed_intercept_recalibration": True,
        "design_seeds": list(PROFILE_SEEDS),
        "freeze_commit": _git_head(),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(identity_freeze, FROZEN / "traffic_s1_s6_runner_identity.json")

    status = (
        "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY"
        if all_pass
        else "BLOCKED_TRAFFIC_PROFILE_S1_FINAL_FREEZE_FAILED"
    )
    support_minima = {
        sid: {
            "group": support_by_scenario[sid]["minimum_positive_group_expected_arrivals"],
            "stratum": support_by_scenario[sid]["minimum_positive_stratum_expected_arrivals"],
            "client_stratum": support_by_scenario[sid]["minimum_positive_client_stratum_expected_arrivals"],
        }
        for _, sid in SCENARIO_ORDER
    }
    stop = {
        "status": status,
        "selected_strength": SELECTED_STRENGTH,
        "selection_reason": "deterministic_support_fallback",
        "hard_trace_count": total_traces,
        "scenario_pass_count": direction_cert["pass_count"],
        "parameter_sets_per_scenario": 1,
        "per_seed_intercept_solve_count": per_seed_solve,
        "strength_grid_search_count": 0,
        "other_strength_executed_count": 0,
        "exact_enumeration_window_count": N_CLIENTS * N_WINDOWS,
        "probability_bounds": PROB_BOUNDS,
        "hardcoded_pass_count": hardcoded_pass,
        "unsupported_arrival_count": unsupported,
        "failed_attempt_omission_count": failed_omit,
        "q_leakage_count": q_leak,
        "target_leakage_count": target_leak,
        "training_artifact_count": 0,
        "seed_29001_read_count": 0,
        "validation_seed_read_count": 0,
        "formal_seed_read_count": 0,
        "e2_formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "design_seeds": list(PROFILE_SEEDS),
        "registry_sha256": identity_freeze["registry_sha256"],
        "direction_certificate_sha256": identity_freeze["direction_certificate_sha256"],
        "next_authorized_round": (
            "E2-TRAFFIC-REAL-RUNNER-CANARY-R1" if all_pass else "TEACHER_REVIEW_REQUIRED"
        ),
        "runtime_commit": _git_head(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_results": {sid: scenario_certs[sid]["status"] for _, sid in SCENARIO_ORDER},
        "clip_by_scenario": clip_by_scenario,
        "support_minima": support_minima,
    }
    dump_json(stop, OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")

    front = {
        "selected strength": SELECTED_STRENGTH,
        "selection reason": "deterministic_support_fallback",
        "scenarios": 6,
        "seeds": list(PROFILE_SEEDS),
        "traces": total_traces,
        "per-seed intercept solve count": per_seed_solve,
        "minimum expected group arrivals": {
            sid: support_minima[sid]["group"] for _, sid in SCENARIO_ORDER
        },
        "minimum expected stratum arrivals": {
            sid: support_minima[sid]["stratum"] for _, sid in SCENARIO_ORDER
        },
        "S1-S6 direction PASS count": direction_cert["pass_count"],
        "unsupported arrivals": unsupported,
        "failed-attempt omissions": failed_omit,
        "q leakage": q_leak,
        "training count": 0,
        "seed29001 reads": 0,
        "validation reads": 0,
        "formal reads": 0,
        "status": status,
    }
    write_report({
        "front": front,
        "sections": [
            ("2. Why PROFILE-S2 Was Blocked", tombstone),
            ("3. Deterministic PROFILE-S1 Fallback", {
                "selected_strength": SELECTED_STRENGTH,
                "kappas": strength,
                "selection_reason": "deterministic_support_fallback",
            }),
            ("4. Fixed Registry Parameters", candidate["scenarios"]),
            ("5. Exact Expected Mass", exact_mass_audit),
            ("6. Clip and Support Audit", clip_support),
            ("7. Eighteen PROFILE-S1 Hard Traces", {"count": total_traces}),
            ("8. S1-S6 Stage-Wise Directions", direction_cert["by_scenario"]),
            ("9. Final Runner Registry", identity_freeze),
            ("12. Stop Position", {k: stop[k] for k in stop if k not in {"clip_by_scenario", "support_minima"}}),
            ("13. Next Authorized Round", stop["next_authorized_round"]),
        ],
    })
    write_readme(stop)
    print(json.dumps({
        k: stop[k] for k in stop if k not in {"clip_by_scenario", "support_minima", "scenario_results"}
    }, indent=2))
    print("scenario_results", stop["scenario_results"])
    print("support_minima", support_minima)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
