"""F-1-O: Complete-aligned R3 with a within-stratum observation propensity.

Reference: ccfa-review-reports/raven-mcs-f1-experiment-design.md sections 2, 3.1.

This module differs from ``generator_r3.generate_complete_aligned_r3`` in exactly one place: the
per-risk-unit observation probability.

    published   p_i = clip(mean_observation_rate * scale, 0.05, 0.95),
                      scale = 0.55 on UTC blocks {2,3} else 1.0
    F-1-O       p_i = clip(sigmoid(beta0(block(i)) + theta_O * z_i), 0.05, 0.95),

with ``z_i`` the tercile rank (+1 / 0 / -1) of the unit's ``time_index`` inside its opportunity
stratum, and ``beta0(block)`` solved by bisection so that the mean of ``p`` over that block's train
units equals the published block rate. The marginal is therefore preserved per block by
construction, and the manipulation moves the propensity *inside* the stratum, where the frozen
propensity model (features ``bias``, ``hour_block``, ``planned_workload_pre``) is blind.

No extra RNG draws are taken: ``o_flags`` compares the same uniforms against a different threshold,
so theta_O = 0 reproduces the published trace bit-for-bit. Everything else (opportunity law, risk
set size, stage-2 usable process, MC q, target maps, seeds) is unchanged.

Writes nothing here; use :func:`materialize_f1o_trace` to write a trace directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e3.real_runner.constants import S_MAX, WINDOW_DURATION
from raven_mcs.e3.real_runner.generator_r3 import _block_from_stratum, build_joint_pi_opp
from raven_mcs.e3.real_runner.simoracle_q import estimate_q_true_mc
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3
from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata, freeze_event_trace

GENERATOR_VERSION_F1O = "e3-complete-aligned-r3-f1o-v1"

P_GEN_MIN = 0.05
P_GEN_MAX = 0.95
TAIL_BLOCKS = {2, 3}
PUBLISHED_SCALE = 0.55


def published_block_rate(mean_observation_rate: float, block: int) -> float:
    """The rate the published generator assigns to every unit of this block."""
    scale = PUBLISHED_SCALE if block in TAIL_BLOCKS else 1.0
    return float(np.clip(mean_observation_rate * scale, P_GEN_MIN, P_GEN_MAX))


def within_stratum_terciles(train: pd.DataFrame, stratum_col: str = "opportunity_stratum",
                            time_col: str = "time_index") -> dict[str, int]:
    """z_i in {-1, 0, +1}: thirds of the within-stratum ordering by time_index.

    RNG-free and deterministic. Ties are broken by unit order, which is stable per dataset.
    """
    frames = train[[stratum_col, time_col, "unit_id"]].copy()
    frames[time_col] = frames[time_col].astype(np.int64)
    out: dict[str, int] = {}
    for _, grp in frames.sort_values([stratum_col, time_col]).groupby(stratum_col, sort=False):
        n = len(grp)
        if n == 0:
            continue
        lo, hi = n / 3.0, 2.0 * n / 3.0
        for rank, uid in enumerate(grp["unit_id"].astype(str).to_numpy()):
            out[uid] = -1 if rank < lo else (1 if rank >= hi else 0)
    return out


def bisect_block_intercepts(
    train: pd.DataFrame,
    terciles: dict[str, int],
    *,
    theta: float,
    mean_observation_rate: float,
    tol: float = 1e-12,
    max_iter: int = 200,
) -> dict[int, float]:
    """beta0(block): the logit intercept that restores the published block mean."""
    by_block: dict[int, list[int]] = {}
    for row in train.itertuples(index=False):
        uid = str(row.unit_id)
        z = terciles.get(uid)
        if z is None:
            continue
        by_block.setdefault(_block_from_stratum(str(row.target_group)), []).append(z)

    out: dict[int, float] = {}
    for block, zs in by_block.items():
        z_arr = np.asarray(zs, dtype=np.float64)
        target = published_block_rate(mean_observation_rate, block)

        def mean_p(intercept: float) -> float:
            return float(np.mean(np.clip(
                1.0 / (1.0 + np.exp(-(intercept + theta * z_arr))), P_GEN_MIN, P_GEN_MAX)))

        lo, hi = -60.0, 60.0
        if not (mean_p(lo) - tol <= target <= mean_p(hi) + tol):
            raise ValueError(
                f"infeasible block rate {target} for block {block}; "
                f"attainable [{mean_p(lo):.6f}, {mean_p(hi):.6f}]")
        for _ in range(max_iter):
            mid = 0.5 * (lo + hi)
            if mean_p(mid) < target:
                lo = mid
            else:
                hi = mid
        out[block] = 0.5 * (lo + hi)
    return out


def probability_table(
    intercepts: dict[int, float], theta: float,
) -> dict[tuple[int, int], float]:
    """p for every (block, tercile) cell."""
    return {
        (block, z): float(np.clip(
            1.0 / (1.0 + np.exp(-(beta0 + theta * z))), P_GEN_MIN, P_GEN_MAX))
        for block, beta0 in intercepts.items()
        for z in (-1, 0, 1)
    }


def generate_f1o_trace(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
    seed: int,
    num_windows: int,
    theta: float,
    mean_observation_rate: float = 0.35,
    s_max: int = S_MAX,
    m_mc: int = 2000,
) -> tuple[EventTrace, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Same construction as the published generator, with the F-1-O observation layer."""
    rng = np.random.default_rng(int(seed) + 13)
    train = atomic.loc[atomic["split"].astype(str) == "train"].copy()
    pools: dict[tuple[str, str], list[str]] = {}
    for row in train.itertuples(index=False):
        client = spatial_to_client.get(str(row.spatial_id))
        if client is None:
            continue
        key = (client, str(row.opportunity_stratum))
        pools.setdefault(key, []).append(str(row.unit_id))
    for k in pools:
        pools[k] = sorted(set(pools[k]))
    client_ids = sorted({c for c, _ in pools})
    strata_by_client: dict[str, list[str]] = {}
    for (c, s), units in pools.items():
        if units:
            strata_by_client.setdefault(c, []).append(s)
    for c in strata_by_client:
        strata_by_client[c] = sorted(set(strata_by_client[c]))

    pi_opp_joint = build_joint_pi_opp(client_ids, strata_by_client)
    unit_meta = {
        str(r.unit_id): {
            "group": str(r.target_group),
            "spatial": str(r.spatial_id),
            "time_index": int(r.time_index),
            "stratum": str(r.opportunity_stratum),
        }
        for r in atomic.itertuples(index=False)
    }

    terciles = within_stratum_terciles(train)
    intercepts = bisect_block_intercepts(
        train, terciles, theta=float(theta), mean_observation_rate=float(mean_observation_rate),
    )
    p_table = probability_table(intercepts, float(theta))

    opp_rows = []
    pobs_rows = []
    event_rows = []
    for window_id in range(int(num_windows)):
        deadline = float(window_id) + WINDOW_DURATION
        for client_id in client_ids:
            strata = strata_by_client.get(client_id, [])
            if not strata:
                continue
            joints = np.asarray([pi_opp_joint[(client_id, s)] for s in strata], dtype=np.float64)
            cond = joints / joints.sum()
            s_idx = int(rng.choice(len(strata), p=cond))
            stratum = strata[s_idx]
            pi_joint = float(pi_opp_joint[(client_id, stratum)])
            support = pools[(client_id, stratum)]
            k = min(4, len(support))
            risk = list(rng.choice(support, size=k, replace=False)) if k else []

            p_obs_by_unit: dict[str, float] = {}
            for uid in risk:
                block = _block_from_stratum(unit_meta[uid]["group"])
                p_obs_by_unit[uid] = p_table[(block, terciles.get(uid, 0))]
            o_flags = (rng.random(len(risk)) < np.asarray([p_obs_by_unit[u] for u in risk])
                       if risk else [])
            observed = [u for u, f in zip(risk, o_flags) if f]

            reg = float(window_id) + 0.05 + 0.01 * client_ids.index(client_id)
            usable = compute_usable_r3(
                rng=rng,
                registration_time=reg,
                window_deadline=deadline,
                window_id=window_id,
                s_max=s_max,
                align_disadvantage=_block_from_stratum(stratum) in TAIL_BLOCKS,
                has_observations=len(observed) > 0,
            )
            q_true = estimate_q_true_mc(
                prestate={
                    "registration_time": reg,
                    "window_deadline": deadline,
                    "window_id": window_id,
                    "s_max": s_max,
                    "align_disadvantage": _block_from_stratum(stratum) in TAIL_BLOCKS,
                    "has_observations": len(observed) > 0,
                    "device_tier_prior": usable["device_tier"],
                },
                m_mc=int(m_mc),
                mc_seed=int(seed) * 10007 + window_id * 97 + client_ids.index(client_id),
            )

            opp_rows.append({
                "dataset": dataset,
                "seed": int(seed),
                "window": int(window_id),
                "client": client_id,
                "opportunity_stratum": stratum,
                "pi_opp_joint": pi_joint,
                "pi_opp_conditional": float(cond[s_idx]),
                "p_client": 1.0 / len(client_ids),
                "generator_version": GENERATOR_VERSION_F1O,
                "theta_O": float(theta),
            })
            for uid, p in p_obs_by_unit.items():
                pobs_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "client_id": client_id,
                    "window": int(window_id),
                    "atomic_unit_id": uid,
                    "p_obs_true": p,
                })
            q_store = float(max(q_true["q_true"], 1e-12))
            p_mean = float(np.mean(list(p_obs_by_unit.values()))) if p_obs_by_unit else 0.0
            event_rows.append({
                "window_id": int(window_id),
                "client_id": client_id,
                "risk_set_unit_ids": list(risk),
                "opportunity_features": {
                    "pi_opp_true": pi_joint,
                    "p_obs_true": p_mean,
                    "p_obs_true_by_unit": p_obs_by_unit,
                    "q_use_true": float(q_true["q_true"]),
                    "q_mc_se": float(q_true["q_se"]),
                    "M_MC": int(m_mc),
                    "opportunity_stratum": stratum,
                    "generator_version": GENERATOR_VERSION_F1O,
                    "theta_O": float(theta),
                    "drift_period": None,
                    "drift_magnitude": 0.0,
                    "occupancy_A": 1,
                },
                "observed_unit_ids": list(observed),
                "O": {u: True for u in observed},
                "registration_time": float(usable["T_reg"]),
                "downloaded_version": int(usable["downloaded_version"]),
                "model_age": float(usable["tau"]),
                "tau": int(usable["tau"]),
                "device_profile": usable["device_profile"],
                "network_profile": usable["network_profile"],
                "compute_success": bool(usable["compute_success"]),
                "compute_duration": float(usable["T_cmp"]),
                "network_success": bool(usable["network_success"]),
                "network_duration": float(usable["T_net"]),
                "arrival_time": float(usable["T_arr"]),
                "U": int(usable["U"]),
                "raw_workload": float(len(observed)),
                "oracle_p": float(max(p_mean, 1e-12)),
                "oracle_q": q_store,
                "hidden_confounder": 0.0,
            })

    events = pd.DataFrame(event_rows)
    meta = EventTraceMetadata(
        dataset=dataset,
        seed=int(seed),
        num_windows=int(num_windows),
        num_clients=len(client_ids),
        s_max=int(s_max),
        generator=GENERATOR_VERSION_F1O,
        notes=("joint pi_opp", "atomic p_obs", "within-stratum theta_O", "MC q"),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    audit = {
        "sum_pi_opp_joint": float(sum(pi_opp_joint.values())),
        "n_pairs": len(pi_opp_joint),
        "theta_O": float(theta),
        "block_intercepts": {str(k): float(v) for k, v in intercepts.items()},
        "p_by_block_tercile": {f"{b}|{z}": float(v) for (b, z), v in p_table.items()},
        "published_block_rates": {
            str(b): published_block_rate(mean_observation_rate, b) for b in sorted(intercepts)
        },
        "generator_version": GENERATOR_VERSION_F1O,
        "n_event_rows": int(len(events)),
        "n_client_windows": int(len(client_ids) * int(num_windows)),
    }
    return trace, pd.DataFrame(opp_rows), pd.DataFrame(pobs_rows), audit


def materialize_f1o_trace(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
    out_dir,
    seed: int,
    num_windows: int,
    theta: float,
    m_mc: int = 2000,
) -> dict[str, Any]:
    import shutil

    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    trace, opp, pobs, audit = generate_f1o_trace(
        dataset=dataset,
        atomic=atomic,
        spatial_to_client=spatial_to_client,
        seed=seed,
        num_windows=num_windows,
        theta=theta,
        m_mc=m_mc,
    )
    et_dir = out_dir / "training_eventtrace"
    if et_dir.exists():
        shutil.rmtree(et_dir, ignore_errors=True)
    identity = freeze_event_trace(trace, et_dir)
    opp.to_parquet(out_dir / "opportunity_events.parquet", index=False)
    pobs.to_parquet(out_dir / "atomic_p_obs_true.parquet", index=False)
    return {"identity": identity, "audit": audit, "status": "READY"}
