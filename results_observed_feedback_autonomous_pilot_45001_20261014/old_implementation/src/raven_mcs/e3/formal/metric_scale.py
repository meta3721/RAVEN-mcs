"""Metric-domain policy and lossless standardized-to-physical conversions."""
from __future__ import annotations
from typing import Any

def policy(dataset: str, *, reused: bool = False, sigma: float | None = None) -> dict[str, Any]:
    raw = dataset == "sensorscope"
    return {"dataset": dataset, "zscore_applied": not raw, "primary_domain": "physical",
            "conversion": "IDENTITY_RAW_PHYSICAL" if raw else "OFFLINE_LINEAR_CONVERSION",
            "status": "RAW_PHYSICAL" if raw else "OFFLINE_LINEAR_CONVERSION",
            "sigma": sigma, "RMSE_rho_status": "NOT_COMPARABLE_FROM_SEALED_OUTPUTS" if reused else "APPLICABLE",
            "store_fields": ["RMSE_mu_std", "RMSE_mu_phys", "MAE_mu_std", "MAE_mu_phys"]}

def convert_metrics(metrics: dict[str, Any], scale: dict[str, Any]) -> dict[str, Any]:
    out = dict(metrics)
    sigma = scale.get("sigma")
    for metric in ("RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho"):
        value = metrics.get(metric)
        if value is None:
            continue
        out[f"{metric}_std"] = value
        if scale["status"] == "RAW_PHYSICAL":
            out[f"{metric}_phys"] = value
        else:
            if sigma is None:
                raise ValueError(f"sigma required for physical conversion of {metric}")
            out[f"{metric}_phys"] = float(value) * float(sigma)
    if scale.get("RMSE_rho_status") != "APPLICABLE":
        out["RMSE_rho_status"] = scale["RMSE_rho_status"]
        out["RMSE_rho_phys"] = None
    return out
