"""Gate confusion and routing helpers for R1j. Evaluation only."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd

from raven_mcs.sag.r1j_spec import (
    BALANCED_ACC_MIN,
    FALSE_SAFE_MAX,
    JOINT_VALID_MIN,
    NONVACUOUS_ZERO_MAX,
    NUM_TOL,
)


def classify(y_oracle: bool, y_cert: bool) -> str:
    if y_cert and y_oracle:
        return "TRUE_SAFE"
    if (not y_cert) and (not y_oracle):
        return "TRUE_UNSAFE"
    if y_cert and (not y_oracle):
        return "FALSE_SAFE"
    return "FALSE_UNSAFE"


def confusion_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {
            "n": 0, "TP": 0, "TN": 0, "FP": 0, "FN": 0,
            "false_safe_rate": float("nan"), "false_unsafe_rate": float("nan"),
            "precision_safe": float("nan"), "recall_safe": float("nan"),
            "specificity": float("nan"), "balanced_accuracy": float("nan"),
            "accuracy": float("nan"),
        }
    yo = frame["Y_oracle"].astype(bool)
    yc = frame["Y_cert"].astype(bool)
    tp = int((yc & yo).sum())
    tn = int((~yc & ~yo).sum())
    fp = int((yc & ~yo).sum())
    fn = int((~yc & yo).sum())
    n = int(len(frame))
    fsr = float(fp / (fp + tn)) if (fp + tn) else 0.0
    fur = float(fn / (fn + tp)) if (fn + tp) else 0.0
    prec = float(tp / (tp + fp)) if (tp + fp) else float("nan")
    rec = float(tp / (tp + fn)) if (tp + fn) else float("nan")
    spec = float(tn / (tn + fp)) if (tn + fp) else float("nan")
    ba = float(np.nanmean([rec, spec]))
    acc = float((tp + tn) / n) if n else float("nan")
    return {
        "n": n, "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "false_safe_rate": fsr, "false_unsafe_rate": fur,
        "precision_safe": prec, "recall_safe": rec,
        "specificity": spec, "balanced_accuracy": ba, "accuracy": acc,
    }


def dataset_verdict(
    *,
    joint_validity: float,
    false_safe_rate: float,
    false_unsafe_rate: float,
    balanced_accuracy: float,
    fraction_zero: float,
    boundary_has_both_cert: bool,
    all_ccov_zero_on_boundary: bool,
) -> str:
    if not np.isfinite(joint_validity) or joint_validity + NUM_TOL < JOINT_VALID_MIN or false_safe_rate > FALSE_SAFE_MAX:
        return "NOT_CALIBRATED"
    if all_ccov_zero_on_boundary or (not boundary_has_both_cert and fraction_zero >= 0.99):
        return "NO_DISCRIMINATION"
    if (
        joint_validity >= JOINT_VALID_MIN
        and false_safe_rate <= FALSE_SAFE_MAX
        and balanced_accuracy >= BALANCED_ACC_MIN
        and fraction_zero <= NONVACUOUS_ZERO_MAX
        and boundary_has_both_cert
        and not all_ccov_zero_on_boundary
    ):
        return "DYNAMIC_CERTIFICATE_USABLE"
    if joint_validity >= JOINT_VALID_MIN and false_safe_rate <= FALSE_SAFE_MAX:
        return "SAFE_BUT_TOO_CONSERVATIVE"
    return "NO_DISCRIMINATION"


def overall_verdict(ss: str, ua: str) -> str:
    if ss == "DYNAMIC_CERTIFICATE_USABLE" and ua != "NOT_CALIBRATED":
        if ua == "DYNAMIC_CERTIFICATE_USABLE":
            return "READY_FOR_SAG_1SEED_FUNCTIONAL_VALIDATION"
        if ua in {"SAFE_BUT_TOO_CONSERVATIVE", "NO_DISCRIMINATION"}:
            return "READY_FOR_LIMITED_SAG_1SEED_VALIDATION"
        return "READY_FOR_SAG_1SEED_FUNCTIONAL_VALIDATION"
    if ss == "SAFE_BUT_TOO_CONSERVATIVE":
        return "R1J_CERTIFICATE_TOO_CONSERVATIVE"
    if ss == "NOT_CALIBRATED" or ua == "NOT_CALIBRATED" and ss != "DYNAMIC_CERTIFICATE_USABLE":
        return "R1J_CERTIFICATE_NOT_CALIBRATED"
    if ss == "NO_DISCRIMINATION":
        return "R1J_CERTIFICATE_TOO_CONSERVATIVE"
    return "R1J_CERTIFICATE_NOT_CALIBRATED"
