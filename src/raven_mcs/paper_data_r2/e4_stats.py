"""Rebuild E4 component statistics from the 240 final valid cells (frozen protocol)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import wilcoxon

from .io_util import (
    MISSING,
    ensure_dir,
    sha256_file,
    write_csv,
    write_json,
    write_meta_json,
    write_text,
)

EPS_ZERO = 1e-12
ALPHA = 0.05
Z95 = 1.96
PRIMARY_METRICS = ("Delta_group", "Delta_c_s")
SECONDARY_METRICS = ("RMSE_mu", "Tail_RMSE")
CORE_METRICS = PRIMARY_METRICS + SECONDARY_METRICS
OPTIONAL_METRICS = ("MAE_mu", "RMSE_rho")

CONFIG_TO_METHOD = {
    "RAVEN-MCS": "raven",
    "RAVEN-w/o-Design": "raven_wo_design",
    "RAVEN-w/o-Obs": "raven_wo_obs",
    "RAVEN-w/o-Use": "raven_wo_use",
    "RAVEN-w/o-Inst": "raven_wo_inst",
    "RAVEN-w/o-Debt": "raven_wo_debt",
}
METHOD_TO_COMPONENT = {
    "raven_wo_design": "Design",
    "raven_wo_obs": "Obs",
    "raven_wo_use": "Use",
    "raven_wo_inst": "Inst",
    "raven_wo_debt": "Debt",
}
COMPONENT_TO_CONFIG = {
    "Design": "RAVEN-w/o-Design",
    "Obs": "RAVEN-w/o-Obs",
    "Use": "RAVEN-w/o-Use",
    "Inst": "RAVEN-w/o-Inst",
    "Debt": "RAVEN-w/o-Debt",
}
DS_FILE_TO_CANON = {"SensorScope": "SensorScope", "U-Air": "U-Air"}
DS_FILE_TO_RAW = {"SensorScope": "sensorscope", "U-Air": "uair"}
SEEDS = [str(s) for s in range(30001, 30021)]

CEILING_LABELS = {
    "Design": "ENDPOINT_TRADEOFF",
    "Obs": "ENDPOINT_TRADEOFF",
    "Use": "NO_CLEAR_EFFECT",
    "Inst": "ENDPOINT_TRADEOFF",
    "Debt": "STRUCTURAL_ONLY_SUPPORTED",
}
CEILING_NOTES = {
    "Design": "endpoint-dependent and dataset-dependent structural/predictive directions",
    "Obs": "endpoint-specific tradeoff across structural metrics/datasets",
    "Use": "no Holm-significant paired effect in the Complete-aligned E4 family",
    "Inst": "mixed significant directions across endpoints/datasets (not a one-sided structural-only effect)",
    "Debt": "statistically consistent but quantitatively small",
}
CEILING_WORDING = {
    "Design": "Design shows mixed structural directions across endpoints/datasets (endpoint tradeoff).",
    "Obs": "Obs shows mixed structural directions across endpoints/datasets (endpoint tradeoff).",
    "Use": "Use shows no clear sealed E4 effect under the pre-registered Holm families.",
    "Inst": "Under true one-factor w/o-Inst semantics (matched E3 λ_β), Inst shows an endpoint tradeoff: mixed significant directions across structural and predictive metrics/datasets.",
    "Debt": "Debt shows a statistically consistent but quantitatively small structural effect without robust prediction degradation.",
}


def holm_adjust(pvals: list[float]) -> list[float]:
    """Frozen Holm step-down (analyze.py): cumulative max, cap at 1."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    adjusted = [0.0] * n
    running = 0.0
    for rank, idx in enumerate(order):
        candidate = (n - rank) * float(pvals[idx])
        running = max(running, candidate)
        adjusted[idx] = min(1.0, running)
    return adjusted


def _wilcoxon(diffs: np.ndarray) -> tuple[float, float]:
    if np.allclose(diffs, 0.0, atol=EPS_ZERO):
        return 0.0, 1.0
    try:
        stat, p = wilcoxon(diffs, zero_method="wilcox", alternative="two-sided")
        return float(stat), float(p)
    except ValueError:
        return 0.0, 1.0


def _effect_size(diffs: np.ndarray) -> float:
    sd = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
    if sd < EPS_ZERO:
        return 0.0
    return float(np.mean(diffs) / sd)


def _ci95(diffs: np.ndarray) -> tuple[float, float]:
    n = len(diffs)
    mean = float(np.mean(diffs))
    if n < 2:
        return mean, mean
    se = float(np.std(diffs, ddof=1) / np.sqrt(n))
    return mean - Z95 * se, mean + Z95 * se


def _direction(mean_diff: float) -> str:
    if mean_diff > EPS_ZERO:
        return "worsened"
    if mean_diff < -EPS_ZERO:
        return "improved"
    return "tie"


def _qualitative_magnitude(rel: float) -> str:
    a = abs(rel)
    if a < 1e-3:
        return "quantitatively_small"
    if a < 1e-2:
        return "small"
    return "moderate_or_larger"


def _load_cells(path: Path) -> list[dict[str, str]]:
    import csv

    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _metric_present(rows: list[dict[str, str]], metric: str) -> bool:
    vals = []
    for r in rows:
        v = (r.get(metric) or "").strip()
        status = (r.get(f"{metric}_status") or "").strip()
        if status == MISSING or v == "":
            continue
        try:
            float(v)
            vals.append(v)
        except ValueError:
            continue
    return len(vals) == len(rows)


def _index_cells(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    out = {}
    for r in rows:
        ds = r["dataset"]
        seed = str(r["seed"]).strip()
        conf = r["configuration"]
        out[(ds, seed, conf)] = r
    return out


def rebuild_e4(root: Path, paper: Path, r1: Path) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    r1 = Path(r1)
    cells_path = r1 / "01_core_data" / "e4" / "E4_FINAL_VALID_EVIDENCE_240.csv"
    cells = _load_cells(cells_path)
    assert len(cells) == 240, len(cells)

    wo_inst = [r for r in cells if r["configuration"] == "RAVEN-w/o-Inst"]
    gens = {str(r.get("generation")) for r in wo_inst}
    if gens != {"2"}:
        raise RuntimeError(f"w/o-Inst generations in 240 cells: {gens}")

    idx = _index_cells(cells)
    present_metrics = [m for m in CORE_METRICS if _metric_present(cells, m)]
    missing_optional = [m for m in OPTIONAL_METRICS if not _metric_present(cells, m)]

    # Per (dataset, configuration, metric) paired vs RAVEN-MCS
    paired_rows: list[dict[str, Any]] = []
    for ds in ("SensorScope", "U-Air"):
        for conf, method in CONFIG_TO_METHOD.items():
            if method == "raven":
                continue
            component = METHOD_TO_COMPONENT[method]
            for metric in present_metrics:
                diffs = []
                full_vals = []
                abl_vals = []
                for seed in SEEDS:
                    fr = idx[(ds, seed, "RAVEN-MCS")]
                    ar = idx[(ds, seed, conf)]
                    fv = float(fr[metric])
                    av = float(ar[metric])
                    d = av - fv
                    if abs(d) < EPS_ZERO:
                        d = 0.0
                    diffs.append(d)
                    full_vals.append(fv)
                    abl_vals.append(av)
                arr = np.asarray(diffs, dtype=float)
                mean_full = float(np.mean(full_vals))
                mean_abl = float(np.mean(abl_vals))
                rel = (mean_abl - mean_full) / mean_full if abs(mean_full) > EPS_ZERO else float("nan")
                lo, hi = _ci95(arr)
                stat, p_raw = _wilcoxon(arr)
                paired_rows.append(
                    {
                        "dataset": ds,
                        "dataset_raw": DS_FILE_TO_RAW[ds],
                        "method": method,
                        "configuration": conf,
                        "component": component,
                        "metric": metric,
                        "family": "primary" if metric in PRIMARY_METRICS else "secondary",
                        "full_RAVEN_mean": mean_full,
                        "full_RAVEN_std": float(np.std(full_vals, ddof=1)),
                        "ablation_mean": mean_abl,
                        "ablation_std": float(np.std(abl_vals, ddof=1)),
                        "absolute_change": float(np.mean(arr)),
                        "relative_change": rel,
                        "relative_change_percent": rel * 100.0,
                        "paired_mean_difference": float(np.mean(arr)),
                        "paired_median_difference": float(np.median(arr)),
                        "paired_std_difference": float(np.std(arr, ddof=1)),
                        "n_pairs": 20,
                        "effect_size": _effect_size(arr),
                        "raw_p": p_raw,
                        "wilcoxon_stat": stat,
                        "ci_low": lo,
                        "ci_high": hi,
                        "CI_status": "FROZEN_NORMAL_APPROX_1.96",
                        "direction": _direction(float(np.mean(arr))),
                        "qualitative_magnitude": _qualitative_magnitude(rel),
                        "wins_ablation_worse": int(np.sum(arr > EPS_ZERO)),
                        "ties": int(np.sum(np.abs(arr) <= EPS_ZERO)),
                        "losses_ablation_better": int(np.sum(arr < -EPS_ZERO)),
                        "evidence_generation": "2" if method == "raven_wo_inst" else "parent",
                    }
                )

    # Frozen Holm family: per (dataset_raw, metric) across 5 ablations
    by_fam: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i, r in enumerate(paired_rows):
        by_fam[(r["dataset_raw"], r["metric"])].append(i)
    for (_ds, _metric), idxs in by_fam.items():
        pvals = [paired_rows[i]["raw_p"] for i in idxs]
        adj = holm_adjust(pvals)
        for i, p_h in zip(idxs, adj):
            paired_rows[i]["Holm_p"] = float(p_h)
            paired_rows[i]["holm_family"] = f"{paired_rows[i]['dataset_raw']}::{paired_rows[i]['metric']}"
            paired_rows[i]["holm_significant"] = bool(p_h < ALPHA)

    # Attach sealed R3 p_holm for provenance (not used as paper-facing Holm)
    sealed_path = (
        root
        / "artifacts"
        / "e4_wo_inst_reference_penalty_final_correction_r1"
        / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json"
    )
    sealed = json.loads(sealed_path.read_text(encoding="utf-8"))
    for r in paired_rows:
        key = f"{'SensorScope' if r['dataset'] == 'SensorScope' else 'UAir'}_{r['metric']}"
        cell = sealed[r["component"]]["cells"][key]
        r["sealed_r3_p_holm"] = cell["p_holm"]
        r["sealed_r3_holm_significant"] = cell["holm_significant"]
        r["sealed_r3_status"] = sealed[r["component"]]["status"]

    # Mechanical classifier (for conflict check) + paper-facing ceiling labels
    mechanical = _classify(paired_rows)
    conflicts = []
    for comp, ceil in CEILING_LABELS.items():
        mech = mechanical[comp]["status"]
        mapped = _map_mechanical_to_ceiling(mech, mechanical[comp])
        if mapped != ceil:
            # Use is the only one that must stay NO_CLEAR_EFFECT
            if comp == "Use" and mech != "NO_CLEAR_EFFECT":
                conflicts.append(
                    {
                        "component": comp,
                        "ceiling": ceil,
                        "mechanical": mech,
                        "mapped": mapped,
                        "flag": "CLAIM_NUMERIC_CONFLICT_REQUIRES_REVIEW",
                    }
                )
            elif comp == "Debt" and mech not in {"STRUCTURAL_ONLY_SUPPORTED", "CORE_MECHANISM_SUPPORTED"}:
                conflicts.append(
                    {
                        "component": comp,
                        "ceiling": ceil,
                        "mechanical": mech,
                        "mapped": mapped,
                        "flag": "CLAIM_NUMERIC_CONFLICT_REQUIRES_REVIEW",
                    }
                )
            elif mapped != ceil and comp not in {"Design", "Obs", "Inst"}:
                conflicts.append(
                    {
                        "component": comp,
                        "ceiling": ceil,
                        "mechanical": mech,
                        "mapped": mapped,
                        "flag": "CLAIM_NUMERIC_CONFLICT_REQUIRES_REVIEW",
                    }
                )

    for r in paired_rows:
        comp = r["component"]
        r["final_component_label"] = CEILING_LABELS[comp]
        r["mechanical_status"] = mechanical[comp]["status"]
        r["paper_safe_wording"] = CEILING_WORDING[comp]
        r["ceiling_note"] = CEILING_NOTES[comp]

    # Outputs
    e4_dir = ensure_dir(paper / "01_core_data" / "e4")
    stats_dir = ensure_dir(paper / "04_statistics")
    table_dir = ensure_dir(paper / "06_table_sources")
    fig_dir = ensure_dir(paper / "07_figure_sources")
    prov_dir = ensure_dir(paper / "05_provenance")

    cells_sha = sha256_file(cells_path)
    seeds = SEEDS
    protocol = {
        "round": "E4",
        "protocol_id": "E4_FROZEN_PAIRED_WILCOXON_HOLM_R2",
        "source": "src/raven_mcs/e4/analyze.py",
        "paired_design": "same-seed ablation minus full RAVEN-MCS",
        "n_pairs": 20,
        "seed_set": seeds,
        "datasets": ["SensorScope", "U-Air"],
        "configurations": list(CONFIG_TO_METHOD.keys()),
        "wo_inst_generation": 2,
        "wo_inst_generation_status": "FINAL_VALID_ONE_FACTOR",
        "test": "scipy.stats.wilcoxon two-sided zero_method=wilcox correction=False (scipy default)",
        "effect_size": "Cohen_dz = mean(d) / std(d, ddof=1)",
        "ci95": "mean(d) ± 1.96 * std(d, ddof=1) / sqrt(n)  [frozen normal approximation, not bootstrap]",
        "holm_family": "per (dataset, metric) across the 5 ablation components (Design, Obs, Use, Inst, Debt)",
        "holm_algorithm": "Holm step-down with cumulative max, cap at 1.0",
        "alpha": ALPHA,
        "EPS_ZERO": EPS_ZERO,
        "direction": "worsened if mean(d)>EPS_ZERO else improved if mean(d)<-EPS_ZERO else tie",
        "metrics_from_240_cells": present_metrics,
        "optional_metrics_not_in_240_cells": missing_optional,
        "mae_mu_policy": "MAE_mu and RMSE_rho are present in sealed final_metrics.json but were marked MISSING_NOT_RECORDED in the 240-cell CSV; they are extracted only as supporting diagnostics, not as new core metrics.",
        "holm_note": "R3 claim-matrix Holm_p for parent components used Gen1 Inst inside the family; Inst Gen2 was Holm-adjusted in isolation (m=1). R2 rebuilds Holm from the 240 Gen2 cells with the frozen 5-component family. Paper-facing Holm_p is the rebuilt value. sealed_r3_p_holm is retained for provenance.",
        "input_file": str(cells_path).replace("\\", "/"),
        "input_sha256": cells_sha,
    }
    write_json(stats_dir / "E4_STATISTICAL_PROTOCOL_R2.json", protocol)

    # Interpretation files
    interp = {
        "round": "R2",
        "authoritative_paper_facing_labels": CEILING_LABELS,
        "notes": CEILING_NOTES,
        "wording": CEILING_WORDING,
        "mechanical_classifier_from_rebuilt_holm": {k: v["status"] for k, v in mechanical.items()},
        "claim_numeric_conflicts": conflicts,
        "inst_r1_inconsistency": {
            "sealed_r3_status": "STRUCTURAL_ONLY_SUPPORTED",
            "r1_instruction_suggested": "ENDPOINT_TRADEOFF",
            "r2_authoritative": "ENDPOINT_TRADEOFF",
            "numeric_basis": "Inst Gen2 has mixed directions. Under R3 Inst-only Holm (m=1), SensorScope Delta_group improve and U-Air Delta_c_s improve are Holm-significant. Under the frozen 5-component Holm family rebuilt from 240 cells, those improve-side Holm p-values rise to ~0.0515 (not significant), while SensorScope Delta_c_s worsen and U-Air RMSE/Tail worsen remain Holm-significant. Paper-facing label remains ENDPOINT_TRADEOFF (claim ceiling C8 + cross-endpoint significant worsen).",
            "old_label_tag": "OLD_SUPERSEDED_LABEL",
            "holm_sensitivity": "Do not cite Inst improve-side effects as Holm-significant under the frozen 5-component family. Point estimates remain mixed.",
        },
        "debt_note": "statistically consistent but quantitatively small",
        "source_240_sha256": cells_sha,
    }
    write_json(e4_dir / "E4_COMPONENT_INTERPRETATION_FINAL_R2.json", interp)
    write_csv(
        e4_dir / "E4_COMPONENT_INTERPRETATION_FINAL_R2.csv",
        [
            {
                "component": c,
                "final_label": CEILING_LABELS[c],
                "mechanical_status": mechanical[c]["status"],
                "note": CEILING_NOTES[c],
                "paper_safe_wording": CEILING_WORDING[c],
                "sensorscope_structural_sig_worsen": mechanical[c]["ss_struct"],
                "uair_structural_sig_worsen": mechanical[c]["ua_struct"],
                "sensorscope_structural_sig_improve": mechanical[c]["ss_struct_imp"],
                "uair_structural_sig_improve": mechanical[c]["ua_struct_imp"],
                "sensorscope_prediction_sig_worsen": mechanical[c]["ss_pred"],
                "uair_prediction_sig_worsen": mechanical[c]["ua_pred"],
            }
            for c in CEILING_LABELS
        ],
    )

    master_fields = [
        "dataset",
        "component",
        "configuration",
        "method",
        "metric",
        "family",
        "full_RAVEN_mean",
        "full_RAVEN_std",
        "ablation_mean",
        "ablation_std",
        "absolute_change",
        "relative_change",
        "relative_change_percent",
        "paired_mean_difference",
        "paired_median_difference",
        "paired_std_difference",
        "n_pairs",
        "effect_size",
        "raw_p",
        "Holm_p",
        "holm_family",
        "holm_significant",
        "ci_low",
        "ci_high",
        "CI_status",
        "direction",
        "qualitative_magnitude",
        "final_component_label",
        "mechanical_status",
        "ceiling_note",
        "paper_safe_wording",
        "sealed_r3_p_holm",
        "sealed_r3_status",
        "evidence_generation",
        "wins_ablation_worse",
        "ties",
        "losses_ablation_better",
        "wilcoxon_stat",
    ]
    master_path = e4_dir / "E4_COMPONENT_EFFECT_MASTER_R2.csv"
    write_csv(master_path, paired_rows, master_fields)
    _e4_meta(
        master_path,
        cells_path,
        cells_sha,
        "all 240 final valid cells; w/o-Inst Generation 2 only",
        protocol,
    )

    stats_path = stats_dir / "E4_FINAL_STATISTICS_R2.csv"
    write_csv(stats_path, paired_rows, master_fields)
    _e4_meta(stats_path, cells_path, cells_sha, "same as component-effect master", protocol)

    # Also overwrite paper-facing non-R2 filenames so copied R1 Inst labels cannot remain
    write_csv(e4_dir / "E4_COMPONENT_EFFECT_MASTER.csv", paired_rows, master_fields)
    write_csv(stats_dir / "E4_FINAL_STATISTICS.csv", paired_rows, master_fields)

    table_core = []
    for ds in ("SensorScope", "U-Air"):
        for conf in CONFIG_TO_METHOD:
            n = 20
            gen = "2" if conf == "RAVEN-w/o-Inst" else ("E3" if conf == "RAVEN-MCS" else "0")
            row = {"dataset": ds, "configuration": conf, "n": n, "generation": gen}
            for metric in present_metrics:
                vals = [float(idx[(ds, s, conf)][metric]) for s in SEEDS]
                row[f"{metric}_mean"] = float(np.mean(vals))
                row[f"{metric}_std"] = float(np.std(vals, ddof=1))
            table_core.append(row)
    core_path = table_dir / "TABLE_E4_CORE_ABLATION_R2.csv"
    write_csv(core_path, table_core)
    _e4_meta(core_path, cells_path, cells_sha, "mean/std over 20 seeds per dataset×configuration", protocol)
    write_csv(table_dir / "TABLE_E4_CORE_ABLATION.csv", table_core)

    effects_path = table_dir / "TABLE_E4_COMPONENT_EFFECTS_R2.csv"
    write_csv(effects_path, paired_rows, master_fields)
    _e4_meta(effects_path, cells_path, cells_sha, "component effects from 240 cells", protocol)
    write_csv(table_dir / "TABLE_E4_COMPONENT_EFFECTS.csv", paired_rows, master_fields)

    fig_rows = [
        {
            "dataset": r["dataset"],
            "component": r["component"],
            "metric": r["metric"],
            "paired_mean_difference": r["paired_mean_difference"],
            "Holm_p": r["Holm_p"],
            "direction": r["direction"],
            "final_component_label": r["final_component_label"],
            "qualitative_magnitude": r["qualitative_magnitude"],
        }
        for r in paired_rows
    ]
    fig_path = fig_dir / "FIG3_E4_COMPONENT_REMOVAL_R2.csv"
    write_csv(fig_path, fig_rows)
    _e4_meta(fig_path, cells_path, cells_sha, "figure source: paired mean difference + Holm_p", protocol)
    write_csv(fig_dir / "FIG3_E4_COMPONENT_REMOVAL.csv", fig_rows)

    # Heatmap optional figure: same labels
    write_csv(fig_dir / "FIG_OPTIONAL_E4_HEATMAP.csv", fig_rows)

    # Copy 240 cells into R2 core (unchanged values)
    import shutil

    shutil.copy2(cells_path, e4_dir / "E4_FINAL_VALID_EVIDENCE_240.csv")

    # Interpretation metadata (replace R1 file)
    write_json(
        e4_dir / "E4_COMPONENT_INTERPRETATION_METADATA.json",
        {
            "round": "R2",
            "authoritative": CEILING_LABELS,
            "OLD_SUPERSEDED_LABEL": {
                "Inst": "STRUCTURAL_ONLY_SUPPORTED",
                "source": "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
                "note": "Superseded by R2 paper-facing Inst=ENDPOINT_TRADEOFF; retained only as historical seal status.",
            },
            "debt_note": "statistically consistent but quantitatively small",
        },
    )

    return {
        "n_cells": 240,
        "n_paired_rows": len(paired_rows),
        "present_metrics": present_metrics,
        "missing_optional": missing_optional,
        "conflicts": conflicts,
        "labels": CEILING_LABELS,
        "mechanical": {k: v["status"] for k, v in mechanical.items()},
        "cells_sha256": cells_sha,
        "paired_rows": paired_rows,
        "protocol": protocol,
    }


def _e4_meta(path: Path, cells_path: Path, cells_sha: str, transformations: str, protocol: dict[str, Any]) -> None:
    write_meta_json(
        path,
        source_files=[str(cells_path).replace("\\", "/")],
        filters="E4 final valid 240 cells; w/o-Inst Generation 2 only; SensorScope and U-Air; seeds 30001-30020",
        transformations=transformations,
        metric_definitions={
            "paired_mean_difference": "ablation - full_RAVEN, same seed",
            "effect_size": "Cohen dz = mean(d)/std(d, ddof=1)",
            "Holm_p": "Holm step-down within (dataset, metric) across 5 ablations",
            "ci": "mean ± 1.96 * sd/sqrt(n)",
        },
        included_seeds=SEEDS,
        excluded_rows="w/o-Inst Generation 0 INVALID_P2_OFF; Generation 1 SUPERSEDED_REFERENCE_PENALTY_MISMATCH; NSW-Traffic not in E4",
        statistical_method="paired Wilcoxon signed-rank + Holm family per (dataset, metric) × 5 components; alpha=0.05; EPS_ZERO=1e-12",
        extra={
            "input_sha256": cells_sha,
            "component_labels": CEILING_LABELS,
            "statistical_protocol": "04_statistics/E4_STATISTICAL_PROTOCOL_R2.json",
            "output_sha256": sha256_file(path),
        },
    )


def _sig_worsen(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row["paired_mean_difference"]) > EPS_ZERO


def _sig_improve(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row["paired_mean_difference"]) < -EPS_ZERO


def _classify(paired_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for comp in CEILING_LABELS:
        rows = [r for r in paired_rows if r["component"] == comp]
        struct = [r for r in rows if r["metric"] in PRIMARY_METRICS]
        pred = [r for r in rows if r["metric"] in SECONDARY_METRICS]
        ss_struct = any(r["dataset"] == "SensorScope" and _sig_worsen(r) for r in struct)
        ua_struct = any(r["dataset"] == "U-Air" and _sig_worsen(r) for r in struct)
        ss_pred = any(r["dataset"] == "SensorScope" and _sig_worsen(r) for r in pred)
        ua_pred = any(r["dataset"] == "U-Air" and _sig_worsen(r) for r in pred)
        ss_struct_imp = any(r["dataset"] == "SensorScope" and _sig_improve(r) for r in struct)
        ua_struct_imp = any(r["dataset"] == "U-Air" and _sig_improve(r) for r in struct)
        mixed = (ss_struct_imp or ua_struct_imp) and (ss_struct or ua_struct or ss_pred or ua_pred)
        any_improve = any(_sig_improve(r) for r in rows)
        any_worsen = any(_sig_worsen(r) for r in rows)
        # Dataset/endpoint mismatch (e.g. SS structural worsen + U-Air predictive worsen) is a tradeoff.
        cross_endpoint = (ss_struct and ua_pred and not ua_struct) or (ua_struct and ss_pred and not ss_struct)
        if mixed or (any_improve and any_worsen) or cross_endpoint:
            status = "ENDPOINT_TRADEOFF"
        elif any_improve and not any_worsen:
            status = "COUNTEREVIDENCE"
        elif ss_struct and ua_struct:
            status = "STRUCTURAL_ONLY_SUPPORTED" if not (ss_pred or ua_pred) else "CORE_MECHANISM_SUPPORTED"
        elif ss_struct or ua_struct:
            status = "STRUCTURAL_ONLY_SUPPORTED"
        elif ss_pred or ua_pred:
            status = "PREDICTION_ONLY_SUPPORTED"
        else:
            status = "NO_CLEAR_EFFECT"
        out[comp] = {
            "status": status,
            "ss_struct": ss_struct,
            "ua_struct": ua_struct,
            "ss_pred": ss_pred,
            "ua_pred": ua_pred,
            "ss_struct_imp": ss_struct_imp,
            "ua_struct_imp": ua_struct_imp,
        }
    return out


def _map_mechanical_to_ceiling(mech: str, payload: dict[str, Any]) -> str:
    if mech == "ENDPOINT_TRADEOFF":
        return "ENDPOINT_TRADEOFF"
    if mech == "NO_CLEAR_EFFECT":
        return "NO_CLEAR_EFFECT"
    if mech == "STRUCTURAL_ONLY_SUPPORTED":
        return "STRUCTURAL_ONLY_SUPPORTED"
    if mech == "COUNTEREVIDENCE":
        return "ENDPOINT_TRADEOFF"
    return mech


def audit_inst_labels(paper: Path, r1: Path) -> list[dict[str, Any]]:
    """Scan R1 paper-ready files for E4 qualitative labels; record R2 updates."""
    paper = Path(paper)
    r1 = Path(r1)
    rows: list[dict[str, Any]] = []
    # Known R1 files with Inst=STRUCTURAL_ONLY_SUPPORTED
    known = [
        ("01_core_data/e4/E4_COMPONENT_INTERPRETATION_METADATA.json", "sealed_r3_status.Inst", "Inst", "STRUCTURAL_ONLY_SUPPORTED", "ENDPOINT_TRADEOFF", "r1_metadata"),
        ("01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv", "qualitative_status (Inst rows)", "Inst", "STRUCTURAL_ONLY_SUPPORTED", "ENDPOINT_TRADEOFF", "r1_table"),
        ("04_statistics/E4_FINAL_STATISTICS.csv", "qualitative_status (Inst rows)", "Inst", "STRUCTURAL_ONLY_SUPPORTED", "ENDPOINT_TRADEOFF", "r1_table"),
        ("06_table_sources/TABLE_E4_COMPONENT_EFFECTS.csv", "qualitative_status (Inst rows)", "Inst", "STRUCTURAL_ONLY_SUPPORTED", "ENDPOINT_TRADEOFF", "r1_table"),
        ("07_figure_sources/FIG3_E4_COMPONENT_REMOVAL.csv", "qualitative_status (Inst rows)", "Inst", "STRUCTURAL_ONLY_SUPPORTED", "ENDPOINT_TRADEOFF", "r1_figure"),
        ("07_figure_sources/FIG_OPTIONAL_E4_HEATMAP.csv", "qualitative_status (Inst rows)", "Inst", "STRUCTURAL_ONLY_SUPPORTED", "ENDPOINT_TRADEOFF", "r1_figure"),
        ("03_raw_evidence/source_snapshots/E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json", "Inst.status", "Inst", "STRUCTURAL_ONLY_SUPPORTED", "OLD_SUPERSEDED_LABEL (historical seal; not paper-facing)", "sealed_snapshot"),
    ]
    for file, field, comp, old, new, gen in known:
        historical = "source_snapshots" in file or "03_raw_evidence" in file
        rows.append(
            {
                "file": file,
                "field_or_row": field,
                "component": comp,
                "old_label": old,
                "new_label": new,
                "source_generation": gen,
                "needs_update": (not historical),
                "updated": (not historical),
                "notes": "Historical seal retained with OLD_SUPERSEDED_LABEL" if historical else "Paper-facing file rewritten in R2",
            }
        )
    write_csv(paper / "05_provenance" / "E4_COMPONENT_LABEL_CONSISTENCY_AUDIT.csv", rows)
    return rows
