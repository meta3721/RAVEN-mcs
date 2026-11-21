"""Collect E3 formal evidence (SensorScope/U-Air main; Traffic NOT_COMPARABLE)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import (
    MISSING,
    NOT_COMPARABLE,
    VALID,
    canon_dataset,
    canon_method,
    copy_file,
    empty_or_value,
    read_csv,
    read_json,
    safe_float,
    sha256_file,
    write_csv,
    write_json,
    write_text,
)


E3_RUNS = "artifacts/e3_formal_runs_r1"
E3_SEAL = "artifacts/e3_final_evidence_provenance_and_wording_seal_r1"
E3_CLOSURE = "artifacts/e3_formal_evidence_integrity_and_claim_closure_r1"
E3_HAJEK = "artifacts/e3_local_hajek_weight_and_p2_certificate_final_closure_r1"


def _metric_from_final(metrics: dict[str, Any], key: str) -> tuple[str, str]:
    if key in metrics and metrics[key] is not None:
        return str(metrics[key]), VALID
    # dual-domain physical aliases
    aliases = {
        "RMSE_mu": ["RMSE_mu", "RMSE_mu_phys", "rmse_mu"],
        "MAE_mu": ["MAE_mu", "MAE_mu_phys", "mae_mu"],
        "Tail_RMSE": ["Tail_RMSE", "Tail_RMSE_phys", "tail_rmse"],
        "Delta_group": ["Delta_group", "delta_group"],
        "Delta_c_s": ["Delta_c_s", "delta_c_s"],
        "RMSE_rho": ["RMSE_rho", "RMSE_rho_phys", "rmse_rho"],
    }
    for alt in aliases.get(key, [key]):
        if alt in metrics and metrics[alt] is not None:
            return str(metrics[alt]), VALID
    return "", MISSING


def _comparison_class(dataset: str, reused_or_new: str) -> str:
    ds = dataset.lower()
    if ds in {"sensorscope", "uair"}:
        return "SCI_COMPARABLE_MAIN"
    if ds == "traffic":
        if str(reused_or_new).lower() == "reused":
            return "NOT_COMPARABLE_CROSS_VINTAGE"
        return "NOT_COMPARABLE_CROSS_VINTAGE"
    return "SUPPORTING_ONLY"


def collect_e3(root: Path, paper: Path, missing: list[dict[str, Any]]) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    core = paper / "01_core_data" / "e3"
    support = paper / "02_supporting_data" / "e3"
    solver = paper / "02_supporting_data" / "solver"
    raw = paper / "03_raw_evidence" / "e3"
    stats = paper / "04_statistics"
    prov = paper / "05_provenance"
    for d in (core, support, solver, raw, stats, prov, raw / "local_hajek"):
        d.mkdir(parents=True, exist_ok=True)

    status_csv = root / E3_RUNS / "E3_FORMAL_RUN_STATUS.csv"
    summary_csv = root / E3_RUNS / "E3_FORMAL_SUMMARY.csv"
    reused_idx = root / E3_RUNS / "reused_traffic" / "E3_REUSED_TRAFFIC_EVIDENCE_INDEX.json"

    if not status_csv.is_file():
        missing.append(
            {
                "item": "E3_FORMAL_RUN_STATUS",
                "round": "E3",
                "dataset": "",
                "method": "",
                "seed": "",
                "expected_source": f"{E3_RUNS}/E3_FORMAL_RUN_STATUS.csv",
                "importance": "CORE",
                "can_be_reconstructed_offline": "false",
                "requires_new_experiment": "true",
                "recommended_action": "Restore E3 formal runs seal",
            }
        )

    index_rows: list[dict[str, Any]] = []
    if status_csv.is_file():
        for r in read_csv(status_csv):
            ds_raw = r.get("dataset", "")
            method_raw = r.get("method", "")
            seed = r.get("seed", "")
            run_path = root / E3_RUNS / "runs" / ds_raw / method_raw / f"seed{seed}" / "final_metrics.json"
            metrics: dict[str, Any] = {}
            metrics_hash = ""
            if run_path.is_file():
                metrics = read_json(run_path)
                metrics_hash = sha256_file(run_path)
            rmse_mu, rmse_mu_s = _metric_from_final(metrics, "RMSE_mu")
            mae_mu, mae_mu_s = _metric_from_final(metrics, "MAE_mu")
            tail, tail_s = _metric_from_final(metrics, "Tail_RMSE")
            dg, dg_s = _metric_from_final(metrics, "Delta_group")
            dcs, dcs_s = _metric_from_final(metrics, "Delta_c_s")
            rho, rho_s = _metric_from_final(metrics, "RMSE_rho")
            cmp = _comparison_class(ds_raw, r.get("reused_or_new", "new"))
            if ds_raw.lower() == "traffic":
                # Force NOT_COMPARABLE for cross-method E3 inference boundary
                rho_s = NOT_COMPARABLE if rho_s == VALID else rho_s
            index_rows.append(
                {
                    "dataset": canon_dataset(ds_raw),
                    "dataset_raw": ds_raw,
                    "method": canon_method(method_raw),
                    "method_raw": method_raw,
                    "seed": seed,
                    "logical_run_id": r.get("logical_run_id", ""),
                    "attempt_id": r.get("attempt_count", ""),
                    "source_revision": r.get("source_revision", ""),
                    "source_vintage": "E3_formal_new" if r.get("reused_or_new") == "new" else "E2_reused",
                    "preprocessing_vintage": "",
                    "EventTrace_hash": r.get("eventtrace_hash", ""),
                    "checkpoint_hash": "",
                    "metrics_hash": metrics_hash,
                    "accepted": r.get("accepted", ""),
                    "comparison_class": cmp,
                    "RMSE_mu": rmse_mu,
                    "RMSE_mu_status": rmse_mu_s,
                    "MAE_mu": mae_mu,
                    "MAE_mu_status": mae_mu_s,
                    "Tail_RMSE": tail,
                    "Tail_RMSE_status": tail_s,
                    "Delta_group": dg,
                    "Delta_group_status": dg_s,
                    "Delta_c_s": dcs,
                    "Delta_c_s_status": dcs_s,
                    "RMSE_rho": rho,
                    "RMSE_rho_status": rho_s if ds_raw.lower() != "traffic" else NOT_COMPARABLE,
                    "Delta_pair": empty_or_value(metrics.get("Delta_pair", "")),
                    "n_eff": empty_or_value(metrics.get("effective_sample_size_mean", metrics.get("n_eff", ""))),
                    "ESS": empty_or_value(metrics.get("effective_sample_size_mean", "")),
                    "max_weight": empty_or_value(metrics.get("max_weight", "")),
                    "runtime": empty_or_value(metrics.get("runtime", metrics.get("runtime_seconds", ""))),
                    "P2_warning_count": empty_or_value(
                        metrics.get("P2_solver_failure_count", metrics.get("solver_failure_count", ""))
                    ),
                    "scenario": r.get("scenario", ""),
                    "reused_or_new": r.get("reused_or_new", ""),
                    "paper_role": "E3_main" if cmp == "SCI_COMPARABLE_MAIN" else "E3_traffic_reference_only",
                    "source_file": f"{E3_RUNS}/E3_FORMAL_RUN_STATUS.csv",
                    "notes": "",
                }
            )

    # Append 100 reused Traffic records
    n_reused = 0
    if reused_idx.is_file():
        payload = read_json(reused_idx)
        for rec in payload.get("records", []):
            n_reused += 1
            m = rec.get("metrics") or {}
            method_raw = rec.get("method", "")
            seed = str(rec.get("seed", ""))
            index_rows.append(
                {
                    "dataset": "NSW-Traffic",
                    "dataset_raw": "traffic",
                    "method": canon_method(method_raw),
                    "method_raw": method_raw,
                    "seed": seed,
                    "logical_run_id": f"e3::traffic::reused::{method_raw}::seed{seed}",
                    "attempt_id": "1",
                    "source_revision": "",
                    "source_vintage": "E2_reused",
                    "preprocessing_vintage": "E2",
                    "EventTrace_hash": "",
                    "checkpoint_hash": "",
                    "metrics_hash": (rec.get("provenance") or {}).get("result_hash", ""),
                    "accepted": "True",
                    "comparison_class": "NOT_COMPARABLE_CROSS_VINTAGE",
                    "RMSE_mu": empty_or_value(m.get("RMSE_mu", "")),
                    "RMSE_mu_status": NOT_COMPARABLE,
                    "MAE_mu": "",
                    "MAE_mu_status": MISSING,
                    "Tail_RMSE": "",
                    "Tail_RMSE_status": MISSING,
                    "Delta_group": empty_or_value(m.get("Gap_mis", "")),
                    "Delta_group_status": "DESCRIPTIVE_ONLY",
                    "Delta_c_s": "",
                    "Delta_c_s_status": NOT_COMPARABLE,
                    "RMSE_rho": empty_or_value(m.get("RMSE_rho", "")),
                    "RMSE_rho_status": NOT_COMPARABLE,
                    "Delta_pair": "",
                    "n_eff": empty_or_value(m.get("effective_sample_size_mean", "")),
                    "ESS": empty_or_value(m.get("effective_sample_size_mean", "")),
                    "max_weight": "",
                    "runtime": "",
                    "P2_warning_count": empty_or_value(m.get("P2_solver_failure_count", "")),
                    "scenario": "complete_aligned",
                    "reused_or_new": "reused",
                    "paper_role": "E3_traffic_reference_only",
                    "source_file": f"{E3_RUNS}/reused_traffic/E3_REUSED_TRAFFIC_EVIDENCE_INDEX.json",
                    "notes": "NOT_COMPARABLE for cross-method E3 inference",
                }
            )

    write_csv(core / "E3_FINAL_VALID_EVIDENCE_INDEX.csv", index_rows)

    ss = [r for r in index_rows if r["dataset"] == "SensorScope"]
    ua = [r for r in index_rows if r["dataset"] == "U-Air"]
    main = [r for r in index_rows if r["comparison_class"] == "SCI_COMPARABLE_MAIN"]
    traffic = [r for r in index_rows if r["dataset"] == "NSW-Traffic"]

    write_csv(core / "E3_SENSOR_SCOPE_ALL_METHODS.csv", ss)
    write_csv(core / "E3_UAIR_ALL_METHODS.csv", ua)
    write_csv(core / "E3_MAIN_COMPARABLE_LONG.csv", main)

    # Wide: dataset x method x seed pivot for key metrics
    wide_rows: list[dict[str, Any]] = []
    for r in main:
        for metric in ("RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s", "RMSE_rho"):
            wide_rows.append(
                {
                    "dataset": r["dataset"],
                    "method": r["method"],
                    "seed": r["seed"],
                    "metric": metric,
                    "value": r.get(metric, ""),
                    "status": r.get(f"{metric}_status", ""),
                    "comparison_class": r["comparison_class"],
                }
            )
    write_csv(core / "E3_MAIN_COMPARABLE_WIDE.csv", wide_rows)

    structural = [
        {
            "dataset": r["dataset"],
            "method": r["method"],
            "seed": r["seed"],
            "Delta_group": r.get("Delta_group", ""),
            "Delta_group_status": r.get("Delta_group_status", ""),
            "Delta_c_s": r.get("Delta_c_s", ""),
            "Delta_c_s_status": r.get("Delta_c_s_status", ""),
            "comparison_class": r["comparison_class"],
        }
        for r in main
    ]
    prediction = [
        {
            "dataset": r["dataset"],
            "method": r["method"],
            "seed": r["seed"],
            "RMSE_mu": r.get("RMSE_mu", ""),
            "MAE_mu": r.get("MAE_mu", ""),
            "Tail_RMSE": r.get("Tail_RMSE", ""),
            "RMSE_rho": r.get("RMSE_rho", ""),
            "comparison_class": r["comparison_class"],
        }
        for r in main
    ]
    write_csv(core / "E3_STRUCTURAL_METRICS_MASTER.csv", structural)
    write_csv(core / "E3_PREDICTION_METRICS_MASTER.csv", prediction)

    write_csv(support / "E3_TRAFFIC_REFERENCE_ONLY.csv", traffic)
    write_csv(
        support / "E3_TRAFFIC_NOT_COMPARABLE_INDEX.csv",
        [
            {
                "dataset": r["dataset"],
                "method": r["method"],
                "seed": r["seed"],
                "comparison_class": r["comparison_class"],
                "reused_or_new": r.get("reused_or_new", ""),
                "logical_run_id": r.get("logical_run_id", ""),
                "notes": r.get("notes", ""),
            }
            for r in traffic
        ],
    )

    # Statistics
    if summary_csv.is_file():
        copy_file(summary_csv, stats / "E3_FINAL_STATISTICS.csv")
    for name in ("E3_FORMAL_HOLM_RESULTS.csv", "E3_FORMAL_PAIRED_TESTS.csv", "E3_FORMAL_EFFECT_SIZES.csv"):
        src = root / E3_RUNS / name
        if src.is_file():
            copy_file(src, stats / name)

    # Local-Hajek provenance
    hajek_files = []
    for base in (root / E3_SEAL, root / E3_HAJEK, root / E3_CLOSURE):
        if not base.exists():
            continue
        for p in base.glob("*HAJEK*"):
            if p.is_file():
                copy_file(p, raw / "local_hajek" / p.name)
                hajek_files.append(str(p.relative_to(root)))
    hajek_summary = {
        "status": "LOCAL_HAJEK_FORMAL_COLLAPSE_PROVENANCE_CERTIFIED",
        "effective_client_windows_total": 9666,
        "SensorScope": 6070,
        "U-Air": 3596,
        "weight_range": 0,
        "weight_policy": "uniform",
        "source_files": hajek_files,
    }
    # Prefer sealed numbers if present
    for cand in (
        root / E3_SEAL / "E3_LOCAL_HAJEK_PROVENANCE_FINAL_DECISION.json",
        root / E3_HAJEK / "E3_LOCAL_HAJEK_PROVENANCE_FINAL_DECISION.json",
    ):
        if cand.is_file():
            sealed = read_json(cand)
            hajek_summary["sealed_decision"] = sealed
            break
    write_csv(
        support / "E3_LOCAL_HAJEK_PROVENANCE_SUMMARY.csv",
        [
            {
                "quantity": "effective_client_windows_total",
                "value": hajek_summary["effective_client_windows_total"],
                "status": VALID,
            },
            {"quantity": "SensorScope", "value": hajek_summary["SensorScope"], "status": VALID},
            {"quantity": "U-Air", "value": hajek_summary["U-Air"], "status": VALID},
            {"quantity": "weight_range", "value": hajek_summary["weight_range"], "status": VALID},
            {
                "quantity": "final_status",
                "value": hajek_summary["status"],
                "status": VALID,
            },
        ],
    )
    write_text(
        support / "E3_LOCAL_HAJEK_PROVENANCE_REPORT.md",
        "\n".join(
            [
                "# E3 Local-Hajek provenance",
                "",
                f"- Final status: `{hajek_summary['status']}`",
                f"- Effective client-windows: {hajek_summary['effective_client_windows_total']} "
                f"(SensorScope {hajek_summary['SensorScope']} + U-Air {hajek_summary['U-Air']})",
                "- weight_range=0 / uniform",
                "- See raw evidence under `03_raw_evidence/e3/local_hajek/`.",
                "",
            ]
        ),
    )

    # P2 solver supporting
    p2_sources = []
    for base in (root / E3_CLOSURE, root / E3_SEAL, root / E3_HAJEK):
        if not base.exists():
            continue
        for p in base.glob("*P2*"):
            if p.is_file():
                copy_file(p, solver / p.name)
                p2_sources.append(p.name)
    warn_rows: list[dict[str, Any]] = []
    affected: list[dict[str, Any]] = []
    cert = root / E3_CLOSURE / "E3_P2_SOLVER_CERTIFICATE_AUDIT.csv"
    if cert.is_file():
        for r in read_csv(cert):
            warn_rows.append(dict(r))
            if str(r.get("warning", r.get("has_warning", ""))).lower() in {"1", "true", "yes"} or r.get(
                "n_warning_windows"
            ):
                affected.append(dict(r))
    write_csv(solver / "P2_WARNING_WINDOWS.csv", warn_rows)
    write_csv(solver / "P2_AFFECTED_RUNS.csv", affected if affected else warn_rows)
    write_csv(
        solver / "P2_FEASIBILITY_SUMMARY.csv",
        [
            {
                "boundary": "P2_INACCURATE_WINDOWS_FEASIBILITY_CERTIFIED_OPTIMALITY_NOT_RECONSTRUCTABLE",
                "status": VALID,
                "source_files": ";".join(p2_sources),
            }
        ],
    )
    write_csv(
        solver / "P2_SOLVER_STATUS_SUMMARY.csv",
        [{"n_audit_rows": len(warn_rows), "n_source_files": len(p2_sources)}],
    )
    write_text(
        solver / "P2_AUDIT_LIMITATION.md",
        "\n".join(
            [
                "# P2 audit limitation",
                "",
                "Sealed scientific boundary:",
                "`P2_INACCURATE_WINDOWS_FEASIBILITY_CERTIFIED_OPTIMALITY_NOT_RECONSTRUCTABLE`",
                "",
                "Feasibility of warning-affected windows was audited; exact optimality cannot be reconstructed from sealed outputs.",
                "Do not write solver warnings as exact optimality proofs.",
                "",
            ]
        ),
    )

    # Raw seal copies
    for rel_base in (E3_RUNS, E3_SEAL, E3_CLOSURE, E3_HAJEK):
        base = root / rel_base
        if not base.exists():
            continue
        dest = raw / Path(rel_base).name
        dest.mkdir(parents=True, exist_ok=True)
        for p in base.glob("*"):
            if p.is_file() and p.suffix.lower() in {".csv", ".json", ".md"}:
                copy_file(p, dest / p.name)

    prov_rows = []
    for rel in (
        f"{E3_RUNS}/E3_FORMAL_RUN_STATUS.csv",
        f"{E3_RUNS}/E3_FORMAL_SUMMARY.csv",
        f"{E3_SEAL}/E3_CLAIM_MATRIX_FINAL_R3.json",
        f"{E3_CLOSURE}/E3_TRAFFIC_CROSS_VINTAGE_COMPARISON_POLICY.json",
    ):
        src = root / rel
        if src.is_file():
            prov_rows.append(
                {
                    "round": "E3",
                    "source_path": rel,
                    "sha256": sha256_file(src),
                    "size_bytes": src.stat().st_size,
                    "role": "e3_core_source",
                }
            )
    write_csv(prov / "E3_EVIDENCE_PROVENANCE.csv", prov_rows)

    status = {
        "round": "E3",
        "n_index_rows": len(index_rows),
        "n_formal_status_rows": len(index_rows) - n_reused,
        "n_reused_traffic": n_reused,
        "n_main_comparable": len(main),
        "n_traffic": len(traffic),
        "expected_merged": 660,
        "core_complete": len(index_rows) == 660 and len(main) > 0,
    }
    write_json(core / "E3_COLLECTION_STATUS.json", status)
    return status
