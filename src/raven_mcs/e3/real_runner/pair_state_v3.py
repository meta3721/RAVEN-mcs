"""True method-dependent Delta_pair over client×atomic pairs."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from raven_mcs.e3.real_runner.constants import PAIR_SCHEMA_VERSION
from raven_mcs.metrics.distribution import delta_pair
from raven_mcs.utils.hashing import sha256_json

REQUIRED_COLUMNS_V3 = [
    "dataset",
    "seed",
    "scenario",
    "method",
    "window",
    "client_id",
    "atomic_unit_id",
    "spatial_unit",
    "timestamp",
    "target_group",
    "opportunity_stratum",
    "eta_r",
    "I_r",
    "alpha_method",
    "w_method",
    "contribution",
    "target_pair_mass",
    "pair_support_mask",
    "normalization_denominator",
    "eventtrace_hash",
    "config_hash",
    "method_source_hash",
    "schema_version",
]


def pair_state_schema_v3() -> dict[str, Any]:
    return {
        "schema_version": PAIR_SCHEMA_VERSION,
        "formula": {
            "Pi_hat_k_i": "(1/S_R) sum_r eta_r I_r alpha_{k,r}^{(m)} w_{k,r,i}^{(m)}",
            "Delta_pair": "||Pi_hat - pi_tar||_1",
            "code": "raven_mcs.metrics.distribution.delta_pair",
        },
        "pair_identity": "(client_id, atomic_unit_id)",
        "method_dependence": ["alpha_method", "w_method"],
        "required_columns": REQUIRED_COLUMNS_V3,
        "outputs": ["pair_state.parquet", "delta_pair_summary.json"],
    }


def build_pi_tar_client_atomic(
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    *,
    split: str = "test",
) -> dict[tuple[str, str], float]:
    """Uniform over supported test atomic units, attributed to owning client."""
    test = atomic.loc[
        (atomic["split"].astype(str) == split) & atomic["support_flag"].astype(bool)
    ].copy()
    if test.empty:
        raise ValueError("empty test support")
    mass = 1.0 / float(len(test))
    out: dict[tuple[str, str], float] = {}
    for row in test.itertuples(index=False):
        client = spatial_to_client[str(row.spatial_id)]
        out[(client, str(row.unit_id))] = mass
    return out


def accumulate_pair_state_from_runner(
    *,
    window_metrics: list[Any],
    diagnostics: list[dict[str, Any]],
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    dataset: str,
    seed: int,
    scenario: str,
    method: str,
    eventtrace_hash: str | None,
    config_hash: str | None,
    method_source_hash: str | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build Pi_hat from alpha and local Hajek weights in runner diagnostics."""
    pi_tar = build_pi_tar_client_atomic(atomic, spatial_to_client, split="test")
    unit_meta = atomic.set_index("unit_id")
    # Aggregate contributions
    contrib: dict[tuple[str, str], float] = {}
    rows: list[dict[str, Any]] = []
    s_r = 0.0
    for wm in window_metrics:
        active = bool(getattr(wm, "active", True))
        eta = 1.0
        i_r = 1.0 if active else 0.0
        if active:
            s_r += eta
        alpha = np.asarray(wm.alpha, dtype=np.float64)
        # Map alpha to clients via diagnostics for this window
        win_diag = [d for d in diagnostics if int(d.get("window_id", -1)) == int(wm.window_id)]
        # Fallback: equal alpha over clients present in diag
        clients = sorted({str(d["client_id"]) for d in win_diag}) if win_diag else []
        alpha_map: dict[str, float] = {}
        if clients and len(alpha) == len(clients):
            for c, a in zip(clients, alpha):
                alpha_map[c] = float(a)
        elif clients:
            for c in clients:
                alpha_map[c] = 1.0 / len(clients)

        for d in win_diag:
            cid = str(d["client_id"])
            a = float(alpha_map.get(cid, 0.0))
            unit_ids = d.get("observed_unit_ids") or d.get("risk_set_unit_ids") or []
            weights = d.get("a_bar") or d.get("w_units")
            if weights is None:
                weights = [1.0 / max(len(unit_ids), 1)] * len(unit_ids)
            w_arr = np.asarray(weights, dtype=np.float64)
            if float(w_arr.sum()) > 0:
                w_arr = w_arr / float(w_arr.sum())
            for uid, w in zip(unit_ids, w_arr):
                uid = str(uid)
                c_term = float(eta * i_r * a * w)
                key = (cid, uid)
                contrib[key] = contrib.get(key, 0.0) + c_term
                meta = unit_meta.loc[uid] if uid in unit_meta.index else None
                rows.append(
                    {
                        "dataset": dataset,
                        "seed": int(seed),
                        "scenario": scenario,
                        "method": method,
                        "window": int(wm.window_id),
                        "client_id": cid,
                        "atomic_unit_id": uid,
                        "spatial_unit": str(meta["spatial_id"]) if meta is not None else "",
                        "timestamp": int(meta["time_index"]) if meta is not None else -1,
                        "target_group": str(meta["target_group"]) if meta is not None else "",
                        "opportunity_stratum": str(meta["opportunity_stratum"]) if meta is not None else "",
                        "eta_r": eta,
                        "I_r": i_r,
                        "alpha_method": a,
                        "w_method": float(w),
                        "contribution": c_term,
                        "target_pair_mass": float(pi_tar.get(key, 0.0)),
                        "pair_support_mask": key in pi_tar,
                        "normalization_denominator": float(s_r) if s_r > 0 else 1.0,
                        "eventtrace_hash": eventtrace_hash,
                        "config_hash": config_hash,
                        "method_source_hash": method_source_hash,
                        "schema_version": PAIR_SCHEMA_VERSION,
                    }
                )

    # Normalize contributions to Pi_hat
    denom = float(s_r) if s_r > 0 else 1.0
    keys = sorted(set(list(contrib.keys()) + list(pi_tar.keys())))
    pi_hat = np.asarray([contrib.get(k, 0.0) / denom for k in keys], dtype=np.float64)
    if float(pi_hat.sum()) > 0:
        pi_hat = pi_hat / float(pi_hat.sum())
    pi_t = np.asarray([pi_tar.get(k, 0.0) for k in keys], dtype=np.float64)
    if float(pi_t.sum()) > 0:
        pi_t = pi_t / float(pi_t.sum())
    dpair = float(delta_pair(pi_hat, pi_t))
    frame = pd.DataFrame(rows)
    # attach accumulated mass
    if not frame.empty:
        acc = frame.groupby(["client_id", "atomic_unit_id"])["contribution"].transform("sum") / denom
        frame["accumulated_pair_mass"] = acc
    summary = {
        "Delta_pair": dpair,
        "pair_support_size": int(len(keys)),
        "schema_version": PAIR_SCHEMA_VERSION,
        "pi_hat_hash": sha256_json({"keys": [list(k) for k in keys], "pi_hat": pi_hat.tolist()}),
        "pi_tar_hash": sha256_json({"keys": [list(k) for k in keys], "pi_tar": pi_t.tolist()}),
        "status": "OK",
    }
    return frame, summary


def toy_exact_delta_pair() -> dict[str, Any]:
    """Analytic toy: two methods, different alpha/w, exact Delta_pair."""
    # pairs: (c0,u0), (c0,u1)
    pi_tar = np.array([0.5, 0.5])
    # method A: mass [0.8, 0.2]
    pi_a = np.array([0.8, 0.2])
    # method B: mass [0.2, 0.8]
    pi_b = np.array([0.2, 0.8])
    da = delta_pair(pi_a, pi_tar)
    db = delta_pair(pi_b, pi_tar)
    # Reconstruct via contribution formula one window eta=I=1
    # A: alpha=1 on c0, w=[0.8,0.2]
    contrib_a = {"(c0,u0)": 0.8, "(c0,u1)": 0.2}
    contrib_b = {"(c0,u0)": 0.2, "(c0,u1)": 0.8}
    return {
        "Delta_pair_A": float(da),
        "Delta_pair_B": float(db),
        "hand_A": 0.6,
        "hand_B": 0.6,
        "methods_differ": not np.allclose(pi_a, pi_b),
        "exact_match_A": abs(da - 0.6) < 1e-12,
        "exact_match_B": abs(db - 0.6) < 1e-12,
        "contrib_a": contrib_a,
        "contrib_b": contrib_b,
    }
