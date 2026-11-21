"""Oracle coverage ceiling diagnostics for SAG G1-R1f.

C_real_support and C_oracle_safe are diagnostic upper bounds derived from
frozen target mass and realized opportunity. They are not certificates.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

NUM_TOL = 1e-12
ORACLE_PASS_ROUTING_FRACTION = 0.20


def ge_threshold(value: float, threshold: float, *, tol: float = NUM_TOL) -> bool:
    return float(value) + tol >= float(threshold)


def c_real_support_from_pairs(
    pi_tar: Sequence[float],
    pi_opp_realized: Sequence[float],
) -> tuple[float, int, int, float]:
    """Loose realized-support ceiling: target mass with any realized opportunity."""
    tar = np.asarray(pi_tar, dtype=np.float64)
    realized = np.asarray(pi_opp_realized, dtype=np.float64)
    tot = float(tar.sum())
    if tot <= NUM_TOL:
        return float("nan"), 0, 0, tot
    pos = tar > NUM_TOL
    n_pos = int(pos.sum())
    real_pos = realized > NUM_TOL
    n_real = int((pos & real_pos).sum())
    c_real = float(tar[real_pos].sum() / tot)
    return c_real, n_real, n_pos, tot


def c_oracle_safe_from_pairs(
    pi_tar: Sequence[float],
    pi_opp_realized: Sequence[float],
    pi_safe: float,
) -> tuple[float, int]:
    """Oracle safe ceiling: target mass with realized opportunity >= pi_safe."""
    tar = np.asarray(pi_tar, dtype=np.float64)
    realized = np.asarray(pi_opp_realized, dtype=np.float64)
    tot = float(tar.sum())
    if tot <= NUM_TOL:
        return float("nan"), 0
    pos = tar > NUM_TOL
    safe = realized >= float(pi_safe) - NUM_TOL
    n_safe = int((pos & safe).sum())
    c_oracle = float(tar[safe].sum() / tot)
    return c_oracle, n_safe


def classify_threshold_compatibility(
    *,
    fraction_oracle_pass: float,
    max_c_oracle_safe: float,
    n_oracle_pass: int,
    tau_cov: float,
) -> str:
    """Protocol-threshold compatibility routing label (internal experiment only)."""
    if not np.isfinite(max_c_oracle_safe) or max_c_oracle_safe + NUM_TOL < tau_cov:
        return "E3_THRESHOLD_INCOMPATIBLE"
    if int(n_oracle_pass) == 0:
        return "E3_THRESHOLD_INCOMPATIBLE"
    if fraction_oracle_pass >= ORACLE_PASS_ROUTING_FRACTION and n_oracle_pass >= 2:
        return "E3_THRESHOLD_COMPATIBLE"
    if fraction_oracle_pass > 0:
        return "E3_THRESHOLD_MARGINAL"
    return "E3_THRESHOLD_INCOMPATIBLE"


def derive_final_verdict(
    compat_by_dataset: Mapping[str, str],
    evidence_ok: bool,
) -> str:
    if not evidence_ok:
        return "R1F_EVIDENCE_FAILURE"
    labels = set(compat_by_dataset.values())
    if "E3_THRESHOLD_COMPATIBLE" in labels and labels == {"E3_THRESHOLD_COMPATIBLE"}:
        return "READY_FOR_CERTIFICATE_REPAIR"
    if "E3_THRESHOLD_INCOMPATIBLE" in labels:
        return "E3_THRESHOLD_INCOMPATIBLE"
    if labels == {"E3_THRESHOLD_MARGINAL"} or "E3_THRESHOLD_MARGINAL" in labels:
        return "E3_THRESHOLD_MARGINAL"
    return "R1F_EVIDENCE_FAILURE"


def gap_decomposition_row(
    *,
    dataset: str,
    window_id: int,
    tau_cov: float,
    c_real_support: float,
    c_oracle_safe: float,
    c_cov_r1d: float,
) -> dict[str, Any]:
    gap_support = tau_cov - c_real_support
    gap_pi_safe = c_real_support - c_oracle_safe
    gap_certificate = c_oracle_safe - c_cov_r1d
    return {
        "dataset": dataset,
        "window_id": int(window_id),
        "tau_cov": float(tau_cov),
        "C_real_support": float(c_real_support),
        "C_oracle_safe": float(c_oracle_safe),
        "C_cov_r1d": float(c_cov_r1d),
        "gap_support": float(gap_support),
        "gap_pi_safe": float(gap_pi_safe),
        "gap_certificate": float(gap_certificate),
        "decomposition_sum": float(gap_support + gap_pi_safe + gap_certificate),
        "tau_minus_formal": float(tau_cov - c_cov_r1d),
    }


def compute_oracle_windows_from_prediction(
    pred: pd.DataFrame,
    *,
    dataset: str,
    seed: int,
    pi_safe: float,
    tau_cov: float,
    c_cov_r1d_by_window: Mapping[int, float],
    trace_hash: str,
    target_law_hash: str,
    pi_safe_rule_hash: str,
) -> pd.DataFrame:
    """Per warm-up window oracle ceiling from frozen R1d prediction rows."""
    sub = pred.loc[pred["dataset"].astype(str) == dataset].copy()
    rows: list[dict[str, Any]] = []
    for window_id, chunk in sub.groupby("window_id", sort=True):
        cold = int(chunk["cold_start"].iloc[0]) == 1
        pos = chunk.loc[pd.to_numeric(chunk["pi_tar"], errors="coerce") > NUM_TOL].copy()
        tar = pos["pi_tar"].astype(float)
        realized = pd.to_numeric(pos["pi_opp_realized"], errors="coerce").fillna(0.0)
        c_real, n_real, n_pos, tot = c_real_support_from_pairs(tar.tolist(), realized.tolist())
        c_oracle, n_safe = c_oracle_safe_from_pairs(tar.tolist(), realized.tolist(), pi_safe)
        c_formal = float(c_cov_r1d_by_window.get(int(window_id), float("nan")))
        if cold:
            c_formal = float("nan")
        rows.append(
            {
                "dataset": dataset,
                "seed": int(seed),
                "window_id": int(window_id),
                "is_warmup_eligible": not cold,
                "n_target_positive_pairs": int(n_pos),
                "pi_safe": float(pi_safe),
                "tau_cov": float(tau_cov),
                "C_real_support": c_real,
                "C_oracle_safe": c_oracle,
                "C_cov_r1d": c_formal,
                "oracle_safe_minus_tau": float(c_oracle - tau_cov) if np.isfinite(c_oracle) else float("nan"),
                "real_support_minus_tau": float(c_real - tau_cov) if np.isfinite(c_real) else float("nan"),
                "formal_minus_tau": float(c_formal - tau_cov) if np.isfinite(c_formal) else float("nan"),
                "oracle_pass": ge_threshold(c_oracle, tau_cov) if not cold else False,
                "real_support_pass": ge_threshold(c_real, tau_cov) if not cold else False,
                "formal_pass": ge_threshold(c_formal, tau_cov) if not cold and np.isfinite(c_formal) else False,
                "n_real_positive_pairs": int(n_real),
                "n_real_pi_safe_pairs": int(n_safe),
                "target_mass_total": float(tot),
                "trace_hash": trace_hash,
                "target_law_hash": target_law_hash,
                "pi_safe_rule_hash": pi_safe_rule_hash,
            }
        )
    return pd.DataFrame(rows)


def summarize_oracle_windows(frame: pd.DataFrame, *, dataset: str, tau_cov: float) -> dict[str, Any]:
    warm = frame.loc[frame["is_warmup_eligible"] == True]  # noqa: E712
    if warm.empty:
        return {"dataset": dataset, "n_warmup_windows": 0}
    c_real = warm["C_real_support"].astype(float)
    c_oracle = warm["C_oracle_safe"].astype(float)
    c_formal = warm["C_cov_r1d"].astype(float)
    n_real_pass = int(warm["real_support_pass"].sum())
    n_oracle_pass = int(warm["oracle_pass"].sum())
    n_formal_pass = int(warm["formal_pass"].sum())
    n_warm = int(len(warm))
    oracle_gap = c_oracle - float(tau_cov)
    return {
        "dataset": dataset,
        "n_warmup_windows": n_warm,
        "mean_C_real_support": float(c_real.mean()),
        "median_C_real_support": float(c_real.median()),
        "p10_C_real_support": float(c_real.quantile(0.10)),
        "p90_C_real_support": float(c_real.quantile(0.90)),
        "max_C_real_support": float(c_real.max()),
        "mean_C_oracle_safe": float(c_oracle.mean()),
        "median_C_oracle_safe": float(c_oracle.median()),
        "p10_C_oracle_safe": float(c_oracle.quantile(0.10)),
        "p90_C_oracle_safe": float(c_oracle.quantile(0.90)),
        "max_C_oracle_safe": float(c_oracle.max()),
        "mean_C_cov_r1d": float(c_formal.mean()),
        "median_C_cov_r1d": float(c_formal.median()),
        "max_C_cov_r1d": float(c_formal.max()),
        "n_real_support_pass": n_real_pass,
        "fraction_real_support_pass": float(n_real_pass / n_warm),
        "n_oracle_pass": n_oracle_pass,
        "fraction_oracle_pass": float(n_oracle_pass / n_warm),
        "n_formal_pass": n_formal_pass,
        "fraction_formal_pass": float(n_formal_pass / n_warm),
        "oracle_gap_mean": float(oracle_gap.mean()),
        "oracle_gap_median": float(oracle_gap.median()),
        "oracle_gap_max": float(oracle_gap.max()),
        "P_oracle_pass": float(n_oracle_pass / n_warm),
        "compatibility": classify_threshold_compatibility(
            fraction_oracle_pass=float(n_oracle_pass / n_warm),
            max_c_oracle_safe=float(c_oracle.max()),
            n_oracle_pass=n_oracle_pass,
            tau_cov=float(tau_cov),
        ),
    }
