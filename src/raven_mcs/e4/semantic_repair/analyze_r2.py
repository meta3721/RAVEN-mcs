"""Recompute Inst-affected stats and R2 claim matrix from corrected evidence."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import wilcoxon

from raven_mcs.e4.analyze import (
    ALL_METRICS,
    COMPONENT,
    EPS_ZERO,
    PRIMARY_METRICS,
    SECONDARY_METRICS,
    apply_holm_by_family,
    holm_adjust,
)
from raven_mcs.e4.constants import ABLATIONS, DATASETS, FORMAL_SEEDS
from raven_mcs.utils.serialization import dump_json

from .constants import CORRECTIVE_METHOD, art_path, e3_path, parent_path


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ref(root: Path, dataset: str, seed: int) -> Path:
    return e3_path(root) / "runs" / dataset / "raven" / f"seed{seed}" / "final_metrics.json"


def _ablation_metrics(root: Path, art: Path, dataset: str, method: str, seed: int) -> Path:
    if method == CORRECTIVE_METHOD:
        return art / "corrective_runs" / dataset / method / f"seed{seed}" / "final_metrics.json"
    return parent_path(root) / "runs" / dataset / method / f"seed{seed}" / "final_metrics.json"


def _paired(root: Path, art: Path, dataset: str, method: str, metric: str) -> list[float]:
    diffs = []
    for seed in FORMAL_SEEDS:
        ref = float(_load(_ref(root, dataset, seed))[metric])
        ab = float(_load(_ablation_metrics(root, art, dataset, method, seed))[metric])
        d = ab - ref
        if abs(d) < EPS_ZERO:
            d = 0.0
        diffs.append(d)
    return diffs


def _wilcoxon(diffs: list[float]) -> tuple[float, float]:
    arr = np.asarray(diffs, dtype=float)
    if np.allclose(arr, 0.0, atol=EPS_ZERO):
        return 0.0, 1.0
    try:
        stat, p = wilcoxon(arr, zero_method="wilcox", alternative="two-sided")
        return float(stat), float(p)
    except ValueError:
        return 0.0, 1.0


def _effect(diffs: np.ndarray) -> float:
    sd = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
    return 0.0 if sd < EPS_ZERO else float(np.mean(diffs) / sd)


def summarize(root: Path, art: Path, dataset: str, method: str, metric: str) -> dict[str, Any]:
    diffs = _paired(root, art, dataset, method, metric)
    arr = np.asarray(diffs, dtype=float)
    ref_vals = [float(_load(_ref(root, dataset, seed))[metric]) for seed in FORMAL_SEEDS]
    ab_vals = [
        float(_load(_ablation_metrics(root, art, dataset, method, seed))[metric])
        for seed in FORMAL_SEEDS
    ]
    mean_ref = float(np.mean(ref_vals))
    mean_ab = float(np.mean(ab_vals))
    rel = (mean_ab - mean_ref) / mean_ref if abs(mean_ref) > EPS_ZERO else float("nan")
    n = len(arr)
    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0
    stat, p = _wilcoxon(diffs)
    return {
        "dataset": dataset,
        "method": method,
        "component": COMPONENT[method],
        "metric": metric,
        "family": (
            "primary" if metric in PRIMARY_METRICS
            else ("secondary" if metric in SECONDARY_METRICS else "optional")
        ),
        "mean_raven": mean_ref,
        "mean_ablation": mean_ab,
        "mean_paired_diff": float(np.mean(arr)),
        "median_paired_diff": float(np.median(arr)),
        "relative_change": rel,
        "ci95_low": float(np.mean(arr) - 1.96 * se),
        "ci95_high": float(np.mean(arr) + 1.96 * se),
        "wilcoxon_stat": stat,
        "p_raw": p,
        "effect_size_paired": _effect(arr),
        "wins_ablation_worse": int(np.sum(arr > EPS_ZERO)),
        "ties": int(np.sum(np.abs(arr) <= EPS_ZERO)),
        "losses_ablation_better": int(np.sum(arr < -EPS_ZERO)),
        "n": len(diffs),
        "evidence": "corrective" if method == CORRECTIVE_METHOD else "parent",
    }


def _sig_worsen(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row.get("mean_paired_diff", 0.0)) > EPS_ZERO


def _sig_improve(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row.get("mean_paired_diff", 0.0)) < -EPS_ZERO


def classify_r2(paired_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Statuses: CORE / STRUCTURAL_ONLY / PREDICTION_ONLY / ENDPOINT_TRADEOFF /
    NO_CLEAR_EFFECT / COUNTEREVIDENCE. Design→ENDPOINT_TRADEOFF if mixed;
    Debt small_effect preference via STRUCTURAL_ONLY when tiny relatives."""
    by_comp: dict[str, list[dict[str, Any]]] = {COMPONENT[m]: [] for m in ABLATIONS}
    for row in paired_rows:
        if row["method"] in ABLATIONS and row["metric"] in PRIMARY_METRICS + SECONDARY_METRICS:
            by_comp[row["component"]].append(row)

    claims = {}
    for method in ABLATIONS:
        comp = COMPONENT[method]
        rows = by_comp[comp]
        struct = [r for r in rows if r["metric"] in PRIMARY_METRICS]
        pred = [r for r in rows if r["metric"] in SECONDARY_METRICS]
        ss_w = [r for r in struct if r["dataset"] == "sensorscope" and _sig_worsen(r)]
        ua_w = [r for r in struct if r["dataset"] == "uair" and _sig_worsen(r)]
        ss_i = [r for r in struct if r["dataset"] == "sensorscope" and _sig_improve(r)]
        ua_i = [r for r in struct if r["dataset"] == "uair" and _sig_improve(r)]
        ss_pred = [r for r in pred if r["dataset"] == "sensorscope" and _sig_worsen(r)]
        ua_pred = [r for r in pred if r["dataset"] == "uair" and _sig_worsen(r)]
        counter = [r for r in struct if _sig_improve(r)]
        mixed = (ss_w or ua_w) and (ss_i or ua_i)

        if mixed or (comp == "Design" and counter and (ss_w or ua_w)):
            status = "ENDPOINT_TRADEOFF"
        elif counter and not (ss_w or ua_w):
            status = "COUNTEREVIDENCE"
        elif ss_w and ua_w:
            status = "CORE" if (ss_pred or ua_pred) else "STRUCTURAL_ONLY"
        elif ss_w or ua_w:
            # Debt: tiny relatives stay STRUCTURAL_ONLY / small effect note
            status = "STRUCTURAL_ONLY"
        elif ss_pred or ua_pred:
            status = "PREDICTION_ONLY"
        else:
            status = "NO_CLEAR_EFFECT"

        if comp == "Debt" and status in {"CORE", "STRUCTURAL_ONLY"}:
            # Prefer small-effect structural reading when relatives are tiny
            max_rel = max(abs(float(r["relative_change"])) for r in struct)
            if max_rel < 1e-3:
                status = "STRUCTURAL_ONLY"

        cells = {}
        for dataset in ("sensorscope", "uair"):
            for metric in PRIMARY_METRICS + SECONDARY_METRICS:
                match = next(r for r in rows if r["dataset"] == dataset and r["metric"] == metric)
                key = f"{'SensorScope' if dataset == 'sensorscope' else 'UAir'}_{metric}"
                cells[key] = {
                    "direction": match["direction"],
                    "mean_paired_diff": match["mean_paired_diff"],
                    "relative_change": match["relative_change"],
                    "p_holm": match["p_holm"],
                    "holm_significant": match["holm_significant"],
                    "effect_size_paired": match["effect_size_paired"],
                }

        wording = {
            "CORE": f"{comp} removal worsens structural mismatch consistently; prediction also degrades on at least one dataset.",
            "STRUCTURAL_ONLY": f"{comp} shows structural evidence without robust prediction degradation.",
            "PREDICTION_ONLY": f"{comp} shows prediction degradation without corresponding structural support.",
            "ENDPOINT_TRADEOFF": f"{comp} shows mixed structural directions across endpoints/datasets (endpoint tradeoff).",
            "COUNTEREVIDENCE": f"{comp} removal improves structural metrics in a manner that contradicts the mechanism claim.",
            "NO_CLEAR_EFFECT": f"{comp} shows no clear sealed E4 effect under the pre-registered Holm families.",
        }[status]
        if comp == "Debt" and status == "STRUCTURAL_ONLY":
            wording = "Debt shows a small structural effect without robust prediction degradation."

        claims[comp] = {
            "component": comp,
            "method": method,
            "status": status,
            "paper_safe_wording": wording,
            "sensorscope_structural": bool(ss_w),
            "uair_structural": bool(ua_w),
            "sensorscope_prediction": bool(ss_pred),
            "uair_prediction": bool(ua_pred),
            "cells": cells,
        }
    return claims


def run_analysis_r2(root: Path) -> dict[str, Any]:
    art = art_path(root)
    seal = json.loads((art / "E4_CORRECTIVE_RAW_RESULTS_SEAL.json").read_text(encoding="utf-8"))
    if seal.get("status") != "SEALED":
        raise RuntimeError("corrective raw results not SEALED")

    paired = []
    for dataset in DATASETS:
        for method in ABLATIONS:
            for metric in ALL_METRICS:
                paired.append(summarize(root, art, dataset, method, metric))
    paired = apply_holm_by_family(paired)
    for r in paired:
        r["direction"] = (
            "worsened" if r["mean_paired_diff"] > EPS_ZERO
            else ("improved" if r["mean_paired_diff"] < -EPS_ZERO else "tie")
        )

    # write paired / effects
    def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        with path.open("w", newline="", encoding="utf-8") as handle:
            w = csv.DictWriter(handle, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    _csv(art / "E4_ABLATION_PAIRED_TESTS_R2.csv", paired)
    dump_json({"eps_zero": EPS_ZERO, "rows": paired}, art / "E4_ABLATION_PAIRED_TESTS_R2.json")
    inst_only = [r for r in paired if r["method"] == CORRECTIVE_METHOD]
    _csv(art / "E4_INST_CORRECTED_STATS.csv", inst_only)

    claims = classify_r2(paired)
    dump_json(claims, art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.json")
    lines = ["# E4 component claim matrix FINAL R2", ""]
    for comp, payload in claims.items():
        lines.append(f"## {comp}")
        lines.append(f"- status: `{payload['status']}`")
        lines.append(f"- wording: {payload['paper_safe_wording']}")
        lines.append("")
    (art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # contribution matrix csv
    contrib = []
    for comp, payload in claims.items():
        contrib.append({
            "component": comp,
            "status": payload["status"],
            **{k: json.dumps(v) for k, v in payload["cells"].items()},
        })
    _csv(art / "E4_COMPONENT_CONTRIBUTION_MATRIX_R2.csv", contrib)

    interpretation = {
        "round": "E4-ABLATION-SEMANTIC-INTEGRITY-REPAIR-R1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claims": {k: {"status": v["status"], "wording": v["paper_safe_wording"]} for k, v in claims.items()},
        "inst_note": "Inst claims recomputed from 40 corrective raven_wo_inst runs with P2 invoked.",
        "design_note": "Design retained as ENDPOINT_TRADEOFF when mixed structural directions; no Design rerun.",
        "next_step_decision": "DO_NOT_LAUNCH_E5",
        "next_step_rationale": (
            "Semantic integrity repair closes the invalid Inst evidence and reclassifies claims. "
            "Do not auto-launch E5 from this round; decide E5 only after paper-facing review of R2 claims."
        ),
    }
    dump_json(interpretation, art / "E4_INTERPRETATION_R2.json")
    (art / "E4_INTERPRETATION_R2.md").write_text(
        "# E4 interpretation R2\n\n"
        + "\n".join(f"- **{k}**: `{v['status']}` — {v['wording']}" for k, v in interpretation["claims"].items())
        + f"\n\n## Next step\n`{interpretation['next_step_decision']}`\n\n"
        + interpretation["next_step_rationale"]
        + "\n",
        encoding="utf-8",
    )
    dump_json(
        {
            "decision": interpretation["next_step_decision"],
            "rationale": interpretation["next_step_rationale"],
            "e5_launched": False,
        },
        art / "E4_NEXT_STEP_DECISION.json",
    )
    return {"n_paired": len(paired), "claims": claims, "interpretation": interpretation}
