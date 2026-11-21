"""WINDOW_COMPLETENESS_RULE_V1. Outcome-blind. Not an oracle filter."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import pandas as pd

from raven_mcs.utils.hashing import sha256_json

N_EDGE = 3
EXPECTED_SPAN_SECONDS = 3600.0
PARTIAL_COVERAGE_CUTOFF = 0.50


def completeness_rule_payload() -> dict[str, Any]:
    return {
        "rule_id": "WINDOW_COMPLETENESS_RULE_V1",
        "uses_oracle": False,
        "uses_c_cov": False,
        "uses_gate": False,
        "uses_predictor": False,
        "native_slot": "processed hourly UTC hour (time_index)",
        "expected_span_seconds": EXPECTED_SPAN_SECONDS,
        "partial_if_time_coverage_ratio_below": PARTIAL_COVERAGE_CUTOFF,
        "edge_n": N_EDGE,
        "full_interior": "same-split previous and next hours exist and are ±1 hour contiguous; slot is a native 1h hour",
        "full_boundary": "native 1h hour complete, but missing previous or next hour inside the same split",
        "partial_left_right": "observed timestamp span inside the hour is < 50% of 3600s, or split cuts records inside the hour",
        "sparse_within_hour_not_partial": (
            "If the processed matrix is one record per spatial_id per hour, "
            "low entity count is not PARTIAL."
        ),
        "forbidden_fields": [
            "C_oracle_safe",
            "oracle_pass",
            "C_cov",
            "Gate",
            "residual",
        ],
    }


def completeness_rule_hash() -> str:
    return sha256_json(completeness_rule_payload())


def classify_boundary(
    *,
    time_coverage_ratio: float,
    split_truncation_left: bool,
    split_truncation_right: bool,
    prev_same_split_contiguous: bool,
    next_same_split_contiguous: bool,
    slot_has_records: bool,
) -> str:
    if not slot_has_records:
        return "UNKNOWN_COMPLETENESS"
    if time_coverage_ratio + 1e-12 < PARTIAL_COVERAGE_CUTOFF:
        if split_truncation_left and split_truncation_right:
            return "PARTIAL_BOTH"
        if split_truncation_left:
            return "PARTIAL_LEFT"
        if split_truncation_right:
            return "PARTIAL_RIGHT"
        return "PARTIAL_BOTH"
    if prev_same_split_contiguous and next_same_split_contiguous:
        return "FULL_INTERIOR"
    return "FULL_BOUNDARY"


def hour_span_seconds(timestamps: Sequence) -> float:
    ts = pd.to_datetime(pd.Series(list(timestamps)), utc=True)
    if ts.empty:
        return 0.0
    span = (ts.max() - ts.min()).total_seconds()
    if span <= 1.0:
        return EXPECTED_SPAN_SECONDS
    return float(min(span, EXPECTED_SPAN_SECONDS))
