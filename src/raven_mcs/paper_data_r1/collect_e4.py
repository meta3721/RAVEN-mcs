"""Collect E4 final ablation evidence (Gen2 wo_inst only in paper-core)."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .io_util import (
    INVALID,
    SUPERSEDED,
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
)


E4_FINAL = "artifacts/e4_wo_inst_reference_penalty_final_correction_r1"
E4_GEN1 = "artifacts/e4_ablation_semantic_integrity_repair_r1"
E4_GEN0 = "artifacts/e4_core_mechanism_ablation_r1"

COMPONENT_MAP = {
    "raven_wo_design": "Design",
    "raven_wo_obs": "Obs",
    "raven_wo_use": "Use",
    "raven_wo_inst": "Inst",
    "raven_wo_debt": "Debt",
}


def _gen_label(generation: str, method: str) -> tuple[str, str]:
    g = str(generation).strip()
    if method == "raven_wo_inst":
        if g in {"0", "E4_GEN0", "GEN0"}:
            return "0", "INVALID_P2_OFF"
        if g in {"1", "E4_GEN1", "GEN1"}:
            return "1", "SUPERSEDED_REFERENCE_PENALTY_MISMATCH"
        if g in {"2", "E4_GEN2", "GEN2", "VALID_GEN2_FINAL"}:
            return "2", "FINAL_VALID_ONE_FACTOR"
    if g in {"E3", "e3"}:
        return "E3", "VALID_E3_REFERENCE"
    return g, "VALID_E4_PARENT"


def collect_e4(root: Path, paper: Path, missing: list[dict[str, Any]]) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    core = paper / "01_core_data" / "e4"
    support = paper / "02_supporting_data" / "e4"
    raw = paper / "03_raw_evidence" / "e4"
    stats = paper / "04_statistics"
    prov = paper / "05_provenance"
    for d in (core, support, raw / "gen0", raw / "gen1", raw / "gen2", stats, prov):
        d.mkdir(parents=True, exist_ok=True)

    index_path = root / E4_FINAL / "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv"
    claims_path = root / E4_FINAL / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json"
    design_audit = root / E4_FINAL / "E4_WO_DESIGN_774_WINDOW_LAYER_AUDIT.csv"
    design_sum = root / E4_FINAL / "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.json"

    if not index_path.is_file():
        missing.append(
            {
                "item": "E4_FINAL_VALID_EVIDENCE_INDEX_R2",
                "round": "E4",
                "dataset": "",
                "method": "",
                "seed": "",
                "expected_source": f"{E4_FINAL}/E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv",
                "importance": "CORE",
                "can_be_reconstructed_offline": "false",
                "requires_new_experiment": "true",
                "recommended_action": "Restore E4 final correction seal",
            }
        )
        write_csv(core / "E4_FINAL_VALID_EVIDENCE_240.csv", [])
        return {"round": "E4", "n_core_cells": 0, "core_complete": False}

    raw_index = read_csv(index_path)
    core_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    for r in raw_index:
        method_raw = r.get("method", "")
        gen_raw = r.get("generation", "")
        gen, gen_status = _gen_label(gen_raw, method_raw)
        # Paper-core: only Gen2 for wo_inst; all other configs from this final index
        if method_raw == "raven_wo_inst" and str(gen) != "2":
            continue
        ds = canon_dataset(r.get("dataset", ""))
        method = canon_method(method_raw)
        row = {
            "dataset": ds,
            "dataset_raw": r.get("dataset", ""),
            "seed": r.get("seed", ""),
            "configuration": method,
            "method_raw": method_raw,
            "generation": gen,
            "generation_status": gen_status,
            "logical_run_id": f"e4::{r.get('dataset')}::{method_raw}::seed{r.get('seed')}::gen{gen}",
            "attempt_id": "",
            "source_revision": "",
            "EventTrace_hash": r.get("EventTrace_hash", ""),
            "checkpoint_hash": "",
            "metrics_hash": r.get("metric_hash", ""),
            "path": r.get("path", ""),
            "lambda_group": "",
            "lambda_beta": "",
            "lambda_v": "",
            "lambda_s": "",
            "Design_enabled": "False" if method_raw == "raven_wo_design" else "True",
            "Obs_enabled": "False" if method_raw == "raven_wo_obs" else "True",
            "Use_enabled": "False" if method_raw == "raven_wo_use" else "True",
            "Inst_enabled": "False" if method_raw == "raven_wo_inst" else "True",
            "Debt_enabled": "False" if method_raw == "raven_wo_debt" else "True",
            "P2_invoked": "True" if method_raw != "raven" else "True",
            "RMSE_mu": r.get("RMSE_mu", ""),
            "MAE_mu": "",
            "MAE_mu_status": "MISSING_NOT_RECORDED",
            "Tail_RMSE": r.get("Tail_RMSE", ""),
            "Delta_group": r.get("Delta_group", ""),
            "Delta_c_s": r.get("Delta_c_s", ""),
            "RMSE_rho": "",
            "RMSE_rho_status": "MISSING_NOT_RECORDED",
            "runtime": "",
            "solver_warnings": "",
            "validity": r.get("status", VALID),
            "accepted": r.get("accepted", ""),
            "superseded_reason": "",
            "comparison_class": "SCI_COMPARABLE_MAIN",
            "paper_role": "E4_core_ablation",
            "source_file": f"{E4_FINAL}/E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv",
        }
        core_rows.append(row)
        for metric in ("Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE"):
            long_rows.append(
                {
                    "dataset": ds,
                    "seed": r.get("seed", ""),
                    "configuration": method,
                    "method_raw": method_raw,
                    "generation": gen,
                    "metric": metric,
                    "value": r.get(metric, ""),
                    "status": VALID if r.get(metric, "") != "" else "MISSING_NOT_RECORDED",
                }
            )

    write_csv(core / "E4_FINAL_VALID_EVIDENCE_240.csv", core_rows)
    write_csv(core / "E4_ABLATION_LONG.csv", long_rows)

    # Relative change vs full RAVEN per dataset/seed/metric
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for r in core_rows:
        if r["method_raw"] == "raven":
            by_key[(r["dataset"], r["seed"])] = r
    rel_rows: list[dict[str, Any]] = []
    for r in core_rows:
        if r["method_raw"] == "raven":
            continue
        full = by_key.get((r["dataset"], r["seed"]))
        if not full:
            continue
        for metric in ("Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE"):
            fv = safe_float(full.get(metric))
            av = safe_float(r.get(metric))
            abs_change = ""
            rel_change = ""
            status = VALID
            if fv is None or av is None:
                status = "MISSING_NOT_RECORDED"
            else:
                abs_change = av - fv
                rel_change = (abs_change / fv * 100.0) if fv != 0 else ""
            rel_rows.append(
                {
                    "dataset": r["dataset"],
                    "seed": r["seed"],
                    "configuration": r["configuration"],
                    "component": COMPONENT_MAP.get(r["method_raw"], ""),
                    "metric": metric,
                    "full_RAVEN": full.get(metric, ""),
                    "ablation": r.get(metric, ""),
                    "absolute_change": abs_change,
                    "relative_change_percent": rel_change,
                    "status": status,
                }
            )
    write_csv(core / "E4_ABLATION_RELATIVE_CHANGE.csv", rel_rows)

    # Component effect master from sealed claims + numerical aggregates
    claims = read_json(claims_path) if claims_path.is_file() else {}
    effect_rows: list[dict[str, Any]] = []
    # Aggregate relative change numerically
    agg: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for r in rel_rows:
        if r["status"] != VALID:
            continue
        v = safe_float(r["absolute_change"])
        if v is None:
            continue
        agg[(r["dataset"], r["component"], r["metric"])].append(v)

    for component, payload in claims.items():
        if not isinstance(payload, dict):
            continue
        cells = payload.get("cells") or {}
        for cell_key, cell in cells.items():
            # SensorScope_Delta_group / UAir_Delta_group
            if "_" not in cell_key:
                continue
            ds_token, metric = cell_key.split("_", 1)
            dataset = "SensorScope" if ds_token.lower().startswith("sensor") else "U-Air"
            diffs = agg.get((dataset, component, metric), [])
            effect_rows.append(
                {
                    "dataset": dataset,
                    "component": component,
                    "metric": metric,
                    "full_RAVEN_mean": "",
                    "ablation_mean": "",
                    "absolute_change": cell.get("mean_paired_diff", ""),
                    "relative_change_percent": (
                        float(cell["relative_change"]) * 100.0
                        if safe_float(cell.get("relative_change")) is not None
                        else ""
                    ),
                    "paired_seed_mean_difference": cell.get("mean_paired_diff", ""),
                    "paired_seed_median_difference": "",
                    "effect_size": cell.get("effect_size_paired", ""),
                    "raw_p": "",
                    "Holm_p": cell.get("p_holm", ""),
                    "CI": "",
                    "direction": cell.get("direction", ""),
                    "n_pairs": 20,
                    "holm_significant": cell.get("holm_significant", ""),
                    "qualitative_status": payload.get("status", ""),
                    "paper_safe_wording": payload.get("paper_safe_wording", ""),
                    "n_numeric_abs_diffs_collected": len(diffs),
                    "source_claim_matrix": f"{E4_FINAL}/E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
                }
            )
    # Fill full/ablation means from core rows
    means: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for r in core_rows:
        for metric in ("Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE"):
            v = safe_float(r.get(metric))
            if v is None:
                continue
            comp = COMPONENT_MAP.get(r["method_raw"], "RAVEN-MCS" if r["method_raw"] == "raven" else "")
            means[(r["dataset"], comp, metric)].append(v)
    for row in effect_rows:
        full_vals = means.get((row["dataset"], "RAVEN-MCS", row["metric"]), [])
        abl_comp = row["component"]
        # map component to method means via COMPONENT_MAP inverse
        method_raw = {v: k for k, v in COMPONENT_MAP.items()}.get(abl_comp, "")
        abl_vals = means.get((row["dataset"], canon_method(method_raw), row["metric"]), [])
        if full_vals:
            row["full_RAVEN_mean"] = sum(full_vals) / len(full_vals)
        if abl_vals:
            row["ablation_mean"] = sum(abl_vals) / len(abl_vals)
    write_csv(core / "E4_COMPONENT_EFFECT_MASTER.csv", effect_rows)

    # Interpretation metadata: prefer sealed R3 statuses; also record instruction §14 notes
    interp = {
        "source_claim_matrix": f"{E4_FINAL}/E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
        "instruction_section_14_suggested": {
            "Design": "ENDPOINT_TRADEOFF",
            "Obs": "ENDPOINT_TRADEOFF",
            "Use": "NO_CLEAR_EFFECT",
            "Inst": "ENDPOINT_TRADEOFF",
            "Debt": "STRUCTURAL_ONLY_SUPPORTED, quantitatively small",
        },
        "sealed_r3_status": {
            k: (v.get("status") if isinstance(v, dict) else None) for k, v in claims.items()
        },
        "note": "Prefer sealed E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json qualitative status for paper wording.",
    }
    write_json(core / "E4_COMPONENT_INTERPRETATION_METADATA.json", interp)

    # Design 774 audit
    if design_audit.is_file():
        copy_file(design_audit, support / "E4_WO_DESIGN_774_WINDOW_AUDIT.csv")
    else:
        missing.append(
            {
                "item": "E4_WO_DESIGN_774_WINDOW_AUDIT",
                "round": "E4",
                "dataset": "U-Air",
                "method": "RAVEN-w/o-Design",
                "seed": "",
                "expected_source": f"{E4_FINAL}/E4_WO_DESIGN_774_WINDOW_LAYER_AUDIT.csv",
                "importance": "SUPPORTING",
                "can_be_reconstructed_offline": "false",
                "requires_new_experiment": "false",
                "recommended_action": "Copy from E4 final correction seal if available",
            }
        )
        write_csv(support / "E4_WO_DESIGN_774_WINDOW_AUDIT.csv", [])
    if design_sum.is_file():
        summary = read_json(design_sum)
        write_json(support / "E4_WO_DESIGN_AUDIT_SUMMARY.json", summary)
    else:
        write_json(
            support / "E4_WO_DESIGN_AUDIT_SUMMARY.json",
            {
                "scope_leakage": 0,
                "unresolved": 0,
                "valid_weight_support_effect": 774,
                "status": "MISSING_SUMMARY_FILE_DEFAULTS_FROM_INSTRUCTIONS",
            },
        )

    # Archive Gen0 / Gen1 indices into raw + ledgers later
    gen1_idx = root / E4_GEN1 / "E4_FINAL_VALID_EVIDENCE_INDEX.csv"
    if gen1_idx.is_file():
        copy_file(gen1_idx, raw / "gen1" / "E4_FINAL_VALID_EVIDENCE_INDEX_GEN1.csv")
    for base, dest_name in (
        (root / E4_GEN0, "gen0"),
        (root / E4_GEN1, "gen1"),
        (root / E4_FINAL, "gen2"),
    ):
        if not base.exists():
            continue
        out = raw / dest_name
        for p in base.glob("*"):
            if p.is_file() and p.suffix.lower() in {".csv", ".json", ".md"}:
                copy_file(p, out / p.name)

    # Statistics: copy claim matrix cells as stats
    write_csv(stats / "E4_FINAL_STATISTICS.csv", effect_rows)

    prov_rows = [
        {
            "round": "E4",
            "source_path": f"{E4_FINAL}/E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv",
            "sha256": sha256_file(index_path),
            "size_bytes": index_path.stat().st_size,
            "role": "e4_core_index",
        }
    ]
    if claims_path.is_file():
        prov_rows.append(
            {
                "round": "E4",
                "source_path": f"{E4_FINAL}/E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
                "sha256": sha256_file(claims_path),
                "size_bytes": claims_path.stat().st_size,
                "role": "e4_claim_matrix_r3",
            }
        )
    write_csv(prov / "E4_EVIDENCE_PROVENANCE.csv", prov_rows)

    n_wo_inst = sum(1 for r in core_rows if r["method_raw"] == "raven_wo_inst")
    status = {
        "round": "E4",
        "n_core_cells": len(core_rows),
        "expected_cells": 240,
        "n_wo_inst_gen2": n_wo_inst,
        "wo_inst_policy": "Only Generation 2 FINAL_VALID_ONE_FACTOR enters PAPER_CORE",
        "gen0_archive": E4_GEN0,
        "gen1_archive": E4_GEN1,
        "gen2_source": E4_FINAL,
        "core_complete": len(core_rows) == 240 and n_wo_inst == 40,
        "design_774_present": design_audit.is_file(),
    }
    write_json(core / "E4_COLLECTION_STATUS.json", status)
    return status
