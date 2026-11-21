"""Hard empirical and expected mass aggregation at atomic/group/stratum levels."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _tv(a: np.ndarray, b: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(a - b)))


def hard_empirical_atomic_mass(
    arrival: pd.DataFrame,
    unit_ids: list[str],
    max_window: int,
) -> np.ndarray:
    index = {u: i for i, u in enumerate(unit_ids)}
    mass = np.zeros(len(unit_ids), dtype=np.float64)
    sub = arrival.loc[
        (arrival["window_id"].astype(int) < int(max_window)) & (arrival["W_arr"] > 0)
    ]
    if sub.empty:
        raise RuntimeError(f"zero hard arrival mass for prefix L={max_window}")
    grouped = sub.groupby(sub["unit_id"].astype(str), sort=False)["W_arr"].sum()
    for unit_id, value in grouped.items():
        mass[index[str(unit_id)]] = float(value)
    total = float(mass.sum())
    if total <= 0:
        raise RuntimeError(f"zero hard arrival mass for prefix L={max_window}")
    return mass / total


def expected_atomic_mass_from_exposure(
    *,
    unit_ids: list[str],
    opp: pd.DataFrame,
    obs: pd.DataFrame,
    usable: pd.DataFrame,
    max_window: int,
) -> np.ndarray:
    """Soft expected arrival using realized schedule exposures and stage probabilities.

    This is diagnostic only and must never replace hard empirical mass.
    """
    index = {u: i for i, u in enumerate(unit_ids)}
    soft = np.zeros(len(unit_ids), dtype=np.float64)
    sub = opp.loc[
        (opp["window_id"].astype(int) < int(max_window)) & (opp["opportunity_selected"])
    ].copy()
    if sub.empty:
        return soft
    obs_key = obs.copy()
    obs_key["unit_id"] = obs_key["unit_id"].astype(str)
    obs_key["client_id"] = obs_key["client_id"].astype(str)
    use_key = usable.loc[usable["attempt_eligible"]].copy()
    use_key["client_id"] = use_key["client_id"].astype(str)
    merged = sub.merge(
        obs_key[["window_id", "client_id", "unit_id", "observation_probability"]],
        on=["window_id", "client_id", "unit_id"],
        how="left",
    ).merge(
        use_key[["window_id", "client_id", "q_use"]],
        on=["window_id", "client_id"],
        how="left",
    )
    merged["observation_probability"] = merged["observation_probability"].fillna(0.0)
    merged["q_use"] = merged["q_use"].fillna(0.0)
    merged["soft_w"] = (
        merged["candidate_event_mass"].astype(float)
        * merged["observation_probability"].astype(float)
        * merged["q_use"].astype(float)
    )
    grouped = merged.groupby(merged["unit_id"].astype(str), sort=False)["soft_w"].sum()
    for unit_id, value in grouped.items():
        soft[index[str(unit_id)]] = float(value)
    total = float(soft.sum())
    if total <= 0:
        grouped2 = sub.groupby(sub["unit_id"].astype(str), sort=False)[
            "candidate_event_mass"
        ].sum()
        for unit_id, value in grouped2.items():
            soft[index[str(unit_id)]] = float(value)
        total = float(soft.sum())
    if total <= 0:
        return np.zeros(len(unit_ids), dtype=np.float64)
    return soft / total


def aggregate_group_mass(
    atomic_mass: np.ndarray,
    group_ids: np.ndarray,
    n_groups: int,
) -> np.ndarray:
    out = np.zeros(n_groups, dtype=np.float64)
    for g in range(n_groups):
        out[g] = float(atomic_mass[group_ids == g].sum())
    return out


def aggregate_stratum_mass(
    atomic_mass: np.ndarray,
    stratum_ids: np.ndarray,
    n_strata: int,
) -> np.ndarray:
    out = np.zeros(n_strata, dtype=np.float64)
    for s in range(n_strata):
        out[s] = float(atomic_mass[stratum_ids == s].sum())
    return out


def mass_diagnostics(
    *,
    emp_atomic: np.ndarray,
    exp_atomic: np.ndarray,
    target_atomic: np.ndarray,
    scores: np.ndarray,
    group_ids: np.ndarray,
    target_group: np.ndarray,
    stratum_ids: np.ndarray,
    target_stratum: np.ndarray,
    obs_atomic: np.ndarray | None,
    realized_observation_rate: float,
    realized_usable_rate: float,
    active_window_rate: float,
    unsupported_arrival_count: int,
    failed_attempt_omission_count: int,
    q_leakage_count: int,
    total_hard_arrival_mass: float,
) -> dict[str, Any]:
    n_groups = int(target_group.size)
    n_strata = int(target_stratum.size)
    emp_g = aggregate_group_mass(emp_atomic, group_ids, n_groups)
    exp_g = aggregate_group_mass(exp_atomic, group_ids, n_groups)
    emp_s = aggregate_stratum_mass(emp_atomic, stratum_ids, n_strata)
    exp_s = aggregate_stratum_mass(exp_atomic, stratum_ids, n_strata)
    head_t = float(target_atomic[scores == -1].sum())
    tail_t = float(target_atomic[scores == 1].sum())
    tail_ratio = float(emp_atomic[scores == 1].sum() / max(tail_t, 1e-15))
    head_ratio = float(emp_atomic[scores == -1].sum() / max(head_t, 1e-15))
    if obs_atomic is None:
        tail_obs = 1.0
    else:
        tail_obs = float(obs_atomic[scores == 1].sum() / max(tail_t, 1e-15))
    d_tv_obs_g = _tv(
        aggregate_group_mass(obs_atomic if obs_atomic is not None else target_atomic, group_ids, n_groups),
        target_group,
    ) if obs_atomic is not None else 0.0
    d_tv_arr_g = _tv(emp_g, target_group)
    return {
        "D_TV_group": _tv(emp_g, target_group),
        "D_TV_stratum": _tv(emp_s, target_stratum),
        "D_TV_group_exp_emp": _tv(emp_g, exp_g),
        "D_TV_stratum_exp_emp": _tv(emp_s, exp_s),
        "D_TV_atomic_exp_emp": _tv(emp_atomic, exp_atomic),
        "tail_mass_ratio": tail_ratio,
        "head_mass_ratio": head_ratio,
        "tail_mass_ratio_obs": float(tail_obs),
        "cancellation_group_TV": float(d_tv_obs_g - d_tv_arr_g),
        "realized_observation_rate": float(realized_observation_rate),
        "realized_usable_rate": float(realized_usable_rate),
        "active_window_rate": float(active_window_rate),
        "unsupported_arrival_count": int(unsupported_arrival_count),
        "failed_attempt_omission_count": int(failed_attempt_omission_count),
        "q_leakage_count": int(q_leakage_count),
        "total_hard_arrival_mass": float(total_hard_arrival_mass),
        "head_arrival_support": int(((scores == -1) & (emp_atomic > 0)).sum()),
        "tail_arrival_support": int(((scores == 1) & (emp_atomic > 0)).sum()),
        "atomic_arrival_support_ratio": float((emp_atomic > 0).mean()),
        "zero_arrival_supported_atom_count": int((emp_atomic <= 0).sum()),
        "finite_status": bool(np.all(np.isfinite(emp_atomic))),
        "empirical_is_expected_alias": bool(np.allclose(emp_atomic, exp_atomic, atol=0.0, equal_nan=False) and np.shares_memory(emp_atomic, exp_atomic)),
    }
