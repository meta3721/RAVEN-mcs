"""Post-window Full-Design vs No-Design audit on a recorded R/O/U window.

Deltas are defined only when A^D = A^0 ≠ ∅.
Both-empty: service_diff = 0 and Delta_beta/M/V = NA (not 0).

R1-A: Δβ = ||β^D−β^0||_2, ΔM = ||M^D−M^0||_2 (operator),
ΔV = ||V^D−V^0||_2 with v_k = S²_{r-}/max(n_eff,1)+v_floor,
service_diff_l1 = ||M^D α^D − M^0 α^0||_1. These four are independent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from raven_mcs.aggregation.p2_cvxpy import solve_p2
from raven_mcs.correction.effective_sample_size import effective_sample_size
from raven_mcs.correction.hajek import (
    composition,
    group_mass,
    raw_weights,
    total_mass,
)
from raven_mcs.correction.second_stage import beta_hat, d_weight, two_stage_mass
from raven_mcs.sag.gate import zeta_tilde


NA = None


def l2_vector(a: np.ndarray, b: np.ndarray) -> float:
    x = np.asarray(a, dtype=np.float64).ravel()
    y = np.asarray(b, dtype=np.float64).ravel()
    if x.shape != y.shape:
        raise ValueError(f"vector shapes differ: {x.shape} vs {y.shape}")
    return float(np.linalg.norm(x - y, ord=2))


def operator_2norm(a: np.ndarray, b: np.ndarray | None = None) -> float:
    mat = np.asarray(a, dtype=np.float64)
    if b is not None:
        mat = mat - np.asarray(b, dtype=np.float64)
    if mat.ndim == 1:
        mat = np.diag(mat)
    return float(np.linalg.norm(mat, ord=2))


def reconstruct_variance_diag(
    n_eff: np.ndarray,
    lagged_s2: np.ndarray,
    *,
    v_floor: float,
) -> np.ndarray:
    n = np.asarray(n_eff, dtype=np.float64).ravel()
    s2 = np.asarray(lagged_s2, dtype=np.float64).ravel()
    if n.shape != s2.shape:
        raise ValueError("n_eff and lagged_s2 must share shape")
    v = s2 / np.maximum(n, 1.0) + float(v_floor)
    v = np.where(np.isfinite(v), v, 1.0 + float(v_floor))
    return np.maximum(v, float(v_floor))


def metrics_from_raw_states(
    *,
    beta_d: np.ndarray,
    beta_0: np.ndarray,
    m_d: np.ndarray,
    m_0: np.ndarray,
    v_d: np.ndarray,
    v_0: np.ndarray,
    alpha_d: np.ndarray,
    alpha_0: np.ndarray,
) -> dict[str, float]:
    """Independent Δβ / ΔM / ΔV / service from explicit states (R1-A)."""
    s_d = np.asarray(m_d, dtype=np.float64) @ np.asarray(alpha_d, dtype=np.float64)
    s_0 = np.asarray(m_0, dtype=np.float64) @ np.asarray(alpha_0, dtype=np.float64)
    return {
        "Delta_beta": l2_vector(beta_d, beta_0),
        "Delta_M": operator_2norm(m_d, m_0),
        "Delta_V": operator_2norm(v_d, v_0),
        "service_diff_l1": float(np.linalg.norm(s_d - s_0, ord=1)),
        "service_diff_l2": float(np.linalg.norm(s_d - s_0, ord=2)),
        "B_M_cf": max(operator_2norm(m_d), operator_2norm(m_0)),
    }


def _solve_alpha(
    m: np.ndarray,
    beta: np.ndarray,
    v_diag: np.ndarray,
    *,
    mu: np.ndarray,
    debt: np.ndarray,
    staleness: np.ndarray,
    lambda_group: float,
    lambda_beta: float,
    lambda_variance: float,
    lambda_staleness: float,
    alpha_max: float,
    e_min: float,
    max_server_learning_rate: float,
) -> np.ndarray:
    n = int(beta.size)
    result = solve_p2(
        m,
        mu,
        beta,
        debt,
        v_diag,
        staleness,
        lambda_group=lambda_group,
        lambda_beta=lambda_beta,
        lambda_variance=lambda_variance,
        lambda_staleness=lambda_staleness,
        alpha_max=alpha_max,
        e_min=min(float(e_min), float(n)),
        max_server_learning_rate=max_server_learning_rate,
    )
    alpha = np.asarray(result.alpha, dtype=np.float64).ravel()
    total = float(alpha.sum())
    if total <= 0:
        return np.ones(n, dtype=np.float64) / float(n)
    return alpha / total


@dataclass
class CounterfactualAudit:
    A_D: tuple[str, ...]
    A_0: tuple[str, ...]
    B_D: tuple[str, ...]
    B_0: tuple[str, ...]
    A_D_size: int
    A_0_size: int
    active_set_mismatch: int
    both_empty: int
    service_diff: float | None
    service_diff_l1: float | None
    service_diff_l2: float | None
    Delta_beta: float | None
    Delta_M: float | None
    Delta_V: float | None
    realized_C_cov: float
    realized_C_ret: float
    realized_C_ESS: float
    realized_C_clip: float
    raw_state: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "A_D_size": self.A_D_size,
            "A_0_size": self.A_0_size,
            "active_set_mismatch": int(self.active_set_mismatch),
            "both_empty": int(self.both_empty),
            "service_diff": self.service_diff,
            "service_diff_l1": self.service_diff_l1,
            "service_diff_l2": self.service_diff_l2,
            "Delta_beta": self.Delta_beta,
            "Delta_M": self.Delta_M,
            "Delta_V": self.Delta_V,
            "A_common_size": (
                self.A_D_size
                if (not self.active_set_mismatch and not self.both_empty)
                else (0 if self.both_empty else float("nan"))
            ),
            "realized_C_cov": self.realized_C_cov,
            "realized_C_ret": self.realized_C_ret,
            "realized_C_ESS": self.realized_C_ESS,
            "realized_C_clip": self.realized_C_clip,
            "B_M_cf": self.raw_state.get("B_M_cf"),
            "ess_clients": list(self.raw_state.get("ess_clients") or []),
            "raw_state": dict(self.raw_state),
        }


def _masses(
    *,
    O: np.ndarray,
    groups: np.ndarray,
    zeta: np.ndarray,
    p_hat: np.ndarray,
    a_max: float,
    p_min: float,
    num_groups: int,
) -> tuple[float, np.ndarray, float, float]:
    a_raw = raw_weights(zeta, p_hat, a_max=a_max, p_min=p_min)
    m_g = group_mass(O, a_raw, groups, n_groups=num_groups)
    m_total = float(total_mass(m_g))
    c_g = composition(m_g, m_total)
    n_eff = float(effective_sample_size(O, a_raw, total_mass=m_total))
    clip = float(np.mean(np.abs(a_raw) >= a_max)) if a_raw.size else 0.0
    return m_total, c_g, n_eff, clip


def _stage2_matrix(
    clients: list[str],
    masses: dict[str, float],
    compositions: dict[str, np.ndarray],
    q_hat: dict[str, float],
    *,
    d_max: float,
    q_min: float,
    num_groups: int,
) -> tuple[np.ndarray, np.ndarray]:
    n = len(clients)
    m_mat = np.zeros((num_groups, n), dtype=np.float64)
    if n == 0:
        return np.zeros(0, dtype=np.float64), m_mat
    mass = np.array([masses[c] for c in clients], dtype=np.float64)
    q = np.array([q_hat.get(c, 0.5) for c in clients], dtype=np.float64)
    d = d_weight(q, d_max=d_max, q_min=q_min)
    b = two_stage_mass(mass, d)
    beta = beta_hat(b)
    for i, cid in enumerate(clients):
        m_mat[:, i] = np.asarray(compositions[cid], dtype=np.float64)
    return beta, m_mat


def audit_design_vs_nodesign(
    *,
    registered: list[str],
    attempted: list[str],
    usable: dict[str, int],
    O: dict[str, np.ndarray],
    groups: dict[str, np.ndarray],
    zeta_d: dict[str, np.ndarray],
    p_hat: dict[str, np.ndarray],
    q_hat: dict[str, float],
    variance: dict[str, float],
    target_positive_count: int,
    target_covered_count: int,
    a_max: float,
    p_min: float,
    d_max: float,
    q_min: float,
    num_groups: int,
    v_floor: float = 1e-4,
    mu: np.ndarray | None = None,
    debt: np.ndarray | None = None,
    staleness: dict[str, float] | None = None,
    lambda_group: float = 1.0,
    lambda_beta: float = 1.0,
    lambda_variance: float = 0.1,
    lambda_staleness: float = 0.1,
    alpha_max: float = 0.5,
    e_min: float = 3.0,
    max_server_learning_rate: float = 1.0,
    n_eff_override: dict[str, tuple[float, float]] | None = None,
) -> CounterfactualAudit:
    """Reconstruct B/A and (when defined) independent Δβ/M/V and service."""
    b_d: list[str] = []
    b_0: list[str] = []
    masses_d: dict[str, float] = {}
    masses_0: dict[str, float] = {}
    comp_d: dict[str, np.ndarray] = {}
    comp_0: dict[str, np.ndarray] = {}
    n_eff_d: dict[str, float] = {}
    n_eff_0: dict[str, float] = {}
    n_effs: list[float] = []
    clips: list[float] = []
    ess_rows: list[dict[str, Any]] = []

    for cid in registered:
        if cid not in attempted:
            continue
        rec_o = np.asarray(O[cid], dtype=np.float64)
        rec_g = np.asarray(groups[cid], dtype=np.int64)
        zd = np.asarray(zeta_d[cid], dtype=np.float64)
        ph = np.asarray(p_hat[cid], dtype=np.float64)
        z0 = zeta_tilde(zd, 0)
        m_d, c_d, n_d, clip_d = _masses(
            O=rec_o, groups=rec_g, zeta=zd, p_hat=ph,
            a_max=a_max, p_min=p_min, num_groups=num_groups,
        )
        m_0, c_0, n_0, clip_0 = _masses(
            O=rec_o, groups=rec_g, zeta=z0, p_hat=ph,
            a_max=a_max, p_min=p_min, num_groups=num_groups,
        )
        if n_eff_override and cid in n_eff_override:
            n_d, n_0 = n_eff_override[cid]
        masses_d[cid] = m_d
        masses_0[cid] = m_0
        comp_d[cid] = c_d
        comp_0[cid] = c_0
        n_eff_d[cid] = float(n_d)
        n_eff_0[cid] = float(n_0)
        obs = rec_o > 0
        if int(obs.sum()) > 0:
            z_obs = zd[obs]
            z_std = float(np.std(z_obs)) if z_obs.size > 1 else 0.0
            z_min = float(np.min(z_obs))
            z_max = float(np.max(z_obs))
        else:
            z_std = float("nan")
            z_min = float("nan")
            z_max = float("nan")
        ess_rows.append({
            "client": str(cid),
            "n_obs": int(obs.sum()),
            "zeta_std": z_std,
            "zeta_min": z_min,
            "zeta_max": z_max,
            "n_eff_D": float(n_d),
            "n_eff_0": float(n_0),
            "abs_neff_diff": abs(float(n_d) - float(n_0)),
        })
        obs = rec_o > 0
        if int(obs.sum()) > 0:
            z_obs = zd[obs]
            z_std = float(np.std(z_obs)) if z_obs.size > 1 else 0.0
            z_min = float(np.min(z_obs))
            z_max = float(np.max(z_obs))
        else:
            z_std = float("nan")
            z_min = float("nan")
            z_max = float("nan")
        ess_rows.append({
            "client": str(cid),
            "n_obs": int(obs.sum()),
            "zeta_std": z_std,
            "zeta_min": z_min,
            "zeta_max": z_max,
            "n_eff_D": float(n_d),
            "n_eff_0": float(n_0),
            "abs_neff_diff": abs(float(n_d) - float(n_0)),
        })
        n_effs.extend([float(n_d), float(n_0)])
        clips.extend([clip_d, clip_0])
        if m_d > 0:
            b_d.append(cid)
        if m_0 > 0:
            b_0.append(cid)

    u_set = {cid for cid, u in usable.items() if int(u) == 1}
    a_d = tuple(sorted(cid for cid in b_d if cid in u_set))
    a_0 = tuple(sorted(cid for cid in b_0 if cid in u_set))
    mismatch = int(a_d != a_0)
    both_empty = int(len(a_d) == 0 and len(a_0) == 0)

    delta_beta: float | None = NA
    delta_m: float | None = NA
    delta_v: float | None = NA
    service_diff: float | None
    service_l1: float | None = NA
    service_l2: float | None = NA
    raw_state: dict[str, Any] = {}
    if both_empty:
        service_diff = 0.0
        service_l1 = 0.0
        service_l2 = 0.0
    elif mismatch:
        service_diff = NA
    else:
        clients = list(a_d)
        beta_d, mat_d = _stage2_matrix(
            clients, masses_d, comp_d, q_hat,
            d_max=d_max, q_min=q_min, num_groups=num_groups,
        )
        beta_0, mat_0 = _stage2_matrix(
            clients, masses_0, comp_0, q_hat,
            d_max=d_max, q_min=q_min, num_groups=num_groups,
        )
        s2 = np.array([float(variance.get(c, 1.0)) for c in clients], dtype=np.float64)
        v_d = reconstruct_variance_diag(
            np.array([n_eff_d[c] for c in clients], dtype=np.float64),
            s2,
            v_floor=v_floor,
        )
        v_0 = reconstruct_variance_diag(
            np.array([n_eff_0[c] for c in clients], dtype=np.float64),
            s2,
            v_floor=v_floor,
        )
        tau = np.array(
            [(staleness or {}).get(c, 0.0) for c in clients],
            dtype=np.float64,
        )
        if mu is None:
            mu_vec = np.full(num_groups, 1.0 / float(num_groups), dtype=np.float64)
        else:
            mu_vec = np.asarray(mu, dtype=np.float64).ravel()
        if debt is None:
            q_vec = np.zeros(num_groups, dtype=np.float64)
        else:
            q_vec = np.asarray(debt, dtype=np.float64).ravel()
        alpha_d = _solve_alpha(
            mat_d, beta_d, v_d,
            mu=mu_vec, debt=q_vec, staleness=tau,
            lambda_group=lambda_group, lambda_beta=lambda_beta,
            lambda_variance=lambda_variance, lambda_staleness=lambda_staleness,
            alpha_max=alpha_max, e_min=e_min,
            max_server_learning_rate=max_server_learning_rate,
        )
        alpha_0 = _solve_alpha(
            mat_0, beta_0, v_0,
            mu=mu_vec, debt=q_vec, staleness=tau,
            lambda_group=lambda_group, lambda_beta=lambda_beta,
            lambda_variance=lambda_variance, lambda_staleness=lambda_staleness,
            alpha_max=alpha_max, e_min=e_min,
            max_server_learning_rate=max_server_learning_rate,
        )
        mets = metrics_from_raw_states(
            beta_d=beta_d, beta_0=beta_0,
            m_d=mat_d, m_0=mat_0,
            v_d=np.diag(v_d), v_0=np.diag(v_0),
            alpha_d=alpha_d, alpha_0=alpha_0,
        )
        delta_beta = mets["Delta_beta"]
        delta_m = mets["Delta_M"]
        delta_v = mets["Delta_V"]
        service_l1 = mets["service_diff_l1"]
        service_l2 = mets["service_diff_l2"]
        service_diff = service_l1
        raw_state = {
            "clients": list(clients),
            "beta_D": beta_d.tolist(),
            "beta_0": beta_0.tolist(),
            "M_D": mat_d.tolist(),
            "M_0": mat_0.tolist(),
            "V_D_diag": v_d.tolist(),
            "V_0_diag": v_0.tolist(),
            "n_eff_D": [n_eff_d[c] for c in clients],
            "n_eff_0": [n_eff_0[c] for c in clients],
            "alpha_D": alpha_d.tolist(),
            "alpha_0": alpha_0.tolist(),
            "s_D": (mat_d @ alpha_d).tolist(),
            "s_0": (mat_0 @ alpha_0).tolist(),
            "B_M_cf": mets["B_M_cf"],
            "Delta_beta": delta_beta,
            "Delta_M": delta_m,
            "Delta_V": delta_v,
            "service_diff_l1": service_l1,
            "service_diff_l2": service_l2,
            "ess_clients": ess_rows,
        }
        vmap_d = {c: float(v_d[i]) for i, c in enumerate(clients)}
        vmap_0 = {c: float(v_0[i]) for i, c in enumerate(clients)}
        for row in ess_rows:
            cid = str(row["client"])
            row["v_D"] = vmap_d.get(cid, float("nan"))
            row["v_0"] = vmap_0.get(cid, float("nan"))
            row["abs_v_diff"] = abs(float(row["v_D"]) - float(row["v_0"])) if cid in vmap_d else float("nan")
    if "ess_clients" not in raw_state:
        raw_state["ess_clients"] = ess_rows

    denom = max(int(target_positive_count), 1)
    realized_cov = float(target_covered_count) / float(denom)
    b_union = set(b_d) | set(b_0)
    if b_union:
        realized_ret = float(len(set(a_d) | set(a_0))) / float(len(b_union))
    else:
        realized_ret = 0.0
    realized_ess = float(np.mean(n_effs)) if n_effs else 0.0
    realized_clip = float(np.mean(clips)) if clips else 0.0

    return CounterfactualAudit(
        A_D=a_d,
        A_0=a_0,
        B_D=tuple(sorted(b_d)),
        B_0=tuple(sorted(b_0)),
        A_D_size=len(a_d),
        A_0_size=len(a_0),
        active_set_mismatch=mismatch,
        both_empty=both_empty,
        service_diff=service_diff,
        service_diff_l1=service_l1,
        service_diff_l2=service_l2,
        Delta_beta=delta_beta,
        Delta_M=delta_m,
        Delta_V=delta_v,
        realized_C_cov=realized_cov,
        realized_C_ret=realized_ret,
        realized_C_ESS=realized_ess,
        realized_C_clip=realized_clip,
        raw_state=raw_state,
    )
