"""Routing helpers for R1k architecture audit. Evaluation only."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.sag.r1j_eval import classify, confusion_metrics
from raven_mcs.sag.r1k_spec import (
    BALANCED_ACC_MIN,
    FALSE_SAFE_MAX,
    NONVACUOUS_ZERO_MAX,
    NUM_TOL,
    SCALE_LIFT_MIN,
    VALIDITY_MIN,
)

__all__ = ["classify", "confusion_metrics", "pairwise_barrier_verdict", "scale_verdict", "aggregate_verdict", "overall_verdict", "theory_decision"]


def pairwise_barrier_verdict(*, boundary_a_blocked: bool, derivation_ok: bool) -> str:
    if not derivation_ok:
        return "PAIRWISE_BARRIER_EVIDENCE_FAILURE"
    if boundary_a_blocked:
        return "STRUCTURAL_PAIRWISE_NONVACUITY_BARRIER_CONFIRMED"
    return "PAIRWISE_BARRIER_NOT_ESTABLISHED"


def scale_verdict(
    *,
    median_cond_over_old: float,
    corr_old: float,
    corr_cond: float,
    mae_old: float,
    mae_cond: float,
) -> str:
    lift = np.isfinite(median_cond_over_old) and median_cond_over_old >= SCALE_LIFT_MIN
    corr_better = (
        np.isfinite(corr_cond)
        and ((not np.isfinite(corr_old)) or (corr_cond > corr_old + 0.02))
    )
    mae_better = np.isfinite(mae_cond) and np.isfinite(mae_old) and mae_cond + NUM_TOL < mae_old
    if lift and (corr_better or mae_better):
        return "PREDICTOR_SCALE_DEFECT_CONFIRMED"
    if lift or corr_better or mae_better:
        return "PREDICTOR_SCALE_DEFECT_PARTIAL"
    if np.isfinite(median_cond_over_old):
        return "NO_MAJOR_SCALE_DEFECT"
    return "SCALE_AUDIT_FAILURE"


def aggregate_verdict(
    *,
    validity: float,
    false_safe_rate: float,
    balanced_accuracy: float,
    fraction_zero: float,
    boundary_has_both: bool,
    all_lcb_zero_on_boundary: bool,
) -> str:
    if not np.isfinite(validity) or validity + NUM_TOL < VALIDITY_MIN or (
        np.isfinite(false_safe_rate) and false_safe_rate > FALSE_SAFE_MAX
    ):
        return "AGGREGATE_NOT_CALIBRATED"
    if all_lcb_zero_on_boundary or (not boundary_has_both and fraction_zero >= 0.99):
        return "AGGREGATE_NO_DISCRIMINATION"
    if (
        validity >= VALIDITY_MIN
        and false_safe_rate <= FALSE_SAFE_MAX
        and balanced_accuracy >= BALANCED_ACC_MIN
        and fraction_zero <= NONVACUOUS_ZERO_MAX
        and boundary_has_both
        and not all_lcb_zero_on_boundary
    ):
        return "AGGREGATE_CERTIFICATE_FEASIBLE_CANDIDATE"
    if validity >= VALIDITY_MIN and false_safe_rate <= FALSE_SAFE_MAX:
        return "AGGREGATE_SAFE_BUT_CONSERVATIVE"
    return "AGGREGATE_NO_DISCRIMINATION"


def overall_verdict(pair_v: str, scale_v: str, agg_v: str, *, agg_better: bool = False) -> str:
    barrier = pair_v == "STRUCTURAL_PAIRWISE_NONVACUITY_BARRIER_CONFIRMED"
    if barrier and agg_v == "AGGREGATE_CERTIFICATE_FEASIBLE_CANDIDATE":
        return "CERTIFICATE_ARCHITECTURE_REDESIGN_RECOMMENDED"
    if barrier and agg_better and agg_v == "AGGREGATE_SAFE_BUT_CONSERVATIVE":
        return "CERTIFICATE_ARCHITECTURE_REDESIGN_RECOMMENDED"
    if (not barrier) and scale_v == "PREDICTOR_SCALE_DEFECT_CONFIRMED":
        return "PAIRWISE_IMPLEMENTATION_REPAIR_RECOMMENDED"
    if not barrier:
        return "PAIRWISE_ARCHITECTURE_REMAINS_VIABLE"
    return "R1K_ARCHITECTURE_AUDIT_INCONCLUSIVE"


def theory_decision(overall: str, pair_v: str, scale_v: str) -> str:
    if overall == "CERTIFICATE_ARCHITECTURE_REDESIGN_RECOMMENDED":
        return "CERTIFICATE_ARCHITECTURE_REDESIGN_RECOMMENDED"
    if overall == "PAIRWISE_IMPLEMENTATION_REPAIR_RECOMMENDED" or (
        scale_v == "PREDICTOR_SCALE_DEFECT_CONFIRMED" and pair_v != "STRUCTURAL_PAIRWISE_NONVACUITY_BARRIER_CONFIRMED"
    ):
        return "PAIRWISE_IMPLEMENTATION_REPAIR_ONLY"
    if overall == "PAIRWISE_ARCHITECTURE_REMAINS_VIABLE":
        return "NO_THEORY_CHANGE_NEEDED"
    return "THEORY_DECISION_INCONCLUSIVE"


def slice_metrics(frame: pd.DataFrame, y_col: str = "Y_agg") -> dict[str, Any]:
    sub = frame.copy()
    if y_col != "Y_cert" and y_col in sub.columns:
        sub = sub.rename(columns={y_col: "Y_cert"})
    return confusion_metrics(sub)
