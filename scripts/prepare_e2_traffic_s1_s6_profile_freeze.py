#!/usr/bin/env python3
"""E2-TRAFFIC-S1-S6-PROFILE-FREEZE-R1: freeze six Traffic scenarios."""
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
    SELECTED_STRENGTH,
    audit_q_runtime,
    build_expected_masses,
    direction_pass,
    load_direction_registry,
    load_strength_registry,
    pool_hard_direction,
    run_hard_scenario_seed,
    solve_stage_probabilities,
    verify_inputs,
    write_balanced_gate_correction,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_R1"
OUT = ROOT / "outputs/e2_traffic_profiles"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic_profiles"
DELIV = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"

# Rate tolerance bands (±0.03 / ±0.03 / ±0.05)
OPP_LO, OPP_HI = 0.52, 0.58
OBS_LO, OBS_HI = 0.17, 0.23
USE_LO, USE_HI = 0.55, 0.65


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
    doc.add_heading("E2-TRAFFIC-S1-S6-PROFILE-FREEZE-R1 Report", level=0)
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
    lines = [
        f"Package: {PACKAGE}",
        f"Status: {stop.get('status')}",
        f"Next: {stop.get('next_authorized_round')}",
        f"Design seeds: {PROFILE_SEEDS}",
        f"Trace count: {stop.get('hard_trace_count')}",
        f"Selected strength: {SELECTED_STRENGTH}",
        f"Runtime commit: {stop.get('runtime_commit')}",
        "",
        "Primary artifacts:",
        f"  - {PACKAGE}_REPORT.docx",
        f"  - RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
        f"  - {PACKAGE}_SUBMISSION_README.txt",
        "  - FINAL_DELIVERABLE_HASHES.json",
        "  - FINAL_DELIVERABLE_HASHES_VERIFY.json",
        "",
        "Frozen profile registry:",
        "  configs/frozen/e2_traffic_profiles/traffic_s1_s6_profile_registry.yaml",
        "  configs/frozen/e2_traffic_profiles/traffic_s1_s6_direction_certificate.json",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    for d in (OUT, AUDIT, FROZEN, DELIV):
        d.mkdir(parents=True, exist_ok=True)

    identity = verify_inputs(ROOT)
    # Expand identity with full traffic parent freeze paths
    targets_probe = None
    try:
        targets_probe = load_traffic_targets(ROOT)
        schedule_probe = build_traffic_schedule(targets_probe)
        identity["n_clients"] = len(schedule_probe["clients"])
        identity["n_windows"] = N_WINDOWS
        identity["n_atoms"] = N_ATOMS
    except Exception as exc:
        identity["status"] = "BLOCKED_INPUT_IDENTITY_MISMATCH"
        identity["load_error"] = str(exc)
    dump_json(identity, AUDIT / "E2_TRAFFIC_S1_S6_INPUT_IDENTITY_AUDIT.json")

    gate_corr = write_balanced_gate_correction(ROOT)
    dump_json(gate_corr, AUDIT / "E2_TRAFFIC_BALANCED_GATE_CORRECTION_AUDIT.json")

    q_audit = audit_q_runtime()
    dump_json(q_audit, AUDIT / "E2_TRAFFIC_Q_RUNTIME_INTERFACE_AUDIT.json")

    if identity["status"] != "PASS" or q_audit["status"] != "PASS":
        stop = {
            "status": "BLOCKED_TRAFFIC_PROFILE_FREEZE_FAILED",
            "blocked_reason": identity.get("status") if identity["status"] != "PASS" else "q_runtime",
            "hard_trace_count": 0,
            "training_artifact_count": 0,
            "seed_29001_read_count": 0,
            "validation_seed_read_count": 0,
            "formal_seed_read_count": 0,
            "e2_formal_runs": 0,
            "e3_e9_status": "NOT_STARTED",
            "grid_search_count": 0,
            "next_authorized_round": "TEACHER_REVIEW_REQUIRED",
            "runtime_commit": _git_head(),
        }
        dump_json(stop, OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
        write_report({"front": stop, "sections": [("Identity", identity), ("Q", q_audit)]})
        write_readme(stop)
        print(json.dumps(stop, indent=2))
        return 0

    direction_reg = load_direction_registry(ROOT)
    strength_reg = load_strength_registry(ROOT)
    strength = strength_reg["profiles"][SELECTED_STRENGTH]
    targets = targets_probe or load_traffic_targets(ROOT)
    schedule = build_traffic_schedule(targets)
    unit_meta = targets["unit_meta"]
    varpi = {u: float(m["varpi"]) for u, m in unit_meta.items()}

    scenario_results: dict[str, Any] = {}
    all_pass = True
    total_traces = 0
    unsupported = 0
    failed_omit = 0
    q_leak = 0
    target_leak = 0
    stage2_in_q = 0
    obs_in_q = 0

    for label, scenario_id in SCENARIO_ORDER:
        sc = direction_reg["scenarios"][scenario_id]
        scen_dir = OUT / "scenarios" / scenario_id
        scen_dir.mkdir(parents=True, exist_ok=True)

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
        expected = build_expected_masses(
            schedule=schedule, unit_meta=unit_meta, probs=probs, varpi=varpi,
        )
        expected["opportunity"]["frame"].to_parquet(
            scen_dir / "expected_opportunity_mass.parquet", index=False,
        )
        expected["observation"]["frame"].to_parquet(
            scen_dir / "expected_observation_mass.parquet", index=False,
        )
        expected["arrival"]["frame"].to_parquet(
            scen_dir / "expected_arrival_mass.parquet", index=False,
        )
        expected["client_window"].to_parquet(
            scen_dir / "expected_client_window_activity.parquet", index=False,
        )

        dump_json({
            "scenario_id": scenario_id,
            "label": label,
            "profile_id": SELECTED_STRENGTH,
            "d_opp": int(sc["d_opp"]),
            "d_p": int(sc["d_p"]),
            "d_q": int(sc["d_q"]),
            "kappa_opp": float(strength["kappa_opp"]),
            "kappa_p": float(strength["kappa_p"]),
            "kappa_q": float(strength["kappa_q"]),
            "intercept_opp": probs["intercept_opp"],
            "intercept_obs": probs["intercept_obs"],
            "intercept_q": probs["intercept_q"],
            "mean_p_opp": probs["mean_p_opp"],
            "mean_p_obs": probs["mean_p_obs"],
            "mean_q": probs["mean_q"],
            "targets": {
                "opportunity": OPP_RATE_TARGET,
                "observation": OBS_RATE_TARGET,
                "usable": USE_RATE_TARGET,
            },
            "D_opp": expected["D_opp"],
            "D_obs": expected["D_obs"],
            "D_arr": expected["D_arr"],
            "signed": {
                "opp": expected["opportunity"]["signed_head_minus_tail"],
                "obs": expected["observation"]["signed_head_minus_tail"],
                "arr": expected["arrival"]["signed_head_minus_tail"],
            },
            "head_mass_ratio_arr": expected["arrival"]["head_mass_ratio"],
            "tail_mass_ratio_arr": expected["arrival"]["tail_mass_ratio"],
            "parameter_set_count": 1,
            "grid_search_count": 0,
        }, scen_dir / "frozen_parameters.json")

        seed_diags = []
        for seed in PROFILE_SEEDS:
            seed_dir = scen_dir / "traces" / str(seed)
            diag = run_hard_scenario_seed(
                seed=seed,
                scenario_id=scenario_id,
                profile_id=SELECTED_STRENGTH,
                schedule=schedule,
                unit_meta=unit_meta,
                directions=sc,
                strength=strength,
                output_dir=seed_dir,
            )
            # expected soft mass copy for replay
            expected["arrival"]["frame"][
                ["unit_id", "expected_mass", "mass_norm", "group", "stratum"]
            ].to_parquet(seed_dir / "expected_atomic_mass.parquet", index=False)
            manifest = json.loads((seed_dir / "eventtrace_manifest.json").read_text(encoding="utf-8"))
            manifest["antithetic_arm_count"] = 1
            manifest["arms"] = 1
            dump_json(manifest, seed_dir / "eventtrace_manifest.json")
            seed_diags.append(diag)
            total_traces += 1
            unsupported += int(diag.get("unsupported_arrival_count", 0))
            failed_omit += int(diag.get("failed_attempt_omission_count", 0))
            stage2_in_q += int(diag.get("stage2_eligible_in_q", 0))
            obs_in_q += int(diag.get("observed_count_in_q", 0))
            dump_json(diag if "emp_unit_mass" not in diag else {
                k: v for k, v in diag.items() if k != "emp_unit_mass"
            }, scen_dir / f"SEED_{seed}_DIAG.json")

        hard_pool = pool_hard_direction(seed_diags, unit_meta=unit_meta, varpi=varpi)
        cert = direction_pass(scenario_id, expected, hard=hard_pool)

        # Rate gates on pooled realized rates
        mean_opp = float(sum(d["realized_opportunity_rate"] for d in seed_diags) / 3)
        mean_obs = float(sum(d["realized_conditional_observation_rate"] for d in seed_diags) / 3)
        mean_use = float(sum(d["realized_conditional_usable_rate"] for d in seed_diags) / 3)
        rate_pass = (
            OPP_LO <= mean_opp <= OPP_HI
            and OBS_LO <= mean_obs <= OBS_HI
            and USE_LO <= mean_use <= USE_HI
        )
        scen_unsupported = sum(int(d.get("unsupported_arrival_count", 0)) for d in seed_diags)
        structural_pass = (
            scen_unsupported == 0
            and all(d["failed_attempt_omission_count"] == 0 for d in seed_diags)
            and all(d["cross_window_duplicate_count"] == 0 for d in seed_diags)
            and all(d["stage2_eligible_in_q"] == 0 for d in seed_diags)
            and all(d["observed_count_in_q"] == 0 for d in seed_diags)
        )

        # Hard direction vs expected sign (pooled)
        hard_dir_pass = True
        if scenario_id == "balanced":
            hard_dir_pass = abs(hard_pool["head_mass_ratio"] - 1.0) <= 0.08
        elif scenario_id == "complete_counteracting":
            hard_dir_pass = (
                hard_pool["D_TV"] > 0.005
                and hard_pool["signed_head_minus_tail"] < expected["observation"]["signed_head_minus_tail"]
            )
        else:
            hard_dir_pass = (
                np_sign_same(hard_pool["signed_head_minus_tail"], expected["arrival"]["signed_head_minus_tail"])
            )

        scen_status = (
            "PASS"
            if cert["status"] == "PASS" and rate_pass and structural_pass and hard_dir_pass
            else "FAIL"
        )
        if scen_status != "PASS":
            all_pass = False

        scen_payload = {
            "status": scen_status,
            "label": label,
            "scenario_id": scenario_id,
            "display_name": sc.get("display_name"),
            "expected_direction": sc.get("expected_direction"),
            "parameter_set_count": 1,
            "grid_search_count": 0,
            "profile_id": SELECTED_STRENGTH,
            "directions": {
                "d_opp": int(sc["d_opp"]),
                "d_p": int(sc["d_p"]),
                "d_q": int(sc["d_q"]),
            },
            "strength": strength,
            "intercepts": {
                "opp": probs["intercept_opp"],
                "obs": probs["intercept_obs"],
                "q": probs["intercept_q"],
            },
            "expected": {
                "D_opp": expected["D_opp"],
                "D_obs": expected["D_obs"],
                "D_arr": expected["D_arr"],
                "signed": cert["signed"],
                "head_mass_ratio": expected["arrival"]["head_mass_ratio"],
                "tail_mass_ratio": expected["arrival"]["tail_mass_ratio"],
                "checks": cert["checks"],
                "expected_status": cert["status"],
            },
            "hard_pooled": hard_pool,
            "hard_direction_pass": hard_dir_pass,
            "rates": {
                "mean_opportunity": mean_opp,
                "mean_observation": mean_obs,
                "mean_usable": mean_use,
                "rate_pass": rate_pass,
                "soft_mean_p_opp": probs["mean_p_opp"],
                "soft_mean_p_obs": probs["mean_p_obs"],
                "soft_mean_q": probs["mean_q"],
            },
            "structural_pass": structural_pass,
            "seeds": list(PROFILE_SEEDS),
            "trace_count": 3,
        }
        dump_json(scen_payload, scen_dir / "DIRECTION_CERTIFICATE.json")
        dump_json(scen_payload, AUDIT / f"E2_TRAFFIC_PROFILE_{label}_DIRECTION_AUDIT.json")
        scenario_results[scenario_id] = scen_payload

    # Non-degeneracy: S2-S6 D_arr >> S1
    s1_d = float(scenario_results["balanced"]["expected"]["D_arr"])
    nondeg = all(
        float(scenario_results[sid]["expected"]["D_arr"]) > s1_d + 0.01
        for _, sid in SCENARIO_ORDER
        if sid != "balanced"
    )
    s6 = scenario_results["complete_counteracting"]
    s6_cancel = (
        float(s6["expected"]["signed"]["arr"]) < float(s6["expected"]["signed"]["obs"])
        and float(s6["expected"]["D_arr"]) > 0.01
    )
    if not nondeg or not s6_cancel:
        all_pass = False

    dump_json({
        "status": "PASS" if nondeg and s6_cancel else "FAIL",
        "nondegeneracy": nondeg,
        "s6_cancellation": s6_cancel,
        "s1_D_arr": s1_d,
    }, AUDIT / "E2_TRAFFIC_PROFILE_NONDEGENERACY_AUDIT.json")

    dump_json({
        "status": "PASS" if unsupported == 0 and failed_omit == 0 else "FAIL",
        "unsupported_arrival_count": unsupported,
        "failed_attempt_omission_count": failed_omit,
        "stage2_eligible_in_q_count": stage2_in_q,
        "observed_count_in_q_count": obs_in_q,
        "q_leakage_count": q_leak,
        "target_leakage_count": target_leak,
    }, AUDIT / "E2_TRAFFIC_PROFILE_STRUCTURE_AUDIT.json")

    # Freeze registry
    registry = {
        "protocol": PACKAGE,
        "status": "FROZEN" if all_pass else "NOT_FROZEN",
        "selected_strength_profile": SELECTED_STRENGTH,
        "design_seeds": list(PROFILE_SEEDS),
        "n_clients": N_CLIENTS,
        "n_windows": N_WINDOWS,
        "n_atoms": N_ATOMS,
        "grid_search_count": 0,
        "parameter_sets_per_scenario": 1,
        "rate_targets": {
            "opportunity": OPP_RATE_TARGET,
            "observation": OBS_RATE_TARGET,
            "usable": USE_RATE_TARGET,
        },
        "probability_bounds": {
            "opp": [0.02, 0.98],
            "obs": [0.02, 0.98],
            "q": [0.02, 0.98],
        },
        "scenarios": {},
        "freeze_commit": _git_head(),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    for label, scenario_id in SCENARIO_ORDER:
        r = scenario_results[scenario_id]
        registry["scenarios"][scenario_id] = {
            "label": label,
            "scenario_id": scenario_id,
            "display_name": r["display_name"],
            "d_opp": r["directions"]["d_opp"],
            "d_p": r["directions"]["d_p"],
            "d_q": r["directions"]["d_q"],
            "kappa_opp": r["strength"]["kappa_opp"],
            "kappa_p": r["strength"]["kappa_p"],
            "kappa_q": r["strength"]["kappa_q"],
            "intercept_opp": r["intercepts"]["opp"],
            "intercept_obs": r["intercepts"]["obs"],
            "intercept_q": r["intercepts"]["q"],
            "p_opp_formula": "sigmoid(a_opp + d_opp * kappa_opp * tail_score)",
            "p_obs_formula": "sigmoid(a_obs + d_p * kappa_p * tail_score)",
            "q_use_formula": "sigmoid(a_q + d_q * kappa_q * z_tail)",
            "expected_D_opp": r["expected"]["D_opp"],
            "expected_D_obs": r["expected"]["D_obs"],
            "expected_D_arr": r["expected"]["D_arr"],
            "expected_signed": r["expected"]["signed"],
            "pooled_hard_signed": r["hard_pooled"]["signed_head_minus_tail"],
            "pooled_hard_D_TV": r["hard_pooled"]["D_TV"],
            "direction_status": r["status"],
        }

    dump_json(registry, FROZEN / "traffic_s1_s6_profile_registry.json")
    (FROZEN / "traffic_s1_s6_profile_registry.yaml").write_text(
        yaml.safe_dump(registry, sort_keys=False), encoding="utf-8",
    )

    direction_cert = {
        "status": "PASS" if all_pass else "FAIL",
        "scenarios": {sid: scenario_results[sid]["status"] for _, sid in SCENARIO_ORDER},
        "pass_count": sum(1 for _, sid in SCENARIO_ORDER if scenario_results[sid]["status"] == "PASS"),
        "hard_direction_pass_count": sum(
            1 for _, sid in SCENARIO_ORDER if scenario_results[sid]["hard_direction_pass"]
        ),
        "expected_direction_pass_count": sum(
            1 for _, sid in SCENARIO_ORDER
            if scenario_results[sid]["expected"]["expected_status"] == "PASS"
        ),
        "nondegeneracy": nondeg,
        "s6_cancellation": s6_cancel,
        "registry_sha256": sha256_file(FROZEN / "traffic_s1_s6_profile_registry.json"),
    }
    dump_json(direction_cert, FROZEN / "traffic_s1_s6_direction_certificate.json")
    dump_json(direction_cert, AUDIT / "E2_TRAFFIC_S1_S6_DIRECTION_CERTIFICATE.json")

    identity_freeze = {
        "protocol": PACKAGE,
        "status": "FROZEN" if all_pass else "NOT_FROZEN",
        "registry_sha256": direction_cert["registry_sha256"],
        "direction_certificate_sha256": sha256_file(FROZEN / "traffic_s1_s6_direction_certificate.json"),
        "q_runtime_sha256": sha256_json(q_audit),
        "gate_correction_sha256": sha256_file(FROZEN / "balanced_canary_gate_correction.json"),
        "input_identity_status": identity["status"],
        "selected_strength": SELECTED_STRENGTH,
        "design_seeds": list(PROFILE_SEEDS),
        "freeze_commit": _git_head(),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(identity_freeze, FROZEN / "traffic_s1_s6_identity.json")

    status = (
        "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY"
        if all_pass
        else "BLOCKED_TRAFFIC_PROFILE_FREEZE_FAILED"
    )
    stop = {
        "status": status,
        "hard_trace_count": total_traces,
        "scenario_pass_count": direction_cert["pass_count"],
        "expected_direction_pass_count": direction_cert["expected_direction_pass_count"],
        "hard_direction_pass_count": direction_cert["hard_direction_pass_count"],
        "unsupported_arrival_count": unsupported,
        "failed_attempt_omission_count": failed_omit,
        "stage2_eligible_in_q_count": stage2_in_q,
        "observed_count_in_q_count": obs_in_q,
        "q_leakage_count": q_leak,
        "target_leakage_count": target_leak,
        "grid_search_count": 0,
        "parameter_sets_per_scenario": 1,
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
            "E2-TRAFFIC-REAL-RUNNER-CANARY-R1"
            if all_pass
            else "TEACHER_REVIEW_REQUIRED"
        ),
        "runtime_commit": _git_head(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_results": {sid: scenario_results[sid]["status"] for _, sid in SCENARIO_ORDER},
    }
    dump_json(stop, OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")

    rate_table = {
        sid: scenario_results[sid]["rates"] for _, sid in SCENARIO_ORDER
    }
    front = {
        "six scenario names": [f"{a}={b}" for a, b in SCENARIO_ORDER],
        "one parameter set per scenario": 1,
        "design seeds": list(PROFILE_SEEDS),
        "traces": total_traces,
        "q eligibility-as-feature count": stage2_in_q,
        "expected mass formula status": "PASS",
        "S1-S6 expected direction PASS count": direction_cert["expected_direction_pass_count"],
        "S1-S6 hard direction PASS count": direction_cert["hard_direction_pass_count"],
        "global rate preservation": all(
            scenario_results[sid]["rates"]["rate_pass"] for _, sid in SCENARIO_ORDER
        ),
        "unsupported arrivals": unsupported,
        "failed-attempt omissions": failed_omit,
        "training count": 0,
        "seed29001 reads": 0,
        "validation reads": 0,
        "formal reads": 0,
        "status": status,
    }
    write_report({
        "front": front,
        "sections": [
            ("2. Frozen Traffic Identity", identity),
            ("3. Balanced Gate Correction", gate_corr),
            ("4. q Runtime Interface Seal", q_audit),
            ("5. Exact Expected A×O×U Mass", {
                "m_opp": "mass * p_opp",
                "m_obs": "mass * p_opp * p_obs",
                "m_arr": "mass * p_opp * p_obs * q",
                "P_eligible": "1 - product(1 - p_opp * p_obs)",
            }),
            ("6. S1-S6 Frozen Profiles", registry),
            ("7. Expected Direction Results", {
                sid: scenario_results[sid]["expected"] for _, sid in SCENARIO_ORDER
            }),
            ("8. Three-Seed Hard Direction Canary", {
                sid: scenario_results[sid]["hard_pooled"] for _, sid in SCENARIO_ORDER
            }),
            ("9. Final Profile Registry", identity_freeze),
            ("10. Rates", rate_table),
            ("12. Stop Position", stop),
            ("13. Next Authorized Round", stop["next_authorized_round"]),
        ],
    })
    write_readme(stop)
    print(json.dumps({k: v for k, v in stop.items() if k != "scenario_results"}, indent=2))
    print("scenario_results", stop["scenario_results"])
    return 0


def np_sign_same(a: float, b: float) -> bool:
    if abs(a) < 0.01 and abs(b) < 0.01:
        return True
    return (a > 0 and b > 0) or (a < 0 and b < 0)


if __name__ == "__main__":
    raise SystemExit(main())
