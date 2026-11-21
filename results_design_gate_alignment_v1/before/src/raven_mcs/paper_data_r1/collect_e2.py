"""Collect E2 Traffic formal sealed evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import (
    VALID,
    canon_method,
    copy_file,
    read_csv,
    read_json,
    sha256_file,
    write_csv,
    write_json,
)


E2_RUNS = "artifacts/e2_traffic_formal_runs_r1"
E2_ANALYSIS = "artifacts/e2_traffic_formal_results_analysis_r1"
E2_SEAL = "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1"
E2_RECON = "artifacts/e2_traffic_offline_metric_reconstruction_r1"


def _copy_tree_files(src: Path, dst: Path, patterns: tuple[str, ...] = ("*.csv", "*.json", "*.md")) -> list[str]:
    copied: list[str] = []
    if not src.exists():
        return copied
    for pat in patterns:
        for p in src.glob(pat):
            if p.is_file():
                copy_file(p, dst / p.name)
                copied.append(str(p))
        for p in src.rglob(pat):
            if p.is_file() and p.parent != src:
                rel = p.relative_to(src)
                copy_file(p, dst / rel)
                copied.append(str(p))
    return copied


def collect_e2(root: Path, paper: Path, missing: list[dict[str, Any]]) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    core = paper / "01_core_data" / "e2"
    stats = paper / "04_statistics"
    prov = paper / "05_provenance"
    raw = paper / "03_raw_evidence" / "e2"
    for d in (core, stats, prov, raw):
        d.mkdir(parents=True, exist_ok=True)

    runs_dir = root / E2_RUNS
    analysis_dir = root / E2_ANALYSIS
    results_path = runs_dir / "formal_results.csv"
    et_path = runs_dir / "eventtrace_manifest.csv"
    stats_path = runs_dir / "formal_statistics.csv"
    dod_path = analysis_dir / "COMPLETE_ALIGNED_DOD.csv"
    dod_sum = analysis_dir / "COMPLETE_ALIGNED_DOD_SUMMARY.json"

    if not results_path.is_file():
        missing.append(
            {
                "item": "E2_formal_results",
                "round": "E2",
                "dataset": "NSW-Traffic",
                "method": "",
                "seed": "",
                "expected_source": str(results_path.relative_to(root)),
                "importance": "CORE",
                "can_be_reconstructed_offline": "false",
                "requires_new_experiment": "true",
                "recommended_action": "Restore sealed E2 formal_results.csv",
            }
        )

    run_rows: list[dict[str, Any]] = []
    if results_path.is_file():
        for r in read_csv(results_path):
            run_rows.append(
                {
                    "dataset": "NSW-Traffic",
                    "scenario": r.get("scenario", ""),
                    "method": canon_method(r.get("method", "")),
                    "method_raw": r.get("method", ""),
                    "method_display": r.get("method_display", ""),
                    "seed": r.get("seed", ""),
                    "logical_run_id": f"e2::{r.get('scenario')}::{r.get('method')}::seed{r.get('seed')}",
                    "attempt_id": r.get("attempt", ""),
                    "source_revision": "",
                    "EventTrace_hash": r.get("eventtrace_events_sha256", ""),
                    "RMSE_mu": r.get("RMSE_mu", ""),
                    "RMSE_rho": r.get("RMSE_rho", ""),
                    "MAE_mu": "",
                    "MAE_mu_status": "MISSING_NOT_RECORDED",
                    "Tail_RMSE": "",
                    "Tail_RMSE_status": "MISSING_NOT_RECORDED",
                    "Delta_group": "",
                    "Delta_group_status": "MISSING_NOT_RECORDED",
                    "Gap_mis": r.get("Gap_mis", ""),
                    "runtime_seconds": r.get("runtime_seconds", ""),
                    "completed_windows": r.get("completed_windows", ""),
                    "accepted": "True" if str(r.get("status", "")).lower() in {"accepted", "ok", "success", ""} else r.get("status", ""),
                    "validity_label": VALID,
                    "comparison_class": "SCI_COMPARABLE_MAIN",
                    "paper_role": "E2_risk_noninterchangeability",
                    "source_file": E2_RUNS + "/formal_results.csv",
                }
            )
        # Enrich group metrics if present
        gm = runs_dir / "formal_group_metrics.csv"
        if gm.is_file():
            by_key = {(r["seed"], r["scenario"], r["method"]): r for r in read_csv(gm)}
            for row in run_rows:
                key = (row["seed"], row["scenario"], row["method_raw"])
                g = by_key.get(key)
                if not g:
                    # try method_display match
                    continue
                for k_src, k_dst in (
                    ("Tail_RMSE", "Tail_RMSE"),
                    ("Delta_group", "Delta_group"),
                    ("MAE_mu", "MAE_mu"),
                    ("Head_RMSE", "Head_RMSE"),
                ):
                    if g.get(k_src):
                        row[k_dst] = g[k_src]
                        row[f"{k_dst}_status"] = VALID

    write_csv(core / "E2_FINAL_VALID_RUNS_600.csv", run_rows)

    # D_aligned
    d_rows: list[dict[str, Any]] = []
    if dod_path.is_file():
        for r in read_csv(dod_path):
            d_rows.append(
                {
                    "dataset": "NSW-Traffic",
                    "scenario": "complete_aligned",
                    "seed": r.get("seed", ""),
                    "method": canon_method(r.get("method", "")),
                    "method_raw": r.get("method", ""),
                    "Delta_mu_aligned": r.get("Delta_mu_aligned", ""),
                    "Delta_rho_aligned": r.get("Delta_rho_aligned", ""),
                    "D_aligned": r.get("D_aligned", ""),
                    "sign_D": r.get("sign_D", ""),
                    "source_file": E2_ANALYSIS + "/COMPLETE_ALIGNED_DOD.csv",
                }
            )
    write_csv(core / "E2_D_ALIGNED_PER_SEED.csv", d_rows)

    summary_rows: list[dict[str, Any]] = []
    if dod_sum.is_file():
        summary = read_json(dod_sum)
        write_json(core / "E2_D_ALIGNED_SUMMARY.json", summary)
        if isinstance(summary, dict):
            for method, payload in summary.items():
                if not isinstance(payload, dict):
                    continue
                summary_rows.append({"method": canon_method(method), "method_raw": method, **payload})
    write_csv(core / "E2_D_ALIGNED_SUMMARY.csv", summary_rows)

    # Risk non-interchangeability master: merge run metrics + D_aligned for complete_aligned
    risk_rows = [r for r in run_rows if r.get("scenario") == "complete_aligned"]
    d_map = {(r["seed"], r["method_raw"]): r for r in d_rows}
    for r in risk_rows:
        d = d_map.get((r["seed"], r["method_raw"]), {})
        r["D_aligned"] = d.get("D_aligned", "")
        r["Delta_mu_aligned"] = d.get("Delta_mu_aligned", "")
        r["Delta_rho_aligned"] = d.get("Delta_rho_aligned", "")
    write_csv(core / "E2_RISK_NONINTERCHANGEABILITY_MASTER.csv", risk_rows)

    # Statistics copy
    if stats_path.is_file():
        copy_file(stats_path, stats / "E2_FINAL_STATISTICS.csv")
        copy_file(stats_path, raw / "formal_statistics.csv")
    else:
        write_csv(stats / "E2_FINAL_STATISTICS.csv", [])

    # EventTrace index 120
    et_rows: list[dict[str, Any]] = []
    if et_path.is_file():
        for r in read_csv(et_path):
            seed = r.get("seed", "")
            scenario = r.get("scenario", "")
            src_path = f"{E2_RUNS}/eventtraces/{seed}/{scenario}"
            et_rows.append(
                {
                    "round": "E2",
                    "dataset": "NSW-Traffic",
                    "scenario": scenario,
                    "seed": seed,
                    "EventTrace_hash": r.get("events_sha256", ""),
                    "source_path": src_path,
                    "size": "",
                    "shared_by_methods": "True",
                    "copied_into_package": "False",
                    "notes": "hash-indexed; bulky EventTrace files not duplicated into CORE",
                }
            )
    write_csv(prov / "E2_EVENTTRACE_INDEX_120.csv", et_rows)

    # Raw evidence copies (top-level sealed files only; not full EventTraces)
    copied = []
    copied += _copy_tree_files(runs_dir, raw / "formal_runs", ("*.csv", "*.json", "*.md"))
    copied += _copy_tree_files(analysis_dir, raw / "analysis", ("*.csv", "*.json", "*.md"))
    if (root / E2_SEAL).exists():
        copied += _copy_tree_files(root / E2_SEAL, raw / "claim_seal", ("*.csv", "*.json", "*.md"))
    if (root / E2_RECON).exists():
        copied += _copy_tree_files(root / E2_RECON, raw / "offline_recon", ("*.csv", "*.json", "*.md"))

    # Provenance
    prov_rows = []
    for rel in (
        f"{E2_RUNS}/formal_results.csv",
        f"{E2_RUNS}/eventtrace_manifest.csv",
        f"{E2_ANALYSIS}/COMPLETE_ALIGNED_DOD.csv",
        f"{E2_ANALYSIS}/FROZEN_600_RESULTS_MANIFEST.json",
    ):
        src = root / rel
        if src.is_file():
            prov_rows.append(
                {
                    "round": "E2",
                    "source_path": rel,
                    "sha256": sha256_file(src),
                    "size_bytes": src.stat().st_size,
                    "role": "e2_core_source",
                }
            )
    write_csv(prov / "E2_EVIDENCE_PROVENANCE.csv", prov_rows)

    status = {
        "round": "E2",
        "n_valid_runs": len(run_rows),
        "n_eventtraces": len(et_rows),
        "n_d_aligned_rows": len(d_rows),
        "expected_runs": 600,
        "expected_eventtraces": 120,
        "core_complete": len(run_rows) == 600 and len(et_rows) == 120,
        "raw_files_copied": len(copied),
    }
    write_json(core / "E2_COLLECTION_STATUS.json", status)
    return status
