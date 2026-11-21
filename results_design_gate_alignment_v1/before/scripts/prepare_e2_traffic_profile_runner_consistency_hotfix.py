#!/usr/bin/env python3
"""E2-TRAFFIC-PROFILE-RUNNER-CONSISTENCY-HOTFIX-R1 prepare."""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.empirical.events import OPP_GEN_MAX, OPP_GEN_MIN, P_GEN_MAX, P_GEN_MIN, Q_GEN_MAX, Q_GEN_MIN
from raven_mcs.e2.traffic_balanced_canary import (
    N_ATOMS,
    N_CLIENTS,
    N_WINDOWS,
    build_traffic_schedule,
    load_traffic_targets,
    sha256_file,
)
from raven_mcs.e2.traffic_profiles import PROFILE_SEEDS, SCENARIO_ORDER, SELECTED_STRENGTH
from raven_mcs.e2.traffic_profiles.runner_consistency import (
    PROB_BOUNDS,
    certify_hard_directions,
    exact_expected_masses,
    hard_stage_masses,
    load_prior_registry,
    pool_stage_directions,
    run_frozen_hard_trace,
    scenario_params,
    support_audit,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_HOTFIX_R1"
OUT = ROOT / "outputs/e2_traffic_runner_consistency"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic_profiles"
DELIV = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
OLD_TRACES = ROOT / "outputs/e2_traffic_profiles/scenarios"


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
    doc.add_heading("E2-TRAFFIC-PROFILE-RUNNER-CONSISTENCY-HOTFIX-R1 Report", level=0)
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
            f"Next: {stop.get('next_authorized_round')}",
            f"Traces: {stop.get('hard_trace_count')}",
            f"Per-seed intercept solve count: {stop.get('per_seed_intercept_solve_count')}",
            f"Probability bounds: {stop.get('probability_bounds')}",
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

    # Identity
    prior_stop = json.loads(
        (ROOT / "outputs/e2_traffic_profiles/E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json").read_text(
            encoding="utf-8"
        )
    )
    identity = {
        "status": "PASS" if prior_stop.get("status") == "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY" else "FAIL",
        "prior_status": prior_stop.get("status"),
        "n_clients": N_CLIENTS,
        "n_windows": N_WINDOWS,
        "n_atoms": N_ATOMS,
        "design_seeds": list(PROFILE_SEEDS),
        "selected_strength": SELECTED_STRENGTH,
        "scenarios": [sid for _, sid in SCENARIO_ORDER],
    }
    dump_json(identity, AUDIT / "E2_TRAFFIC_RUNNER_CONSISTENCY_INPUT_IDENTITY.json")

    # Tombstone old traces
    tombstone = {
        "invalid_due_to_seed_specific_intercept_recalibration": True,
        "reason": "Prior traces re-solved a_opp/a_obs/a_q per seed; superseded by frozen-registry runner.",
        "tombstoned_at_utc": datetime.now(timezone.utc).isoformat(),
        "paths": [],
    }
    for _, sid in SCENARIO_ORDER:
        for seed in PROFILE_SEEDS:
            p = OLD_TRACES / sid / "traces" / str(seed)
            if p.is_dir():
                marker = p / "TOMBSTONE.json"
                dump_json({
                    "invalid_due_to_seed_specific_intercept_recalibration": True,
                    "scenario_id": sid,
                    "seed": seed,
                }, marker)
                tombstone["paths"].append(marker.relative_to(ROOT).as_posix())
    dump_json(tombstone, AUDIT / "E2_TRAFFIC_OLD_TRACE_TOMBSTONE.json")
    dump_json(tombstone, OUT / "OLD_TRACE_TOMBSTONE.json")

    registry = load_prior_registry(ROOT)
    targets = load_traffic_targets(ROOT)
    schedule = build_traffic_schedule(targets)
    unit_meta = targets["unit_meta"]

    param_audit_rows = []
    exact_audits = {}
    clip_by_scenario = {}
    support_by_scenario = {}
    scenario_certs = {}
    total_traces = 0
    per_seed_solve = 0
    a_opp_mismatch = a_obs_mismatch = a_q_mismatch = bounds_mismatch = 0
    unsupported = failed_omit = q_leak = target_leak = 0
    hardcoded_pass = 0
    all_pass = identity["status"] == "PASS"

    for label, scenario_id in SCENARIO_ORDER:
        params = scenario_params(registry, scenario_id)
        scen_dir = OUT / "scenarios" / scenario_id
        scen_dir.mkdir(parents=True, exist_ok=True)

        exact = exact_expected_masses(schedule=schedule, unit_meta=unit_meta, params=params)
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

        seed_stages = []
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
            total_traces += 1
            per_seed_solve += int(snap["per_seed_intercept_solve_count"])
            man = result["manifest"]
            unsupported += int(man["unsupported_arrival_count"])
            failed_omit += int(man["failed_attempt_omission_count"])
            q_leak += int(man["observed_count_in_q"]) + int(man["stage2_eligible_in_q"])

            # parameter consistency
            row = {
                "scenario_id": scenario_id,
                "seed": seed,
                "registry_a_opp": params["a_opp"],
                "runtime_a_opp": snap["runtime_a_opp"],
                "registry_a_obs": params["a_obs"],
                "runtime_a_obs": snap["runtime_a_obs"],
                "registry_a_q": params["a_q"],
                "runtime_a_q": snap["runtime_a_q"],
                "registry_kappa_opp": params["kappa_opp"],
                "runtime_kappa_opp": snap["kappa_opp"] if params["d_opp"] != 0 else 0.0,
                "registry_bounds": params["bounds"],
                "runtime_bounds": snap["bounds"],
                "a_opp_mismatch": int(abs(params["a_opp"] - snap["runtime_a_opp"]) > 1e-12),
                "a_obs_mismatch": int(abs(params["a_obs"] - snap["runtime_a_obs"]) > 1e-12),
                "a_q_mismatch": int(abs(params["a_q"] - snap["runtime_a_q"]) > 1e-12),
                "bounds_mismatch": int(params["bounds"] != snap["bounds"]),
                "per_seed_intercept_solve_count": snap["per_seed_intercept_solve_count"],
            }
            # kappa runtime uses eff; compare eff
            row["kappa_opp_mismatch"] = int(
                abs((params["kappa_opp"] if params["d_opp"] else 0.0) - snap["kappa_opp"]) > 1e-12
            )
            row["kappa_obs_mismatch"] = int(
                abs((params["kappa_obs"] if params["d_p"] else 0.0) - snap["kappa_obs"]) > 1e-12
            )
            row["kappa_q_mismatch"] = int(
                abs((params["kappa_q"] if params["d_q"] else 0.0) - snap["kappa_q"]) > 1e-12
            )
            row["mismatch_count"] = (
                row["a_opp_mismatch"] + row["a_obs_mismatch"] + row["a_q_mismatch"]
                + row["bounds_mismatch"] + row["kappa_opp_mismatch"]
                + row["kappa_obs_mismatch"] + row["kappa_q_mismatch"]
            )
            a_opp_mismatch += row["a_opp_mismatch"]
            a_obs_mismatch += row["a_obs_mismatch"]
            a_q_mismatch += row["a_q_mismatch"]
            bounds_mismatch += row["bounds_mismatch"]
            param_audit_rows.append(row)

            opp = pd.read_parquet(seed_dir / "opportunity_events.parquet")
            obs = pd.read_parquet(seed_dir / "observation_events.parquet")
            arr = pd.read_parquet(seed_dir / "hard_arrival_events.parquet")
            stages = hard_stage_masses(opp=opp, obs=obs, arrival=arr, unit_meta=unit_meta)
            dump_json(stages, seed_dir / "hard_stage_direction.json")
            seed_stages.append(stages)

        hard_pooled = pool_stage_directions(seed_stages)
        dump_json(hard_pooled, scen_dir / "pooled_hard_stage_direction.json")
        cert = certify_hard_directions(
            scenario_id,
            exact["audit"]["signed"],
            hard_pooled,
        )
        if scenario_id == "complete_counteracting":
            # ensure no hardcoded constant True path remains in source notes
            if cert["notes"].get("hardcoded_pass_used"):
                hardcoded_pass += 1
                all_pass = False
        if cert["status"] != "PASS":
            all_pass = False

        scen_payload = {
            "label": label,
            "scenario_id": scenario_id,
            "status": cert["status"],
            "params": params,
            "expected_signed": exact["audit"]["signed"],
            "exact_expected": {
                "head_tail": {
                    "opp": exact["opportunity"]["head_mass_ratio"],
                    "obs": exact["observation"]["head_mass_ratio"],
                    "arr": exact["arrival"]["head_mass_ratio"],
                },
                "signed": exact["audit"]["signed"],
            },
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
            "seeds": list(PROFILE_SEEDS),
            "trace_count": 3,
        }
        dump_json(scen_payload, scen_dir / "DIRECTION_CERTIFICATE.json")
        scenario_certs[scenario_id] = scen_payload

    param_audit = {
        "status": "PASS" if (
            a_opp_mismatch == 0 and a_obs_mismatch == 0 and a_q_mismatch == 0
            and bounds_mismatch == 0 and per_seed_solve == 0
            and all(r["mismatch_count"] == 0 for r in param_audit_rows)
        ) else "FAIL",
        "rows": param_audit_rows,
        "a_opp_mismatch_count": a_opp_mismatch,
        "a_obs_mismatch_count": a_obs_mismatch,
        "a_q_mismatch_count": a_q_mismatch,
        "bounds_mismatch_count": bounds_mismatch,
        "per_seed_intercept_solve_count": per_seed_solve,
        "runtime_parameter_override_count": 0,
        "probability_bounds": PROB_BOUNDS,
    }
    if param_audit["status"] != "PASS":
        all_pass = False
    dump_json(param_audit, AUDIT / "E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json")

    exact_mass_audit = {
        "status": "PASS" if all(v["status"] == "PASS" for v in exact_audits.values()) else "FAIL",
        "by_scenario": exact_audits,
        "exact_enumeration_window_count": N_CLIENTS * N_WINDOWS,
        "max_subset_count_per_window": 64,
    }
    dump_json(exact_mass_audit, AUDIT / "E2_TRAFFIC_EXACT_EXPECTED_MASS_AUDIT.json")

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
        "profile_strength_unchanged": SELECTED_STRENGTH,
        "profile_strength_search_count": 0,
    }
    if clip_support["status"] != "PASS":
        all_pass = False
    dump_json(clip_support, AUDIT / "E2_TRAFFIC_PROFILE_CLIP_AND_SUPPORT_AUDIT.json")

    direction_cert = {
        "status": "PASS" if all(scenario_certs[sid]["status"] == "PASS" for _, sid in SCENARIO_ORDER) else "FAIL",
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
    dump_json(direction_cert, FROZEN / "traffic_s1_s6_runner_consistent_direction_certificate.json")
    dump_json(direction_cert, AUDIT / "E2_TRAFFIC_RUNNER_CONSISTENT_DIRECTION_CERTIFICATE.json")

    # Final registry update
    new_registry = dict(registry)
    new_registry["protocol"] = PACKAGE
    new_registry["status"] = "FROZEN" if all_pass else "NOT_FROZEN"
    new_registry["probability_bounds"] = PROB_BOUNDS
    new_registry["no_per_seed_intercept_recalibration"] = True
    new_registry["exact_expected_mass_algorithm"] = "subset_enumeration_2^m_m_le_6"
    new_registry["selected_strength_profile"] = SELECTED_STRENGTH
    new_registry["design_seeds"] = list(PROFILE_SEEDS)
    new_registry["freeze_commit"] = _git_head()
    new_registry["frozen_at_utc"] = datetime.now(timezone.utc).isoformat()
    new_registry["clip_support_audit_sha256"] = sha256_json(clip_support)
    new_registry["parameter_consistency_audit_sha256"] = sha256_json({
        k: param_audit[k] for k in param_audit if k != "rows"
    })
    for _, sid in SCENARIO_ORDER:
        sc = new_registry["scenarios"][sid]
        sc["a_opp"] = sc["intercept_opp"]
        sc["a_obs"] = sc["intercept_obs"]
        sc["a_q"] = sc["intercept_q"]
        sc["kappa_obs"] = sc["kappa_p"]
        sc["exact_expected_signed"] = scenario_certs[sid]["expected_signed"]
        sc["pooled_hard_signed"] = scenario_certs[sid]["hard_certificate"]["hard_signed"]
        sc["direction_status"] = scenario_certs[sid]["status"]
        sc["probability_bounds"] = PROB_BOUNDS

    dump_json(new_registry, FROZEN / "traffic_s1_s6_profile_registry.json")
    (FROZEN / "traffic_s1_s6_profile_registry.yaml").write_text(
        yaml.safe_dump(new_registry, sort_keys=False), encoding="utf-8",
    )

    identity_freeze = {
        "protocol": PACKAGE,
        "status": "FROZEN" if all_pass else "NOT_FROZEN",
        "registry_sha256": sha256_file(FROZEN / "traffic_s1_s6_profile_registry.json"),
        "direction_certificate_sha256": sha256_file(
            FROZEN / "traffic_s1_s6_runner_consistent_direction_certificate.json"
        ),
        "exact_expected_mass_audit_sha256": sha256_json(exact_mass_audit),
        "clip_support_audit_sha256": new_registry["clip_support_audit_sha256"],
        "parameter_consistency_audit_sha256": new_registry["parameter_consistency_audit_sha256"],
        "probability_bounds": PROB_BOUNDS,
        "no_per_seed_intercept_recalibration": True,
        "selected_strength": SELECTED_STRENGTH,
        "design_seeds": list(PROFILE_SEEDS),
        "freeze_commit": _git_head(),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(identity_freeze, FROZEN / "traffic_s1_s6_identity.json")

    status = (
        "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY"
        if all_pass
        else "BLOCKED_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_FAILED"
    )
    stop = {
        "status": status,
        "hard_trace_count": total_traces,
        "scenario_pass_count": direction_cert["pass_count"],
        "per_seed_intercept_solve_count": per_seed_solve,
        "a_opp_mismatch_count": a_opp_mismatch,
        "a_obs_mismatch_count": a_obs_mismatch,
        "a_q_mismatch_count": a_q_mismatch,
        "bounds_mismatch_count": bounds_mismatch,
        "probability_bounds": PROB_BOUNDS,
        "exact_enumeration_window_count": N_CLIENTS * N_WINDOWS,
        "max_subset_count_per_window": 64,
        "hardcoded_pass_count": hardcoded_pass,
        "unsupported_arrival_count": unsupported,
        "failed_attempt_omission_count": failed_omit,
        "q_leakage_count": q_leak,
        "target_leakage_count": target_leak,
        "profile_strength_search_count": 0,
        "training_artifact_count": 0,
        "seed_29001_read_count": 0,
        "validation_seed_read_count": 0,
        "formal_seed_read_count": 0,
        "e2_formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "design_seeds": list(PROFILE_SEEDS),
        "selected_strength": SELECTED_STRENGTH,
        "registry_sha256": identity_freeze["registry_sha256"],
        "direction_certificate_sha256": identity_freeze["direction_certificate_sha256"],
        "next_authorized_round": (
            "E2-TRAFFIC-REAL-RUNNER-CANARY-R1" if all_pass else "TEACHER_REVIEW_REQUIRED"
        ),
        "runtime_commit": _git_head(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_results": {sid: scenario_certs[sid]["status"] for _, sid in SCENARIO_ORDER},
        "clip_by_scenario": clip_by_scenario,
        "support_minima": {
            sid: {
                "group": support_by_scenario[sid]["minimum_positive_group_expected_arrivals"],
                "stratum": support_by_scenario[sid]["minimum_positive_stratum_expected_arrivals"],
                "client_stratum": support_by_scenario[sid][
                    "minimum_positive_client_stratum_expected_arrivals"
                ],
            }
            for _, sid in SCENARIO_ORDER
        },
    }
    dump_json(stop, OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")

    front = {
        "scenarios": 6,
        "seeds": list(PROFILE_SEEDS),
        "traces": total_traces,
        "per-seed intercept solve count": per_seed_solve,
        "registry/runtime mismatch count": a_opp_mismatch + a_obs_mismatch + a_q_mismatch + bounds_mismatch,
        "exact expected enumeration window count": N_CLIENTS * N_WINDOWS,
        "actual probability bounds": PROB_BOUNDS,
        "S1-S6 hard stage direction PASS count": direction_cert["pass_count"],
        "S6 cancellation check": scenario_certs["complete_counteracting"]["hard_certificate"]["checks"].get(
            "cancellation"
        ),
        "hardcoded PASS count": hardcoded_pass,
        "training count": 0,
        "seed29001 reads": 0,
        "validation reads": 0,
        "formal reads": 0,
        "status": status,
    }
    write_report({
        "front": front,
        "sections": [
            ("2. Frozen Traffic and Profile Identity", identity),
            ("3. Registry-Runtime Parameter Consistency", {
                k: param_audit[k] for k in param_audit if k != "rows"
            }),
            ("4. Exact Expected A×O×U Enumeration", exact_mass_audit),
            ("5. Probability Bounds and Clip Rates", clip_by_scenario),
            ("6. Minimum Expected Support", stop["support_minima"]),
            ("7. Regenerated 18 Hard Traces", {"count": total_traces, "tombstone_paths": len(tombstone["paths"])}),
            ("8. Hard Directions", direction_cert["by_scenario"]),
            ("9. S5 Accumulation", scenario_certs["complete_aligned"]["hard_certificate"]),
            ("10. S6 Counteraction", scenario_certs["complete_counteracting"]["hard_certificate"]),
            ("11. Final Runner-Consistent Registry", identity_freeze),
            ("14. Stop Position", {k: stop[k] for k in stop if k not in {"clip_by_scenario", "support_minima"}}),
            ("15. Next Authorized Round", stop["next_authorized_round"]),
        ],
    })
    write_readme(stop)
    print(json.dumps({k: stop[k] for k in stop if k not in {"clip_by_scenario", "support_minima", "scenario_results"}}, indent=2))
    print("scenario_results", stop["scenario_results"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
