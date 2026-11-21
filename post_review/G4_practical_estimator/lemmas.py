"""Elementary constants and inequalities used by the G4 practical-estimator bound.

These are proof objects, not a new estimator. Implementation caps match
`raven_mcs.correction.hajek.raw_weights` and `second_stage.d_weight`.
"""

from __future__ import annotations

from typing import Any

import numpy as np

A_MAX = 20.0
P_MIN = 0.05
D_MAX = 10.0
Q_MIN = 0.05


def clip_residual(raw: np.ndarray, cap: float) -> np.ndarray:
    """(x - cap)_+ ; |min(cap, x) - x|."""
    x = np.asarray(raw, dtype=np.float64)
    return np.maximum(x - float(cap), 0.0)


def hajek_l1_gap(b: np.ndarray, b_star: np.ndarray) -> tuple[float, float, float]:
    """Return (||β-β*||_1, 2||b-b*||_1 / min(B,B*), min(B,B*))."""
    b = np.asarray(b, dtype=np.float64)
    b_star = np.asarray(b_star, dtype=np.float64)
    if np.any(b < 0) or np.any(b_star < 0):
        raise ValueError("masses must be nonnegative")
    total = float(b.sum())
    total_star = float(b_star.sum())
    if total <= 0.0 or total_star <= 0.0:
        raise ValueError("Hájek denominators must be positive")
    beta = b / total
    beta_star = b_star / total_star
    gap = float(np.abs(beta - beta_star).sum())
    denom = min(total, total_star)
    bound = 2.0 * float(np.abs(b - b_star).sum()) / denom
    return gap, bound, denom


def structured_c1(
    *,
    k_r: int,
    n_r: int,
    b_min: float,
    pi_min: float,
    p_min: float = P_MIN,
    p_min_true: float = P_MIN,
    q_min: float = Q_MIN,
    q_min_true: float = Q_MIN,
    a_max: float = A_MAX,
    d_max: float = D_MAX,
) -> dict[str, float]:
    """C1 and the four Lipschitz pieces. Infinite if any margin is 0."""
    margins = (pi_min, p_min, p_min_true, q_min, q_min_true, b_min)
    if any(m <= 0 for m in margins) or k_r < 1 or n_r < 1:
        return {
            "C1": float("inf"),
            "C_pi": float("inf"),
            "C_p": float("inf"),
            "C_q": float("inf"),
            "C_clip": float("inf"),
            "defined": 0.0,
        }
    scale = 2.0 * float(k_r) * float(n_r) / float(b_min)
    c_pi = scale * (d_max / (pi_min**2 * p_min))
    c_p = scale * (d_max / (pi_min * p_min * p_min_true))
    c_q = scale * (a_max / (q_min * q_min_true))
    c_clip = scale * (a_max + d_max)
    return {
        "C1": float(max(c_pi, c_p, c_q, c_clip)),
        "C_pi": float(c_pi),
        "C_p": float(c_p),
        "C_q": float(c_q),
        "C_clip": float(c_clip),
        "defined": 1.0,
        "scale": float(scale),
    }


def a5_holds(frac_pi_tar_zero: float, *, tol: float = 1e-12) -> bool:
    return float(frac_pi_tar_zero) <= tol


def instantiate_from_g1_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map one G1 three-layer row to A5 / C1 status. Not a tightness claim.

    ``C1_times_Bmin`` is \(C_1 B_{\min}\) at \(K_r=n_r=1\): the Lipschitz
    piece. ESS is recorded only as a qualitative denominator diagnostic.
    """
    frac_zero = float(row["frac_pi_tar_zero"])
    pi_opp_min = float(row["pi_opp_min"])
    p_true_min = float(row["p_true_min"])
    zeta_max = float(row["zeta_max"])
    pi_min_from_zeta = (1.0 / zeta_max) if zeta_max > 0 else 0.0
    unit_global = structured_c1(
        k_r=1,
        n_r=1,
        b_min=1.0,
        pi_min=pi_opp_min,
        p_min_true=p_true_min,
    )
    unit_zeta = structured_c1(
        k_r=1,
        n_r=1,
        b_min=1.0,
        pi_min=pi_min_from_zeta,
        p_min_true=p_true_min,
    )
    if not a5_holds(frac_zero):
        for block in (unit_global, unit_zeta):
            block["C1"] = float("inf")
            block["defined"] = 0.0
    return {
        "dataset": row.get("dataset"),
        "a5_holds": a5_holds(frac_zero),
        "frac_pi_tar_zero": frac_zero,
        "pi_opp_min_global": pi_opp_min,
        "pi_min_from_zeta_max": pi_min_from_zeta,
        "p_true_min": p_true_min,
        "clip_on_mean": float(row["clip_on_mean"]),
        "ess_ratio_on_mean": float(row["ess_ratio_on_mean"]),
        "mean_abs_a_on_minus_oracle": float(row["mean_abs_a_on_minus_oracle"]),
        "C1_times_Bmin_global_pi_min": unit_global,
        "C1_times_Bmin_zeta_floor": unit_zeta,
    }
