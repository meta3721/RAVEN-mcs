"""Offline reconstruction of Head/Tail/Delta_group from frozen formal artifacts."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.aggregation.debt import coverage_mix
from raven_mcs.correction.hajek import composition, group_mass, raw_weights, total_mass
from raven_mcs.e2.traffic_offline_recon import HEAD_GROUPS, TAIL_GROUPS
from raven_mcs.e2.traffic_real_runner import load_target_mu_traffic
from raven_mcs.metrics.distribution import delta_group


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_listy(value: Any) -> list[Any]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return ast.literal_eval(text)
    return list(value)


def _parse_o_dict(value: Any, risk_ids: list[str]) -> np.ndarray:
    if isinstance(value, dict):
        return np.asarray([1.0 if value.get(uid) else 0.0 for uid in risk_ids], dtype=np.float64)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = ast.literal_eval(value)
        if isinstance(parsed, dict):
            return np.asarray([1.0 if parsed.get(uid) else 0.0 for uid in risk_ids], dtype=np.float64)
    arr = np.asarray(_parse_listy(value), dtype=np.float64)
    if arr.size == len(risk_ids):
        return arr
    raise ValueError("O length mismatch with risk set")


def head_tail_from_group_rmse(group_rmse: dict[str, float]) -> dict[str, float]:
    head_vals = [float(group_rmse[g]) for g in HEAD_GROUPS]
    tail_vals = [float(group_rmse[g]) for g in TAIL_GROUPS]
    return {
        "Head_RMSE": float(np.sqrt(np.mean(np.square(head_vals)))),
        "Tail_RMSE": float(np.sqrt(np.mean(np.square(tail_vals)))),
        "head_group_size": len(HEAD_GROUPS),
        "tail_group_size": len(TAIL_GROUPS),
    }


def reconstruct_head_tail_table(formal_results_dir: Path) -> pd.DataFrame:
    rows = []
    runs = formal_results_dir / "runs"
    for seed_dir in sorted(p for p in runs.iterdir() if p.is_dir()):
        seed = int(seed_dir.name)
        for scenario_dir in sorted(p for p in seed_dir.iterdir() if p.is_dir()):
            scenario = scenario_dir.name
            for method_dir in sorted(p for p in scenario_dir.iterdir() if p.is_dir()):
                method = method_dir.name
                metrics_path = method_dir / "final_metrics.json"
                if not metrics_path.is_file():
                    rows.append(
                        {
                            "seed": seed,
                            "scenario": scenario,
                            "method": method,
                            "Head_RMSE": np.nan,
                            "Tail_RMSE": np.nan,
                            "head_group_size": 2,
                            "tail_group_size": 2,
                            "source_artifact_identity": None,
                            "reconstruction_status": "MISSING_EVIDENCE",
                        }
                    )
                    continue
                metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
                ht = head_tail_from_group_rmse(metrics["group_rmse"])
                rows.append(
                    {
                        "seed": seed,
                        "scenario": scenario,
                        "method": method,
                        **ht,
                        "source_artifact_identity": f"{metrics_path.as_posix()}#{_sha(metrics_path)[:16]}",
                        "reconstruction_status": "EXACTLY_RECONSTRUCTABLE",
                        "definition_version": "traffic_HEAD_GROUPS_block0_block1_TAIL_block2_block3_equal_mass_pool",
                    }
                )
    return pd.DataFrame(rows)


def load_unit_group_map(root: Path) -> dict[str, int]:
    """Public-target / hour-block group ids (identical for traffic protocol units)."""
    from raven_mcs.e2.traffic_real_runner import traffic_dataset

    ds = traffic_dataset(root)
    out: dict[str, int] = {}
    for uid in ds._atomic_df["unit_id"].astype(str).tolist():
        unit = ds.get_atomic_by_id(str(uid))
        if unit is not None:
            out[str(uid)] = int(unit.target_group)
    return out


def preload_eventtrace_index(events: pd.DataFrame, unit_group: dict[str, int]) -> dict[tuple[int, str], dict[str, Any]]:
    """Pre-parse eventtrace rows into (window, client) -> risk/O/groups."""
    index: dict[tuple[int, str], dict[str, Any]] = {}
    order: dict[int, list[str]] = {}
    for r in events.itertuples(index=False):
        wid = int(r.window_id)
        cid = str(r.client_id)
        risk_ids = [str(x) for x in _parse_listy(r.risk_set_unit_ids)]
        groups = np.asarray([unit_group[uid] for uid in risk_ids], dtype=np.int64)
        o = _parse_o_dict(r.O, risk_ids)
        index[(wid, cid)] = {
            "risk_ids": risk_ids,
            "groups": groups,
            "O": o,
            "U": bool(r.U),
        }
        order.setdefault(wid, []).append(cid)
    return {"by_key": index, "order": order}


def reconstruct_delta_group_one(
    *,
    root: Path,
    seed: int,
    scenario: str,
    method: str,
    run_dir: Path,
    et_index: dict[str, Any],
    mu: np.ndarray,
    eta: float = 0.01,
    a_max: float = 40.0,
    p_min: float = 0.05,
) -> dict[str, Any]:
    diag_path = run_dir / "runner_diagnostics.parquet"
    if not diag_path.is_file():
        return {
            "seed": seed,
            "scenario": scenario,
            "method": method,
            "Delta_group": np.nan,
            "exact_definition_version": "F7.3_delta_group_omega_bar_minus_mu_l1",
            "source_artifact_identity": None,
            "reconstruction_status": "MISSING_DIAGNOSTICS",
        }
    diag = pd.read_parquet(diag_path)
    by_key = et_index["by_key"]
    order = et_index["order"]
    omega_sum = np.zeros(4, dtype=np.float64)
    scale = 0.0
    used_windows = 0

    # Pre-index diagnostics by (window, client)
    diag_map: dict[tuple[int, str], pd.Series] = {}
    for _, row in diag.iterrows():
        diag_map[(int(row.window_id), str(row.client_id))] = row

    for wid, client_order in order.items():
        a_r = [cid for cid in client_order if by_key[(wid, cid)]["U"] and (wid, cid) in diag_map]
        a_r = [cid for cid in a_r if np.isfinite(float(diag_map[(wid, cid)]["alpha"]))]
        if not a_r:
            continue
        cols = []
        alpha = []
        for cid in a_r:
            row = diag_map[(wid, cid)]
            info = by_key[(wid, cid)]
            risk_ids = info["risk_ids"]
            zeta = np.asarray(_parse_listy(row["zeta_hat"]), dtype=np.float64)
            p_hat = np.asarray(_parse_listy(row["p_hat"]), dtype=np.float64)
            if zeta.size != len(risk_ids) or p_hat.size != len(risk_ids):
                return {
                    "seed": seed,
                    "scenario": scenario,
                    "method": method,
                    "Delta_group": np.nan,
                    "exact_definition_version": "F7.3_delta_group_omega_bar_minus_mu_l1",
                    "source_artifact_identity": f"{diag_path.as_posix()}#{_sha(diag_path)[:16]}",
                    "reconstruction_status": "ALIGNMENT_FAILURE",
                }
            a_raw = raw_weights(zeta, p_hat, a_max=a_max, p_min=p_min)
            m_g = group_mass(info["O"], a_raw, info["groups"], n_groups=4)
            m_total = total_mass(m_g)
            c_g = composition(m_g, m_total) if m_total > 0 else np.full(4, 0.25)
            cols.append(c_g)
            alpha.append(float(row["alpha"]))
        alpha_arr = np.asarray(alpha, dtype=np.float64)
        if abs(float(alpha_arr.sum()) - 1.0) > 1e-5:
            alpha_arr = alpha_arr / max(float(alpha_arr.sum()), 1e-12)
        omega = coverage_mix(np.column_stack(cols), alpha_arr)
        omega_sum = omega_sum + float(eta) * omega
        scale += float(eta)
        used_windows += 1

    if scale <= 0 or used_windows == 0:
        return {
            "seed": seed,
            "scenario": scenario,
            "method": method,
            "Delta_group": np.nan,
            "exact_definition_version": "F7.3_delta_group_omega_bar_minus_mu_l1",
            "source_artifact_identity": f"{diag_path.as_posix()}#{_sha(diag_path)[:16]}",
            "reconstruction_status": "NO_ACTIVE_WINDOWS",
        }
    omega_bar = omega_sum / scale
    return {
        "seed": seed,
        "scenario": scenario,
        "method": method,
        "Delta_group": float(delta_group(omega_bar, mu)),
        "omega_bar_0": float(omega_bar[0]),
        "omega_bar_1": float(omega_bar[1]),
        "omega_bar_2": float(omega_bar[2]),
        "omega_bar_3": float(omega_bar[3]),
        "active_windows_used": int(used_windows),
        "exact_definition_version": "F7.3_delta_group_omega_bar_minus_mu_l1",
        "source_artifact_identity": f"{diag_path.as_posix()}#{_sha(diag_path)[:16]}",
        "reconstruction_status": "RECONSTRUCTABLE_FROM_FROZEN_DIAGNOSTICS",
    }
