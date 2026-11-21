"""Formal paired inference helpers (post-seal only)."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

EPS_ZERO = 1e-12

MAIN_BASELINES = (
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "local_hajek",
    "twostage_hajek",
)


def signed_difference(a: float, b: float) -> float:
    delta = float(a) - float(b)
    return 0.0 if abs(delta) <= EPS_ZERO else delta


def holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda x: x[1])
    n = len(ordered)
    out: dict[str, float] = {}
    prior = 0.0
    for i, (name, p) in enumerate(ordered):
        adj = min(1.0, float(p) * (n - i))
        prior = max(prior, adj)
        out[name] = prior
    return out


def wilcoxon_signed_rank_two_sided(diffs: list[float]) -> tuple[float, str]:
    """Approximate Wilcoxon via scipy if available; else sign-test fallback."""
    arr = np.asarray([d for d in diffs if abs(d) > EPS_ZERO], dtype=float)
    if arr.size == 0:
        return 1.0, "ALL_TIES"
    try:
        from scipy.stats import wilcoxon

        res = wilcoxon(arr, alternative="two-sided", zero_method="wilcox")
        return float(res.pvalue), "WILCOXON"
    except Exception:  # noqa: BLE001
        pos = int(np.sum(arr > 0))
        neg = int(np.sum(arr < 0))
        n = pos + neg
        if n == 0:
            return 1.0, "ALL_TIES"
        # two-sided binomial sign test
        from math import comb

        k = min(pos, neg)
        p = sum(comb(n, i) for i in range(0, k + 1)) / (2 ** (n - 1))
        return float(min(1.0, p)), "SIGN_TEST"


def paired_summary(
    raven: dict[int, float],
    baseline: dict[int, float],
) -> dict[str, Any]:
    seeds = sorted(set(raven) & set(baseline))
    diffs = [signed_difference(raven[s], baseline[s]) for s in seeds]
    nonzero = [d for d in diffs if abs(d) > EPS_ZERO]
    wins = sum(1 for d in nonzero if d < 0)  # smaller RMSE better
    losses = sum(1 for d in nonzero if d > 0)
    ties = len(diffs) - len(nonzero)
    p, status = wilcoxon_signed_rank_two_sided(diffs)
    mean_diff = float(np.mean(diffs)) if diffs else float("nan")
    # effect size: paired Cohen-like
    sd = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else float("nan")
    effect = mean_diff / sd if sd and math.isfinite(sd) and sd > 0 else float("nan")
    return {
        "n": len(seeds),
        "mean_diff_raven_minus_baseline": mean_diff,
        "effect_size": effect,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "p_raw": p,
        "test_status": status,
        "seeds": seeds,
    }


def summarize_vector(vals: list[float]) -> dict[str, Any]:
    arr = np.asarray(vals, dtype=float)
    if arr.size == 0:
        return {"n": 0, "mean": None, "std": None, "median": None, "ci95_low": None, "ci95_high": None}
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
    se = std / math.sqrt(arr.size) if arr.size > 0 else float("nan")
    return {
        "n": int(arr.size),
        "mean": mean,
        "std": std,
        "median": float(np.median(arr)),
        "ci95_low": mean - 1.96 * se,
        "ci95_high": mean + 1.96 * se,
    }
