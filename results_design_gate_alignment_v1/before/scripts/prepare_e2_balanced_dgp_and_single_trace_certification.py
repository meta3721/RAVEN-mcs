#!/usr/bin/env python3
"""E2-BALANCED-DGP-AND-SINGLE-TRACE-CERTIFICATION-REPAIR-R1 prepare."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.balanced_dgp.bounded_schedule import (
    VALIDATION_SEEDS,
    audit_bounded_schedules,
    build_bounded_schedule,
)
from raven_mcs.e2.balanced_dgp.certification import build_cert_hierarchy, select_certification_level
from raven_mcs.e2.balanced_dgp.event_mass import audit_event_mass_semantics
from raven_mcs.e2.balanced_dgp.opp_calibrate import (
    calibrate_opportunity_probabilities,
    write_opp_calibration_outputs,
)
from raven_mcs.e2.balanced_dgp.spatial import load_e1_client_spatial_identity
from raven_mcs.e2.balanced_dgp.tombstone import write_prior_tombstone
from raven_mcs.e2.balanced_dgp.validate_single import run_single_trace_validation_seed
from raven_mcs.e2.balanced_dgp.variance_single import run_single_arm_variance
from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.legal_horizon.schedule100 import freeze_legal_horizon
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1"
NUM_WINDOWS = 100


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _write_report(root: Path, front: list[tuple], sections: list[tuple]) -> Path:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading(PACKAGE, level=0)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Value"
    for k, v in front:
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    for title, body in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(str(body))
    out = root / f"deliverables/TO_SUBMIT_{PACKAGE}"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{PACKAGE}_REPORT.docx"
    doc.save(path)
    return path


def main() -> int:
    root = ROOT
    for d in (
        "outputs/e2_balanced_dgp",
        "outputs/audits",
        "outputs/gates",
        "configs/frozen/e2_dgp_certification",
        "logs",
        f"deliverables/TO_SUBMIT_{PACKAGE}",
    ):
        (root / d).mkdir(parents=True, exist_ok=True)

    write_prior_tombstone(root)
    horizon = freeze_legal_horizon(root)

    schedules = {}
    max_risk = 20
    for seed in VALIDATION_SEEDS:
        streams = build_base_random_streams(seed, n_windows=NUM_WINDOWS, n_clients=8, max_risk_set=20)
        sched = build_bounded_schedule(
            seed, schedule_uniforms=streams["base_client_window_schedule"], root=root,
        )
        max_risk = max(max_risk, max(len(r["candidate_unit_ids"]) for r in sched["rows"]))
        schedules[seed] = sched
        dump_json(sched["audit"], root / f"outputs/e2_balanced_dgp/E2_BOUNDED_SCHEDULE_AUDIT_{seed}.json")

    bounded = audit_bounded_schedules(schedules, root)
    if bounded["status"] != "PASS":
        dump_json({"status": "BLOCKED_BOUNDED_CANDIDATE_WINDOWS", "bounded": bounded},
                  root / "outputs/e2_balanced_dgp/E2_STOP_STATUS.json")
        return 2

    mass_audit = audit_event_mass_semantics(schedules, root=root)
    if mass_audit["status"] != "PASS":
        dump_json({"status": "BLOCKED_EVENT_MASS_SEMANTICS", "mass": mass_audit},
                  root / "outputs/e2_balanced_dgp/E2_STOP_STATUS.json")
        return 2

    calibrated = {}
    soft_rows = []
    prob_frames = []
    for seed in VALIDATION_SEEDS:
        result = calibrate_opportunity_probabilities(schedules[seed], root=root)
        calibrated[seed] = result
        sol = result["solved"]
        soft_rows.append({"seed": seed, **{k: sol[k] for k in (
            "status", "D_TV_group_soft", "D_TV_raw_stratum_soft", "D_TV_client_raw_stratum_soft",
            "p_opp_min", "p_opp_max", "p_opp_mean", "p_opp_std", "opportunity_rate_error",
            "max_marginal_residual", "unsupported_target_cell_count", "solver_converged",
        )}})
        detail = result["detail"].copy()
        detail["seed"] = seed
        detail["p_opp"] = result["p_opp"]
        detail["calibration_weight"] = result["weights"]
        detail["event_mass"] = 1.0
        prob_frames.append(detail)

    soft_audit = write_opp_calibration_outputs(soft_rows, prob_frames, root)
    if soft_audit["status"] != "PASS":
        dump_json({"status": soft_audit["status"], "soft": soft_audit},
                  root / "outputs/e2_balanced_dgp/E2_STOP_STATUS.json")
        _finalize(root, horizon, bounded, mass_audit, soft_audit, None, None, None)
        return 0

    spatial = load_e1_client_spatial_identity(root)
    if spatial["audit"]["status"] != "PASS":
        dump_json({"status": "BLOCKED_NO_VALID_SPATIAL_IDENTITY", "spatial": spatial["audit"]},
                  root / "outputs/e2_balanced_dgp/E2_STOP_STATUS.json")
        return 2

    cert = build_cert_hierarchy(root)
    base = calibrated[29101]
    var = run_single_arm_variance(
        base_schedule=base["calibrated_schedule"],
        unit_stratum=base["unit_stratum"],
        unit_group=base["unit_group"],
        unit_score=base["unit_score"],
        unit_target=base["unit_target"],
        unit_cert_maps=cert["unit_cert_maps"],
        root=root,
        n_reps=200,
    )
    selection = select_certification_level(
        var["frame"],
        cert["hierarchy"],
        expected_arrival_total_count=var["expected_arrival_total_count"],
        audit_registry_hash=var["summary"]["audit_registry_hash"],
        root=root,
    )
    if selection["status"] != "PASS":
        dump_json({
            "status": selection["status"],
            "soft_status": soft_audit["status"],
            "cert_selection": selection["status"],
            "pre_gate": "NOT_RUN",
            "non_balanced_trace_count": 0,
            "profile_selection": "NOT_STARTED",
            "max_risk_set_used": max_risk,
            "antithetic_used_for_selection": False,
            "antithetic_used_for_validation": False,
            "selection": selection,
        }, root / "outputs/e2_balanced_dgp/E2_STOP_STATUS.json")
        _finalize(
            root, horizon, bounded, mass_audit, soft_audit, var["summary"], selection, None,
            stop_status=selection["status"], spatial=spatial["audit"],
        )
        return 0

    level = selection["selected_level"]
    cert_target = cert["hierarchy"][level]["target_mass"]
    cert_unit_map = cert["unit_cert_maps"][level]
    pre_rows = []
    for seed in VALIDATION_SEEDS:
        dest = root / "outputs/e2_balanced_dgp/traces" / str(seed) / "balanced"
        diag = run_single_trace_validation_seed(
            seed=seed,
            schedule=calibrated[seed]["calibrated_schedule"],
            cert_unit_map=cert_unit_map,
            cert_target=cert_target,
            root=root,
            output_dir=dest,
        )
        pre_rows.append(diag)
    pre_df = pd.DataFrame(pre_rows)
    pre_df.to_csv(root / "outputs/e2_balanced_dgp/E2_BALANCED_SINGLE_TRACE_PRE_GATE_BY_SEED.csv", index=False)
    pass_count = int(pre_df["pass"].sum())
    pre_summary = {
        "status": "PASS" if pass_count == 5 else "BALANCED_SINGLE_TRACE_PRE_GATE_FAIL",
        "pass_count": pass_count,
        "required": 5,
        "selected_certification_level": level,
        "rows": pre_rows,
        "non_balanced_trace_count": 0,
        "profile_selection": "NOT_STARTED",
        "antithetic_arms": 1,
    }
    dump_json(pre_summary, root / "outputs/e2_balanced_dgp/E2_BALANCED_SINGLE_TRACE_PRE_GATE_SUMMARY.json")

    stop_status = (
        "READY_FOR_PROFILE_REFREEZE"
        if pre_summary["status"] == "PASS"
        else pre_summary["status"]
    )
    dump_json({
        "status": stop_status,
        "soft_status": soft_audit["status"],
        "cert_selection": selection["status"],
        "pre_gate": pre_summary["status"],
        "non_balanced_trace_count": 0,
        "profile_selection": "NOT_STARTED",
        "max_risk_set_used": max_risk,
        "antithetic_used_for_selection": False,
        "antithetic_used_for_validation": False,
    }, root / "outputs/e2_balanced_dgp/E2_STOP_STATUS.json")

    _finalize(
        root, horizon, bounded, mass_audit, soft_audit,
        var["summary"], selection, pre_summary, stop_status=stop_status,
        spatial=spatial["audit"],
    )
    print(json.dumps({
        "status": stop_status,
        "soft": soft_audit["status"],
        "cert_level": level,
        "pre_gate_pass": pass_count,
        "avg_cand": bounded["candidate_count_mean"],
        "spatial": spatial["audit"]["coordinate_source"],
    }, indent=2))
    return 0


def _finalize(
    root, horizon, bounded, mass_audit, soft_audit, var_summary, selection, pre_summary,
    stop_status=None, spatial=None,
):
    stop_status = stop_status or (soft_audit or {}).get("status", "BLOCKED")
    pre_summary = pre_summary or {"pass_count": 0, "status": "NOT_RUN", "rows": []}
    selection = selection or {"selected_level": None, "status": "NOT_RUN", "feasibility": {}}
    var_summary = var_summary or {}
    spatial = spatial or {}
    level = selection.get("selected_level")
    p95 = None
    zero_rate = None
    if var_summary and level:
        try:
            p95 = var_summary["versions"]["V3"][f"D_TV_cert_{level}"]["p95"]
            zero_rate = var_summary["versions"]["V3"][f"zero_arrival_rate_{level}"]["mean"]
        except Exception:
            pass
    front = [
        ("selected windows", 100),
        ("candidate window bound status", bounded.get("status")),
        ("future candidate count", bounded.get("future_candidate_count")),
        ("average legal candidates per window", bounded.get("candidate_count_mean")),
        ("event mass source", mass_audit.get("event_mass_source")),
        ("p_opp min/max/std", f"{soft_audit.get('p_opp_min')}/{soft_audit.get('p_opp_max')}/{soft_audit.get('p_opp_std')}"),
        ("soft group/raw/client-stratum TV",
         f"{soft_audit.get('max_D_TV_group_soft')}/{soft_audit.get('max_D_TV_raw_stratum_soft')}/{soft_audit.get('max_D_TV_client_raw_stratum_soft')}"),
        ("spatial identity source", spatial.get("coordinate_source")),
        ("synthetic coordinate usage count", spatial.get("synthetic_coordinate_usage_count", 0)),
        ("single-arm V3 P95 cert TV", p95),
        ("zero-arrival positive cell rate", zero_rate),
        ("selected certification level", level),
        ("Balanced single-trace pass count", pre_summary.get("pass_count", 0)),
        ("non-balanced trace count", 0),
        ("Profile selection", "NOT_STARTED"),
        ("seed29001 reads", 0),
        ("E2 formal runs", 0),
    ]
    if pre_summary.get("rows"):
        raws = [float(r["D_TV_raw_stratum"]) for r in pre_summary["rows"]]
        certs = [float(r["D_TV_cert"]) for r in pre_summary["rows"]]
        front.append(("raw hard TV range", f"{min(raws):.4f}–{max(raws):.4f}"))
        front.append(("cert hard TV range", f"{min(certs):.4f}–{max(certs):.4f}"))
    report = _write_report(root, front, [
        ("1. Executive Summary", json.dumps(front, indent=2, default=str)),
        ("2. Prior Tombstone", "INVALID prior CERT-L32 / antithetic / future-suffix / synthetic coords"),
        ("3. Bounded Candidates", json.dumps(bounded, indent=2)),
        ("4. Event Mass", json.dumps(mass_audit, indent=2)),
        ("5. Opportunity Probability Calibration", json.dumps({
            k: soft_audit.get(k) for k in (
                "status", "max_D_TV_group_soft", "max_D_TV_raw_stratum_soft",
                "max_D_TV_client_raw_stratum_soft", "p_opp_min", "p_opp_max", "calibration_target",
            )
        }, indent=2)),
        ("6. Spatial Identity", json.dumps(spatial, indent=2, default=str)),
        ("7. Single-Arm Variance", json.dumps({
            k: var_summary.get(k) for k in ("n_replicates", "antithetic_used", "estimator")
        }, indent=2)),
        ("8. Certification Selection", json.dumps(selection, indent=2, default=str)),
        ("9. Single-Trace Pre-Gate", json.dumps({
            k: pre_summary.get(k) for k in ("status", "pass_count", "selected_certification_level", "antithetic_arms")
        }, indent=2)),
        ("10. Stop Position", "non-balanced=0; profile=NOT_STARTED; 29001=0; canary=0/20; formal=0; E3-E9=NOT_STARTED"),
    ])
    readme = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt"
    readme.write_text("\n".join([
        PACKAGE,
        f"runtime_commit={_git_head()}",
        f"stop_status={stop_status}",
        f"selected_windows=100",
        f"soft_status={soft_audit.get('status')}",
        f"cert_level={selection.get('selected_level')}",
        f"pre_gate={pre_summary.get('status')}",
        f"pass_count={pre_summary.get('pass_count', 0)}/5",
        "antithetic_arms=1",
        "non_balanced=0",
        "profile_selection=NOT_STARTED",
        "E3-E9=NOT_STARTED",
        "",
    ]), encoding="utf-8")
    dump_json({
        "package": PACKAGE,
        "report": str(report.relative_to(root)),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }, root / "outputs/e2_balanced_dgp/E2_CONTEXT.json")


if __name__ == "__main__":
    raise SystemExit(main())
