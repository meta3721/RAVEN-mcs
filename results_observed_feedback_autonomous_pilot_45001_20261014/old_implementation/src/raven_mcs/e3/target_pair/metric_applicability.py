"""Metric applicability matrix and N/A emission policy (mechanism-aware)."""

from __future__ import annotations

from typing import Any

import numpy as np

from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.e3.delta_cs_rho.constants import METRIC_SCHEMA_VERSION
from raven_mcs.e3.target_pair.errors import CentralMetricApplicabilityError

APPLICABLE = "APPLICABLE"
NOT_APPLICABLE = "NOT_APPLICABLE"
UNAVAILABLE = "UNAVAILABLE_WITH_REASON"
NOT_MATERIALIZED = "NOT_MATERIALIZED"

CENTRAL_METHODS = {"central_all", "central_delivered"}

# Atomic Delta_pair is not materialized by the client×group V4/V5 representation.
ATOMIC_DELTA_PAIR_STATUS = NOT_MATERIALIZED

ALL_METRICS = [
    "RMSE_mu",
    "MAE_mu",
    "Head_RMSE",
    "Tail_RMSE",
    "RMSE_rho",
    "Delta_group",
    "Delta_c_s",
    "Delta_pair",
    "delta_ref",
    "Q_norm1_over_S",
    "Q_norm2_over_S",
    "ESS",
    "clip_rate_stage1",
    "clip_rate_stage2",
    "solver_status",
    "runtime_seconds",
]


class MechanismMetricApplicabilityError(RuntimeError):
    CODE = "MECHANISM_METRIC_APPLICABILITY_ERROR"


def applicability_for(method: str, metric: str) -> str:
    if method in CENTRAL_METHODS:
        return _central_applicability(metric)
    return _federated_applicability(method, metric)


def _central_applicability(metric: str) -> str:
    if metric in {
        "RMSE_mu",
        "MAE_mu",
        "Head_RMSE",
        "Tail_RMSE",
        "RMSE_rho",
        "solver_status",
        "runtime_seconds",
    }:
        return APPLICABLE
    if metric == "Delta_pair":
        return NOT_MATERIALIZED
    return NOT_APPLICABLE


def _federated_applicability(method: str, metric: str) -> str:
    policy = get_method_policy(method)
    if metric == "Delta_pair":
        return NOT_MATERIALIZED
    if metric == "Delta_c_s":
        return APPLICABLE
    if metric in {"Q_norm1_over_S", "Q_norm2_over_S"}:
        return APPLICABLE if policy.uses_debt else NOT_APPLICABLE
    if metric == "delta_ref":
        return APPLICABLE if policy.uses_reference_penalty else NOT_APPLICABLE
    if metric in {"clip_rate_stage1", "clip_rate_stage2", "ESS", "Delta_group"}:
        return APPLICABLE
    if metric in ALL_METRICS:
        return APPLICABLE
    return UNAVAILABLE


def mechanism_metric_applicability_matrix() -> dict[str, Any]:
    methods = [
        "fedavg_window",
        "fedasync_window",
        "flamf_timealign_adapted",
        "local_hajek",
        "twostage_hajek",
        "inst_cal",
        "debt_cal",
        "raven",
        "raven_simoracle",
        "central_all",
        "central_delivered",
    ]
    focus = [
        "Delta_c_s",
        "Delta_pair",
        "delta_ref",
        "Q_norm1_over_S",
        "Q_norm2_over_S",
        "RMSE_rho",
        "Delta_group",
    ]
    rows = []
    for m in methods:
        for metric in focus:
            rows.append({"method": m, "metric": metric, "applicability": applicability_for(m, metric)})
    return {
        "schema_version": "E3_MECHANISM_METRIC_APPLICABILITY_R2",
        "na_emission": "null + applicability code; never numeric 0 for NOT_APPLICABLE",
        "paper_table_render": "N/A",
        "atomic_Delta_pair": "NOT_MATERIALIZED (client×group representation is Delta_c_s)",
        "rows": rows,
    }


def metric_applicability_matrix() -> dict[str, Any]:
    """Full method×metric matrix for schema V5."""
    methods = sorted(
        CENTRAL_METHODS
        | {
            "fedavg_window",
            "fedasync_window",
            "flamf_timealign_adapted",
            "local_hajek",
            "twostage_hajek",
            "inst_cal",
            "debt_cal",
            "raven",
            "raven_simoracle",
        }
    )
    rows = []
    for m in methods:
        for metric in ALL_METRICS:
            rows.append({"method": m, "metric": metric, "applicability": applicability_for(m, metric)})
    return {
        "schema_version": "E3_METRIC_APPLICABILITY_MATRIX_V5",
        "na_emission": "null + applicability code; never numeric 0 for NOT_APPLICABLE/NOT_MATERIALIZED",
        "paper_table_render": "N/A",
        "rows": rows,
    }


def emit_metric_value(method: str, metric: str, value: Any) -> dict[str, Any]:
    code = applicability_for(method, metric)
    if code in {NOT_APPLICABLE, NOT_MATERIALIZED}:
        if value is not None and not (isinstance(value, float) and np.isnan(value)):
            if value == 0 or value == 0.0:
                raise MechanismMetricApplicabilityError(
                    f"MECHANISM_METRIC_APPLICABILITY_ERROR: {method}.{metric} emitted fake zero"
                )
        return {"value": None, "applicability": code}
    if code == UNAVAILABLE:
        return {"value": None, "applicability": code, "reason": "unavailable"}
    return {"value": value, "applicability": code}


def finalize_metrics_dict(method: str, metrics: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for metric, value in metrics.items():
        if metric.endswith("_applicability"):
            continue
        packed = emit_metric_value(method, metric, value)
        out[metric] = packed["value"]
        out[f"{metric}_applicability"] = packed["applicability"]
    return out


def metric_schema_v6() -> dict[str, Any]:
    return {
        "schema_version": METRIC_SCHEMA_VERSION,
        "required_fields": ALL_METRICS,
        "structural_metric": "Delta_c_s",
        "Delta_pair_policy": "NOT_MATERIALIZED — atomic client×unit Delta_pair not available",
        "na_policy": "null + *_applicability; paper renders N/A",
        "finite_value_policy": "applicable metrics must be finite floats",
        "no_placeholder_substitution": True,
        "support_separation": {
            "Delta_group": "target_group h(i)",
            "Head_Tail": "target_group h(i)",
            "Delta_c_s": "client × opportunity_stratum s(i)",
            "RMSE_rho": "atomic rho_i^arr",
            "RMSE_mu": "target mu on h(i)",
        },
        "per_metric": {
            "RMSE_mu": {"weighting": "mu target on h", "formula_version": "v6"},
            "RMSE_rho": {
                "weighting": "atomic rho_i^arr = normalize(sum_k pi_opp*nu*p_obs*q)",
                "formula_version": "v6",
                "forbidden": "group-marginal rho_g/n_g",
            },
            "Delta_c_s": {
                "support": "client × opportunity_stratum",
                "formula": "sum_{k,s} |Pi_hat_ks - pi_tar_ks|",
                "formula_version": "v6",
                "forbidden": "client × target_group h",
            },
            "Delta_group": {"support": "target_group h(i)", "formula_version": "v6"},
            "Delta_pair": {"status": "NOT_MATERIALIZED"},
            "Q_norm1_over_S": {"applicable_only_if": "uses_debt"},
            "delta_ref": {"applicable_only_if": "uses_reference_penalty"},
        },
    }


def metric_schema_v5() -> dict[str, Any]:
    """Compatibility shim — prefer V6."""
    return metric_schema_v6()


def metric_schema_v4() -> dict[str, Any]:
    """Compatibility shim — prefer V6."""
    return metric_schema_v6()


# Re-export for older imports that catch CentralMetricApplicabilityError
CentralMetricApplicabilityError = MechanismMetricApplicabilityError  # type: ignore[misc,assignment]
