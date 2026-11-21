"""Post-seal paired E4 ablation analysis (EPS_ZERO=1e-12)."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import wilcoxon

from .constants import ABLATIONS, DATASETS, FORMAL_SEEDS


def holm_adjust(pvals: list[float]) -> list[float]:
    """Holm step-down adjusted p-values (same family, ascending raw p)."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    adjusted = [0.0] * n
    running = 0.0
    for rank, idx in enumerate(order):
        candidate = (n - rank) * float(pvals[idx])
        running = max(running, candidate)
        adjusted[idx] = min(1.0, running)
    return adjusted

EPS_ZERO = 1e-12
PRIMARY_METRICS = ("Delta_group", "Delta_c_s")
SECONDARY_METRICS = ("RMSE_mu", "Tail_RMSE")
OPTIONAL_METRICS = ("MAE_mu",)
ALL_METRICS = PRIMARY_METRICS + SECONDARY_METRICS + OPTIONAL_METRICS
COMPONENT = {
    "raven_wo_design": "Design",
    "raven_wo_obs": "Obs",
    "raven_wo_use": "Use",
    "raven_wo_inst": "Inst",
    "raven_wo_debt": "Debt",
}


def _load_metrics(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ref_path(root: Path, dataset: str, seed: int) -> Path:
    return Path(root) / "artifacts/e3_formal_runs_r1/runs" / dataset / "raven" / f"seed{seed}" / "final_metrics.json"


def _ab_path(art: Path, dataset: str, method: str, seed: int) -> Path:
    return Path(art) / "runs" / dataset / method / f"seed{seed}" / "final_metrics.json"


def paired_diffs(root: Path, art: Path, dataset: str, method: str, metric: str) -> list[float]:
    diffs = []
    for seed in FORMAL_SEEDS:
        ref = float(_load_metrics(_ref_path(root, dataset, seed))[metric])
        ab = float(_load_metrics(_ab_path(art, dataset, method, seed))[metric])
        d = ab - ref
        if abs(d) < EPS_ZERO:
            d = 0.0
        diffs.append(d)
    return diffs


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
    # normal approx for reporting; exact Wilcoxon CI is not required by gates
    return mean - 1.96 * se, mean + 1.96 * se


def _wilcoxon(diffs: list[float]) -> tuple[float, float]:
    arr = np.asarray(diffs, dtype=float)
    if np.allclose(arr, 0.0, atol=EPS_ZERO):
        return 0.0, 1.0
    try:
        stat, p = wilcoxon(arr, zero_method="wilcox", alternative="two-sided")
        return float(stat), float(p)
    except ValueError:
        return 0.0, 1.0


def summarize_comparison(root: Path, art: Path, dataset: str, method: str, metric: str) -> dict[str, Any]:
    diffs = paired_diffs(root, art, dataset, method, metric)
    arr = np.asarray(diffs, dtype=float)
    wins = int(np.sum(arr > EPS_ZERO))  # ablation worse (higher metric)
    losses = int(np.sum(arr < -EPS_ZERO))  # ablation better
    ties = int(np.sum(np.abs(arr) <= EPS_ZERO))
    ref_vals = [
        float(_load_metrics(_ref_path(root, dataset, seed))[metric]) for seed in FORMAL_SEEDS
    ]
    ab_vals = [
        float(_load_metrics(_ab_path(art, dataset, method, seed))[metric]) for seed in FORMAL_SEEDS
    ]
    mean_ref = float(np.mean(ref_vals))
    mean_ab = float(np.mean(ab_vals))
    rel = (mean_ab - mean_ref) / mean_ref if abs(mean_ref) > EPS_ZERO else float("nan")
    lo, hi = _ci95(arr)
    stat, p = _wilcoxon(diffs)
    return {
        "dataset": dataset,
        "method": method,
        "component": COMPONENT[method],
        "metric": metric,
        "family": "primary" if metric in PRIMARY_METRICS else ("secondary" if metric in SECONDARY_METRICS else "optional"),
        "mean_raven": mean_ref,
        "std_raven": float(np.std(ref_vals, ddof=1)),
        "mean_ablation": mean_ab,
        "std_ablation": float(np.std(ab_vals, ddof=1)),
        "mean_paired_diff": float(np.mean(arr)),
        "median_paired_diff": float(np.median(arr)),
        "relative_change": rel,
        "ci95_low": lo,
        "ci95_high": hi,
        "wilcoxon_stat": stat,
        "p_raw": p,
        "effect_size_paired": _effect_size(arr),
        "wins_ablation_worse": wins,
        "ties": ties,
        "losses_ablation_better": losses,
        "n": len(diffs),
        "eps_zero": EPS_ZERO,
    }


def apply_holm_by_family(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Primary: per dataset × structural metric → 5 ablations
    # Secondary: per dataset × prediction metric → 5 ablations
    out = [dict(r) for r in rows]
    index = {id(r): i for i, r in enumerate(out)}
    for dataset in DATASETS:
        for metric in PRIMARY_METRICS + SECONDARY_METRICS:
            idxs = [
                i
                for i, r in enumerate(out)
                if r["dataset"] == dataset and r["metric"] == metric and r["method"] in ABLATIONS
            ]
            if not idxs:
                continue
            pvals = [out[i]["p_raw"] for i in idxs]
            adj = holm_adjust(pvals)
            for i, p_h in zip(idxs, adj):
                out[i]["p_holm"] = float(p_h)
                out[i]["holm_family"] = f"{dataset}::{metric}"
    for r in out:
        r.setdefault("p_holm", r["p_raw"])
        r.setdefault("holm_family", "unassigned")
        r["holm_significant"] = bool(r["p_holm"] < 0.05)
        r["direction"] = (
            "worsened"
            if r["mean_paired_diff"] > EPS_ZERO
            else ("improved" if r["mean_paired_diff"] < -EPS_ZERO else "tie")
        )
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_analysis(root: Path, art: Path) -> dict[str, Any]:
    art = Path(art)
    root = Path(root)
    paired_rows = []
    for dataset in DATASETS:
        for method in ABLATIONS:
            for metric in ALL_METRICS:
                paired_rows.append(summarize_comparison(root, art, dataset, method, metric))
    paired_rows = apply_holm_by_family(paired_rows)

    summary = []
    for dataset in DATASETS:
        for method in ["raven", *ABLATIONS]:
            row: dict[str, Any] = {"dataset": dataset, "method": method}
            for metric in PRIMARY_METRICS + SECONDARY_METRICS:
                vals = []
                for seed in FORMAL_SEEDS:
                    if method == "raven":
                        vals.append(float(_load_metrics(_ref_path(root, dataset, seed))[metric]))
                    else:
                        vals.append(float(_load_metrics(_ab_path(art, dataset, method, seed))[metric]))
                row[f"{metric}_mean"] = float(np.mean(vals))
                row[f"{metric}_std"] = float(np.std(vals, ddof=1))
            summary.append(row)

    effect_rows = [
        {
            "dataset": r["dataset"],
            "component": r["component"],
            "method": r["method"],
            "metric": r["metric"],
            "mean_paired_diff": r["mean_paired_diff"],
            "relative_change": r["relative_change"],
            "effect_size_paired": r["effect_size_paired"],
            "p_holm": r["p_holm"],
            "holm_significant": r["holm_significant"],
            "direction": r["direction"],
        }
        for r in paired_rows
        if r["metric"] in PRIMARY_METRICS + SECONDARY_METRICS
    ]

    holm_rows = [
        {
            "holm_family": r["holm_family"],
            "dataset": r["dataset"],
            "method": r["method"],
            "component": r["component"],
            "metric": r["metric"],
            "p_raw": r["p_raw"],
            "p_holm": r["p_holm"],
            "holm_significant": r["holm_significant"],
            "mean_paired_diff": r["mean_paired_diff"],
        }
        for r in paired_rows
        if r["metric"] in PRIMARY_METRICS + SECONDARY_METRICS
    ]

    write_csv(art / "E4_ABLATION_SUMMARY.csv", summary)
    write_csv(art / "E4_ABLATION_PAIRED_TESTS.csv", paired_rows)
    write_csv(art / "E4_ABLATION_HOLM_RESULTS.csv", holm_rows)
    write_csv(art / "E4_ABLATION_EFFECT_SIZES.csv", effect_rows)
    (art / "E4_ABLATION_PAIRED_TESTS.json").write_text(
        json.dumps({"eps_zero": EPS_ZERO, "rows": paired_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"eps_zero": EPS_ZERO, "n_paired_rows": len(paired_rows), "status": "COMPLETE"}
