"""E4 component claim classification from sealed paired tests."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .constants import ABLATIONS
from .analyze import COMPONENT, PRIMARY_METRICS, SECONDARY_METRICS, EPS_ZERO


def _sig_worsen(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row.get("mean_paired_diff", 0.0)) > EPS_ZERO


def _sig_improve(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row.get("mean_paired_diff", 0.0)) < -EPS_ZERO


def classify_components(paired_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_comp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in paired_rows:
        if row["method"] in ABLATIONS and row["metric"] in PRIMARY_METRICS + SECONDARY_METRICS:
            by_comp[row["component"]].append(row)

    matrix_rows = []
    claims = {}
    for method in ABLATIONS:
        comp = COMPONENT[method]
        rows = by_comp[comp]
        struct = [r for r in rows if r["metric"] in PRIMARY_METRICS]
        pred = [r for r in rows if r["metric"] in SECONDARY_METRICS]
        ss_struct = [r for r in struct if r["dataset"] == "sensorscope" and _sig_worsen(r)]
        ua_struct = [r for r in struct if r["dataset"] == "uair" and _sig_worsen(r)]
        ss_pred = [r for r in pred if r["dataset"] == "sensorscope" and _sig_worsen(r)]
        ua_pred = [r for r in pred if r["dataset"] == "uair" and _sig_worsen(r)]
        counter = [r for r in struct if _sig_improve(r)]

        if counter:
            status = "COUNTEREVIDENCE"
        elif ss_struct and ua_struct:
            status = "CORE_MECHANISM_SUPPORTED" if (ss_pred or ua_pred or True) else "CORE_MECHANISM_SUPPORTED"
            # Consistent structural worsening across both datasets
            if not (ss_pred or ua_pred):
                status = "STRUCTURAL_ONLY_SUPPORTED"
            else:
                status = "CORE_MECHANISM_SUPPORTED"
        elif ss_struct or ua_struct:
            status = "STRUCTURAL_ONLY_SUPPORTED"
        elif ss_pred or ua_pred:
            status = "PREDICTION_ONLY_SUPPORTED"
        else:
            status = "NO_CLEAR_EFFECT"

        cell = {}
        for dataset in ("sensorscope", "uair"):
            for metric in PRIMARY_METRICS + SECONDARY_METRICS:
                match = next(r for r in rows if r["dataset"] == dataset and r["metric"] == metric)
                key = f"{'SensorScope' if dataset=='sensorscope' else 'UAir'}_{metric}"
                cell[key] = {
                    "direction": match["direction"],
                    "mean_paired_diff": match["mean_paired_diff"],
                    "relative_change": match["relative_change"],
                    "p_holm": match["p_holm"],
                    "holm_significant": match["holm_significant"],
                }

        claims[comp] = {
            "component": comp,
            "method": method,
            "status": status,
            "sensorscope_structural": bool(ss_struct),
            "uair_structural": bool(ua_struct),
            "sensorscope_prediction": bool(ss_pred),
            "uair_prediction": bool(ua_pred),
            "paper_safe_wording": _wording(comp, status),
            "cells": cell,
        }
        matrix_rows.append({"component": comp, "status": status, **{k: json.dumps(v) for k, v in cell.items()}})

    return {"claims": claims, "contribution_matrix_rows": matrix_rows}


def _wording(comp: str, status: str) -> str:
    if status == "CORE_MECHANISM_SUPPORTED":
        return f"{comp} removal worsens structural mismatch consistently across SensorScope and U-Air."
    if status == "STRUCTURAL_ONLY_SUPPORTED":
        return f"{comp} shows structural evidence without robust prediction degradation."
    if status == "PREDICTION_ONLY_SUPPORTED":
        return f"{comp} shows prediction degradation without corresponding structural support."
    if status == "COUNTEREVIDENCE":
        return f"{comp} removal improves structural metrics in a manner that contradicts the mechanism claim."
    return f"{comp} shows no clear sealed E4 effect under the pre-registered Holm families."


def write_claim_artifacts(art: Path, classified: dict[str, Any]) -> None:
    art = Path(art)
    (art / "E4_COMPONENT_CLAIM_MATRIX.json").write_text(
        json.dumps(classified["claims"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = ["# E4 component claim matrix", ""]
    for comp, payload in classified["claims"].items():
        lines.append(f"## {comp}")
        lines.append(f"- status: `{payload['status']}`")
        lines.append(f"- wording: {payload['paper_safe_wording']}")
        lines.append("")
    (art / "E4_COMPONENT_CLAIM_MATRIX.md").write_text("\n".join(lines), encoding="utf-8")

    import csv

    rows = classified["contribution_matrix_rows"]
    if rows:
        fields = list(rows[0].keys())
        with (art / "E4_COMPONENT_CONTRIBUTION_MATRIX.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
