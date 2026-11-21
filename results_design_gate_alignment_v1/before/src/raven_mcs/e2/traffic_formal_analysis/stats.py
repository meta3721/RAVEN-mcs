"""Transparent paired statistics for E2 formal results analysis."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from raven_mcs.e2.traffic_formal_runs.stats import summarize_vector


def wilcoxon_two_sided(diff: np.ndarray) -> float:
    arr = np.asarray(diff, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0 or not np.any(arr != 0):
        return float("nan")
    try:
        res = stats.wilcoxon(arr, alternative="two-sided", zero_method="wilcox")
        return float(res.pvalue)
    except ValueError:
        return float("nan")


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm–Bonferroni adjusted p-values (same order as input)."""
    n = len(p_values)
    if n == 0:
        return []
    indexed = []
    for i, p in enumerate(p_values):
        indexed.append((i, float("nan") if p is None or not np.isfinite(p) else float(p)))
    ordered = sorted(indexed, key=lambda t: (np.isnan(t[1]), t[1]))
    adj = [float("nan")] * n
    running = 0.0
    for rank, (idx, p) in enumerate(ordered, start=1):
        if np.isnan(p):
            adj[idx] = float("nan")
            continue
        candidate = min(1.0, (n - rank + 1) * p)
        running = max(running, candidate)
        adj[idx] = running
    # Enforce monotonicity in original sorted order (non-decreasing)
    mono = float("nan")
    for idx, p in ordered:
        if np.isnan(adj[idx]):
            continue
        if np.isnan(mono):
            mono = adj[idx]
        else:
            mono = max(mono, adj[idx])
        adj[idx] = mono
    return adj


def win_tie_loss(diff: np.ndarray, *, smaller_better: bool) -> tuple[int, int, int]:
    arr = np.asarray(diff, dtype=np.float64)
    if smaller_better:
        wins = int(np.sum(arr < -1e-12))
        losses = int(np.sum(arr > 1e-12))
    else:
        # For signed diagnostics without smaller-better: count negative/positive only.
        wins = int(np.sum(arr < -1e-12))
        losses = int(np.sum(arr > 1e-12))
    ties = int(arr.size - wins - losses)
    return wins, ties, losses


def paired_scenario_vs_balanced(
    frame: pd.DataFrame,
    *,
    method: str,
    scenario: str,
    metric: str,
    smaller_better: bool,
) -> dict[str, Any]:
    sub_m = frame.loc[frame["method"] == method]
    scen = sub_m.loc[sub_m["scenario"] == scenario].set_index("seed")[metric]
    bal = sub_m.loc[sub_m["scenario"] == "balanced"].set_index("seed")[metric]
    seeds = sorted(set(scen.index) & set(bal.index))
    diff = np.asarray([float(scen.loc[s] - bal.loc[s]) for s in seeds], dtype=np.float64)
    summary = summarize_vector(diff)
    wins, ties, losses = win_tie_loss(diff, smaller_better=smaller_better)
    p_raw = wilcoxon_two_sided(diff)
    direction = "scenario_higher" if summary["mean"] > 0 else ("scenario_lower" if summary["mean"] < 0 else "zero")
    # Simple paired effect size: mean / sd
    effect = float(summary["mean"] / summary["std"]) if summary["std"] and summary["std"] > 0 else float("nan")
    return {
        "method": method,
        "scenario": scenario,
        "metric": metric,
        "n_pairs": int(len(seeds)),
        "mean_diff": summary["mean"],
        "std_diff": summary["std"],
        "median_diff": summary["median"],
        "iqr_diff": summary["iqr"],
        "ci95_low": summary["ci95_low"],
        "ci95_high": summary["ci95_high"],
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "p_raw": p_raw,
        "effect_direction": direction,
        "effect_size_mean_over_sd": effect,
        "test": "wilcoxon_signed_rank_two_sided",
        "zero_difference_policy": "scipy_wilcox_omit_zeros",
        "smaller_better": bool(smaller_better),
    }


def binomial_ci_wilson(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n <= 0:
        return float("nan"), float("nan")
    z = stats.norm.ppf(1 - alpha / 2)
    phat = successes / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return float(max(0.0, center - margin)), float(min(1.0, center + margin))


def group_rmse_spread(group_frame: pd.DataFrame) -> pd.DataFrame:
    """Descriptive disparity from frozen block RMSE (not protocol Delta_group)."""
    rows = []
    for (seed, scenario, method), sub in group_frame.groupby(["seed", "scenario", "method"]):
        vals = sub["RMSE"].astype(float).to_numpy()
        rows.append(
            {
                "seed": int(seed),
                "scenario": scenario,
                "method": method,
                "group_rmse_max": float(np.max(vals)),
                "group_rmse_min": float(np.min(vals)),
                "group_rmse_range": float(np.max(vals) - np.min(vals)),
                "group_rmse_std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                "n_groups": int(len(vals)),
                "metric_definition": "descriptive_block_rmse_range_not_protocol_Delta_group",
            }
        )
    return pd.DataFrame(rows)
