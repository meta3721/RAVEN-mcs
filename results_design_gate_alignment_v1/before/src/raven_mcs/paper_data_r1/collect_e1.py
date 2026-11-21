"""Collect E1 balanced / no-harm sealed evidence into paper_ready_r1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import (
    MISSING,
    VALID,
    canon_method,
    copy_file,
    read_csv,
    read_json,
    sha256_file,
    write_csv,
    write_json,
    write_text,
)


E1_SOURCES = {
    "per_seed": "outputs/aggregate/E1_R2/per_seed_metrics.csv",
    "aggregate_summary": "outputs/aggregate/E1_R2/aggregate_summary.json",
    "gate_report": "outputs/aggregate/E1_R2/E1_FORMAL_GATE_REPORT.json",
    "no_harm_summary": "outputs/statistics/E1_R2_FINAL_SEALED/no_harm_summary.json",
    "holm": "outputs/statistics/E1_R2_FINAL_SEALED/holm_results.csv",
    "wilcoxon": "outputs/statistics/E1_R2_FINAL_SEALED/wilcoxon_results.csv",
    "table_main": "outputs/paper/E1_R2_FINAL/tables/table_e1_main_metrics.csv",
    "table_no_harm": "outputs/paper/E1_R2_FINAL/tables/table_e1_no_harm.csv",
    "table_per_seed": "outputs/paper/E1_R2_FINAL/tables/table_e1_per_seed_rmse_mu.csv",
    "stats_report": "outputs/statistics/E1_R2_FINAL_SEALED/statistics_report.md",
}


def collect_e1(root: Path, paper: Path, missing: list[dict[str, Any]]) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    raw = paper / "03_raw_evidence" / "e1"
    core = paper / "01_core_data" / "e1"
    stats = paper / "04_statistics"
    prov = paper / "05_provenance"
    raw.mkdir(parents=True, exist_ok=True)
    core.mkdir(parents=True, exist_ok=True)

    found: dict[str, str] = {}
    for key, rel in E1_SOURCES.items():
        src = root / rel
        if src.is_file():
            dst = raw / Path(rel).name
            copy_file(src, dst)
            found[key] = rel
        else:
            missing.append(
                {
                    "item": f"E1_source:{key}",
                    "round": "E1",
                    "dataset": "Balanced",
                    "method": "",
                    "seed": "",
                    "expected_source": rel,
                    "importance": "CORE" if key in {"per_seed", "no_harm_summary", "holm"} else "SUPPORTING",
                    "can_be_reconstructed_offline": "false",
                    "requires_new_experiment": "true" if key == "per_seed" else "false",
                    "recommended_action": "Locate sealed E1 package or document absence",
                }
            )

    runs_rows: list[dict[str, Any]] = []
    paired_rows: list[dict[str, Any]] = []
    if "per_seed" in found:
        for r in read_csv(root / found["per_seed"]):
            method = canon_method(r.get("method", ""))
            row = {
                "dataset": "Balanced",
                "scenario": "balanced_no_harm",
                "method": method,
                "method_raw": r.get("method", ""),
                "seed": r.get("seed", ""),
                "logical_run_id": r.get("run_id", ""),
                "RMSE_mu": r.get("RMSE_mu", ""),
                "MAE_mu": r.get("MAE_mu", "") or "",
                "Tail_RMSE": r.get("Tail_RMSE", ""),
                "Delta_group": r.get("Delta_group", ""),
                "Delta_c_s": r.get("Delta_c_s", ""),
                "RMSE_rho": r.get("RMSE_rho", ""),
                "runtime": r.get("runtime", ""),
                "EventTrace_hash": r.get("event_trace_hash", "") or r.get("data_hash", ""),
                "source_revision": "",
                "accepted": "True",
                "validity_label": VALID,
                "comparison_class": "SCI_COMPARABLE_MAIN",
                "paper_role": "E1_balanced_no_harm_sanity",
                "source_file": found["per_seed"],
                "MAE_mu_status": MISSING if not r.get("MAE_mu") else VALID,
                "notes": "E1_R2_FINAL_SEALED aggregate per-seed metrics",
            }
            runs_rows.append(row)
            paired_rows.append(
                {
                    "dataset": "Balanced",
                    "seed": r.get("seed", ""),
                    "method": method,
                    "RMSE_mu": r.get("RMSE_mu", ""),
                    "Tail_RMSE": r.get("Tail_RMSE", ""),
                    "Delta_group": r.get("Delta_group", ""),
                    "Delta_c_s": r.get("Delta_c_s", ""),
                    "RMSE_rho": r.get("RMSE_rho", ""),
                    "Gap_mis": r.get("Gap_mis", ""),
                    "source_file": found["per_seed"],
                }
            )

    write_csv(core / "E1_FINAL_VALID_RUNS.csv", runs_rows)
    write_csv(core / "E1_FINAL_PAIRED_METRICS.csv", paired_rows)

    stat_rows: list[dict[str, Any]] = []
    if "holm" in found:
        for r in read_csv(root / found["holm"]):
            rr = dict(r)
            rr["source_file"] = found["holm"]
            rr["round"] = "E1"
            stat_rows.append(rr)
    if "wilcoxon" in found:
        for r in read_csv(root / found["wilcoxon"]):
            rr = dict(r)
            rr["source_file"] = found["wilcoxon"]
            rr["round"] = "E1"
            stat_rows.append(rr)
    if "no_harm_summary" in found:
        nh = read_json(root / found["no_harm_summary"])
        write_json(stats / "E1_NO_HARM_SUMMARY.json", nh)
        # Preserve NOT_ESTABLISHED superiority evidence explicitly
        claim = "statistical_superiority_NOT_ESTABLISHED"
        if isinstance(nh, dict):
            claim = str(nh.get("claim", nh.get("status", claim)))
        stat_rows.append(
            {
                "round": "E1",
                "metric": "no_harm_summary",
                "status": claim,
                "source_file": found["no_harm_summary"],
                "notes": "Do not delete NOT_ESTABLISHED superiority evidence",
            }
        )
    write_csv(stats / "E1_FINAL_STATISTICS.csv", stat_rows)

    prov_rows = []
    for key, rel in found.items():
        src = root / rel
        prov_rows.append(
            {
                "round": "E1",
                "artifact_key": key,
                "source_path": rel,
                "sha256": sha256_file(src),
                "size_bytes": src.stat().st_size,
                "role": "sealed_e1_evidence",
            }
        )
    write_csv(prov / "E1_EVIDENCE_PROVENANCE.csv", prov_rows)

    status = {
        "round": "E1",
        "n_valid_runs": len(runs_rows),
        "sources_found": sorted(found.keys()),
        "sources_missing": [k for k in E1_SOURCES if k not in found],
        "core_complete": bool(runs_rows) and ("no_harm_summary" in found or "holm" in found),
        "notes": "E1 sealed outputs taken from outputs/aggregate/E1_R2 and outputs/statistics/E1_R2_FINAL_SEALED",
    }
    write_json(core / "E1_COLLECTION_STATUS.json", status)
    if not runs_rows:
        write_text(
            paper / "10_reports" / "E1_CORE_MISSING.md",
            "# E1 core missing\n\nNo sealed per-seed metrics located under expected E1_R2 paths.\n",
        )
    return status
