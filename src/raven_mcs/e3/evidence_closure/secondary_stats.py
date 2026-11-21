"""Secondary sealed-result inference with explicit comparability exclusions."""

from __future__ import annotations

from typing import Any

from raven_mcs.e3.formal.stats import EPS_ZERO, holm, paired_summary, summarize_vector

__all__ = ("EPS_ZERO", "holm", "paired_summary", "summarize_vector", "secondary_rows")


def secondary_rows(
    dataset: str, metric: str, raven: dict[int, float], baseline: dict[int, float], baseline_name: str,
    comparability: str, validity: str = "VALID",
) -> dict[str, Any]:
    """Produce one transparent comparison row; callers omit non-comparable families."""
    result = paired_summary(raven, baseline)
    r_sum, b_sum = summarize_vector(list(raven.values())), summarize_vector(list(baseline.values()))
    relative = None
    if b_sum["mean"] not in (None, 0):
        relative = result["mean_diff_raven_minus_baseline"] / b_sum["mean"]
    return {
        "dataset": dataset, "metric": metric, "baseline": baseline_name,
        "raven_mean": r_sum["mean"], "raven_std": r_sum["std"],
        "baseline_mean": b_sum["mean"], "baseline_std": b_sum["std"],
        "relative_difference": relative, "comparability_status": comparability,
        "baseline_validity_status": validity, **{k: v for k, v in result.items() if k != "seeds"},
    }
