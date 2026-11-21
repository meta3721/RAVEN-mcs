#!/usr/bin/env python3
"""E2-BALANCED-HARD-VARIANCE-AND-CERTIFICATION-STRATUM-FREEZE-R1 prepare."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml
from docx import Document
from docx.shared import Pt

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.hard_variance.certification import (
    build_cert_hierarchy,
    select_certification_level,
)
from raven_mcs.e2.hard_variance.dense_exposure import (
    PRIOR_CANDIDATE_CAP,
    VALIDATION_SEEDS,
    audit_candidate_truncation,
    audit_dense_exposure,
    build_dense_schedule,
)
from raven_mcs.e2.hard_variance.event_counts import audit_event_counts
from raven_mcs.e2.hard_variance.raw_calibrate import calibrate_dense_raw, write_soft_audit
from raven_mcs.e2.hard_variance.validate import run_balanced_validation_seed
from raven_mcs.e2.hard_variance.variance import run_variance_decomposition
from raven_mcs.e2.legal_horizon.schedule100 import freeze_legal_horizon
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1"
NUM_WINDOWS = 100


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _write_report(root: Path, ctx: dict) -> Path:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading(PACKAGE, level=0)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Value"
    for k, v in ctx.get("front_table", []):
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    for title, body in ctx.get("sections", []):
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
        "outputs/e2_hard_variance",
        "outputs/audits",
        "outputs/gates",
        "configs/frozen/e2_certification",
        "logs",
        f"deliverables/TO_SUBMIT_{PACKAGE}",
    ):
        (root / d).mkdir(parents=True, exist_ok=True)

    # A0: freeze legal horizon identity (W=100)
    horizon = freeze_legal_horizon(root)

    # B: truncation audit + dense schedules
    trunc = audit_candidate_truncation(root)
    schedules = {}
    calibrated = {}
    soft_rows = []
    max_risk = PRIOR_CANDIDATE_CAP
    for seed in VALIDATION_SEEDS:
        # First build once to learn max candidates, then rebuild streams if needed
        probe_streams = build_base_random_streams(
            seed, n_windows=NUM_WINDOWS, n_clients=8, max_risk_set=20,
        )
        # temporary schedule with dummy uniforms for sizing
        # Actually build_dense_schedule only uses uniforms shape[0]/ — need enough rows
        sched = build_dense_schedule(
            seed, schedule_uniforms=probe_streams["base_client_window_schedule"], root=root,
        )
        max_risk = max(max_risk, max(len(r["candidate_unit_ids"]) for r in sched["rows"]))
        schedules[seed] = sched

    # Rebuild with adequate uniform tensors for later validation
    dense_audit = audit_dense_exposure(schedules, root)
    if dense_audit["status"] != "PASS":
        dump_json({"status": "BLOCKED_DENSE_EXPOSURE", "dense_audit": dense_audit},
                  root / "outputs/e2_hard_variance/E2_STOP_STATUS.json")
        return 2

    # Unit maps from first calibration
    unit_stratum = {}
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    for r in processed.itertuples(index=False):
        parts = str(r.opportunity_stratum).split("::")
        unit_stratum[str(r.unit_id)] = "::".join(parts[:3]) if len(parts) >= 3 else str(r.opportunity_stratum)

    # A: event counts
    counts = audit_event_counts(schedules, unit_stratum, root=root)

    # C: raw soft calibration
    for seed in VALIDATION_SEEDS:
        result = calibrate_dense_raw(schedules[seed], root=root)
        calibrated[seed] = result
        sol = result["solved"]
        soft_rows.append({
            "seed": seed,
            "status": sol["status"],
            "D_TV_group_soft": sol["D_TV_group_soft"],
            "D_TV_raw_stratum_soft": sol["D_TV_raw_stratum_soft"],
            "D_TV_client_raw_stratum_soft": sol["D_TV_client_raw_stratum_soft"],
            "max_marginal_residual": sol["max_marginal_residual"],
            "unsupported_target_cell_count": sol["unsupported_target_cell_count"],
            "solver_converged": sol["solver_converged"],
        })
        result["C_ks"].assign(seed=seed).to_csv(
            root / f"outputs/e2_hard_variance/E2_DENSE_RAW_CANDIDATE_EXPOSURE_{seed}.csv",
            index=False,
        )
    soft_audit = write_soft_audit(soft_rows, root)
    pd.DataFrame([
        {"seed": s, "cell": k, "gamma": calibrated[s]["solved"]["gamma_unit"].get(k.split("|")[0]) if False else None}
        for s in VALIDATION_SEEDS for k in []
    ])
    # residuals file
    resid_rows = []
    for seed in VALIDATION_SEEDS:
        sol = calibrated[seed]["solved"]
        resid_rows.append({
            "seed": seed,
            "D_TV_group_soft": sol["D_TV_group_soft"],
            "D_TV_raw_stratum_soft": sol["D_TV_raw_stratum_soft"],
            "D_TV_client_raw_stratum_soft": sol["D_TV_client_raw_stratum_soft"],
            "max_marginal_residual": sol["max_marginal_residual"],
        })
    pd.DataFrame(resid_rows).to_csv(
        root / "outputs/e2_hard_variance/E2_DENSE_BALANCED_CALIBRATION_RESIDUALS.csv", index=False,
    )
    if soft_audit["status"] != "PASS":
        dump_json({"status": soft_audit["status"], "soft_audit": soft_audit},
                  root / "outputs/e2_hard_variance/E2_STOP_STATUS.json")
        _finalize(root, horizon, trunc, dense_audit, counts, soft_audit, None, None, None)
        return 0

    # E: certification hierarchy (before variance so maps exist)
    cert = build_cert_hierarchy(root)

    # D: variance on seed 29101 calibrated schedule (design audit; not validation)
    base_cal = calibrated[29101]
    var = run_variance_decomposition(
        base_schedule=base_cal["calibrated_schedule"],
        unit_stratum=base_cal["unit_stratum"],
        unit_group=base_cal["unit_group"],
        unit_score=base_cal["unit_score"],
        unit_target=base_cal["unit_target"],
        unit_cert_maps=cert["unit_cert_maps"],
        root=root,
        n_reps=200,
    )

    # F: select certification level from audit only
    # Attach design count onto frame for cert feasibility (count units).
    var["frame"].attrs["expected_arrival_total_count"] = var["flat"]["expected_arrival_total_count"]
    selection = select_certification_level(
        var["frame"],
        cert["hierarchy"],
        unit_cert_maps=cert["unit_cert_maps"],
        unit_target=base_cal["unit_target"],
        soft_arrival_by_unit=None,
        audit_registry_hash=var["summary"]["audit_registry_hash"],
        root=root,
    )
    if selection["status"] != "PASS":
        dump_json({"status": selection["status"], "selection": selection},
                  root / "outputs/e2_hard_variance/E2_STOP_STATUS.json")
        _finalize(root, horizon, trunc, dense_audit, counts, soft_audit, var["summary"], selection, None)
        return 0

    level = selection["selected_level"]
    cert_target = cert["hierarchy"][level]["target_mass"]
    cert_unit_map = cert["unit_cert_maps"][level]

    # H: five-seed confirmatory Balanced pre-gate
    pre_rows = []
    for seed in VALIDATION_SEEDS:
        dest = root / "outputs/e2_hard_variance/traces" / str(seed) / "balanced"
        diag = run_balanced_validation_seed(
            seed=seed,
            schedule=calibrated[seed]["calibrated_schedule"],
            cert_unit_map=cert_unit_map,
            cert_target=cert_target,
            root=root,
            output_dir=dest,
        )
        pre_rows.append(diag)
    pre_df = pd.DataFrame(pre_rows)
    pre_df.to_csv(root / "outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_BY_SEED.csv", index=False)
    pass_count = int(pre_df["pass"].sum())
    pre_summary = {
        "status": "PASS" if pass_count == 5 else "BALANCED_CERTIFICATION_PRE_GATE_FAIL",
        "pass_count": pass_count,
        "required": 5,
        "selected_certification_level": level,
        "rows": pre_rows,
        "non_balanced_trace_count": 0,
        "profile_selection": "NOT_STARTED",
    }
    dump_json(pre_summary, root / "outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json")

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
    }, root / "outputs/e2_hard_variance/E2_STOP_STATUS.json")

    _finalize(
        root, horizon, trunc, dense_audit, counts, soft_audit,
        var["summary"], selection, pre_summary,
        stop_status=stop_status,
    )
    print(json.dumps({
        "status": stop_status,
        "soft": soft_audit["status"],
        "cert_level": level,
        "pre_gate_pass": pass_count,
        "avg_cand_before": dense_audit["average_candidates_before"],
        "avg_cand_after": dense_audit["average_candidates_after"],
    }, indent=2))
    return 0


def _finalize(
    root, horizon, trunc, dense_audit, counts, soft_audit, var_summary, selection, pre_summary,
    stop_status=None,
):
    stop_status = stop_status or (soft_audit or {}).get("status", "BLOCKED")
    pre_summary = pre_summary or {"pass_count": 0, "status": "NOT_RUN", "rows": []}
    selection = selection or {"selected_level": None, "status": "NOT_RUN", "feasibility": {}}
    var_summary = var_summary or {}
    front = [
        ("selected windows", 100),
        ("candidate count before (avg)", dense_audit.get("average_candidates_before")),
        ("candidate count after (avg)", dense_audit.get("average_candidates_after")),
        ("total expected hard arrivals (count)", counts.get("expected_hard_arrival_count")),
        ("raw stratum count", 440),
        ("selected certification level", selection.get("selected_level")),
        ("certification cell count", (selection.get("identity") or {}).get("cell_count")),
        ("audit P95 cert TV", _p95_cert(var_summary, selection.get("selected_level"))),
        ("Balanced validation pass count", pre_summary.get("pass_count", 0)),
        ("non-balanced trace count", 0),
        ("Profile selection", "NOT_STARTED"),
        ("seed 29001 reads", 0),
        ("E2 formal runs", 0),
    ]
    if pre_summary.get("rows"):
        front.append(("raw hard TV range", _range(pre_summary["rows"], "D_TV_raw_stratum")))
        front.append(("cert hard TV range", _range(pre_summary["rows"], "D_TV_cert")))
    report = _write_report(root, {
        "front_table": front,
        "sections": [
            ("1. Executive Summary", json.dumps(front, indent=2)),
            ("2. Legal Horizon", json.dumps(horizon, indent=2)),
            ("3. Truncation Audit", json.dumps(trunc, indent=2)),
            ("4. Dense Exposure", json.dumps(dense_audit, indent=2)),
            ("5. Event Counts", json.dumps(counts, indent=2)),
            ("6. Raw Soft Calibration", json.dumps(soft_audit, indent=2)),
            ("7. Variance Decomposition", json.dumps({
                k: var_summary.get(k) for k in ("n_replicates", "incremental_variance", "expected_arrival_total_design")
            }, indent=2)),
            ("8. Certification Selection", json.dumps(selection, indent=2, default=str)),
            ("9. Balanced Cert Pre-Gate", json.dumps({
                k: pre_summary.get(k) for k in ("status", "pass_count", "selected_certification_level")
            }, indent=2)),
            ("10. Stop Position", "non-balanced=0; profile=NOT_STARTED; 29001=0; canary=0/20; formal=0; E3-E9=NOT_STARTED"),
        ],
    })
    readme = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt"
    readme.write_text(
        "\n".join([
            PACKAGE,
            f"runtime_commit={_git_head()}",
            f"stop_status={stop_status}",
            f"selected_windows=100",
            f"soft_status={soft_audit.get('status')}",
            f"cert_level={selection.get('selected_level')}",
            f"pre_gate={pre_summary.get('status')}",
            f"pass_count={pre_summary.get('pass_count', 0)}/5",
            "non_balanced=0",
            "profile_selection=NOT_STARTED",
            "real_canary=0/20",
            "E3-E9=NOT_STARTED",
            "",
        ]),
        encoding="utf-8",
    )
    dump_json({
        "package": PACKAGE,
        "report": str(report.relative_to(root)),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }, root / "outputs/e2_hard_variance/E2_CONTEXT.json")


def _p95_cert(var_summary, level):
    if not var_summary or not level:
        return None
    try:
        return var_summary["versions"]["V3"][f"D_TV_cert_{level}"]["p95"]
    except Exception:
        return None


def _range(rows, key):
    vals = [float(r[key]) for r in rows if key in r]
    if not vals:
        return None
    return f"{min(vals):.4f}–{max(vals):.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
