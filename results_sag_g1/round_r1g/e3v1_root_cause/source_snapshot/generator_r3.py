"""Complete-aligned R3: joint pi_opp, atomic p_obs, realizable staleness."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e3.real_runner.constants import GENERATOR_VERSION, S_MAX, WINDOW_DURATION
from raven_mcs.e3.real_runner.simoracle_q import estimate_q_true_mc
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3
from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata, freeze_event_trace


def build_joint_pi_opp(
    client_ids: list[str],
    strata_by_client: dict[str, list[str]],
    *,
    theta_align: float = 1.25,
    tail_blocks: set[int] | None = None,
) -> dict[tuple[str, str], float]:
    """Joint pi_opp(k,s) with sum_{k,s}=1 (not per-client conditional)."""
    tail_blocks = tail_blocks or {2, 3}
    # Equal client opportunity mass
    p_client = 1.0 / max(len(client_ids), 1)
    raw: dict[tuple[str, str], float] = {}
    for client in client_ids:
        strata = strata_by_client.get(client, [])
        if not strata:
            continue
        scores = []
        for s in strata:
            block = _block_from_stratum(s)
            scores.append(np.exp(-theta_align if block in tail_blocks else 0.0))
        scores_arr = np.asarray(scores, dtype=np.float64)
        cond = scores_arr / scores_arr.sum()
        for s, c in zip(strata, cond):
            raw[(client, s)] = float(p_client * c)
    total = sum(raw.values())
    if total <= 0:
        raise RuntimeError("empty joint pi_opp")
    return {k: v / total for k, v in raw.items()}


def _block_from_stratum(stratum: str) -> int:
    for part in str(stratum).split("::"):
        if part.startswith("block"):
            return int(part.replace("block", ""))
    return 0


def generate_complete_aligned_r3(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
    seed: int,
    num_windows: int,
    mean_observation_rate: float = 0.35,
    s_max: int = S_MAX,
    m_mc: int = 2000,
    delivery_mode: str = "nominal",
    drift_period: int | None = None,
    drift_magnitude: float = 0.0,
) -> tuple[EventTrace, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """delivery_mode='high' is for non-degenerate correctness fixtures only.

    Optional opportunity drift (drifting.yaml): every ``drift_period`` windows,
    a N(0, drift_magnitude) shift is added to log stratum weights.  Defaults
    keep complete_aligned sampling bit-identical (no extra RNG draws).
    """
    rng = np.random.default_rng(int(seed) + 13)
    high = str(delivery_mode) == "high"
    if high:
        mean_observation_rate = max(float(mean_observation_rate), 0.85)
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
    all_strata = sorted({s for strata in strata_by_client.values() for s in strata})
    stratum_to_idx = {s: i for i, s in enumerate(all_strata)}
    drift_shift = np.zeros(len(all_strata), dtype=np.float64)
    period = int(drift_period) if drift_period else 0
    unit_meta = {
        str(r.unit_id): {
            "group": str(r.target_group),
            "spatial": str(r.spatial_id),
            "time_index": int(r.time_index),
            "stratum": str(r.opportunity_stratum),
        }
        for r in atomic.itertuples(index=False)
    }

    opp_rows = []
    pobs_rows = []
    event_rows = []
    for window_id in range(int(num_windows)):
        deadline = float(window_id) + WINDOW_DURATION
        if period > 0 and window_id > 0 and window_id % period == 0:
            drift_shift = rng.normal(0.0, float(drift_magnitude), len(all_strata))
        # Sample one (client, stratum) from JOINT pi_opp for opportunity events per client:
        # each client still gets an event; stratum ~ conditional from joint factorization.
        for client_id in client_ids:
            strata = strata_by_client.get(client_id, [])
            if not strata:
                continue
            joints = np.asarray([pi_opp_joint[(client_id, s)] for s in strata], dtype=np.float64)
            cond = joints / joints.sum()
            if period > 0:
                log_cond = np.log(np.maximum(cond, 1e-12))
                shifts = np.asarray(
                    [drift_shift[stratum_to_idx[s]] for s in strata],
                    dtype=np.float64,
                )
                scores = np.exp(log_cond + shifts)
                cond = scores / scores.sum()
            s_idx = int(rng.choice(len(strata), p=cond))
            stratum = strata[s_idx]
            pi_joint = float(pi_opp_joint[(client_id, stratum)])
            support = pools[(client_id, stratum)]
            k = min(4, len(support))
            risk = list(rng.choice(support, size=k, replace=False)) if k else []

            p_obs_by_unit: dict[str, float] = {}
            for uid in risk:
                block = _block_from_stratum(unit_meta[uid]["group"])
                scale = 0.55 if block in {2, 3} else 1.0
                p_obs_by_unit[uid] = float(np.clip(mean_observation_rate * scale, 0.05, 0.95))
            o_flags = rng.random(len(risk)) < np.asarray([p_obs_by_unit[u] for u in risk]) if risk else []
            observed = [u for u, f in zip(risk, o_flags) if f]

            reg = float(window_id) + 0.05 + 0.01 * client_ids.index(client_id)
            usable = compute_usable_r3(
                rng=rng,
                registration_time=reg,
                window_deadline=deadline,
                window_id=window_id,
                s_max=s_max,
                align_disadvantage=(
                    False if high else (_block_from_stratum(stratum) in {2, 3})
                ),
                has_observations=len(observed) > 0,
                force_device_tier=2 if high else None,
            )
            # High-delivery fixture: if observations exist, force a usable update
            # (still respects EventTrace tau/downloaded invariants).
            if high and len(observed) > 0 and int(usable["U"]) == 0:
                usable = dict(usable)
                usable["U"] = 1
                usable["compute_success"] = True
                usable["network_success"] = True
                usable["deadline_pass"] = True
                usable["staleness_pass"] = True
                if int(usable["tau"]) > int(s_max):
                    usable["tau"] = int(s_max)
                    usable["downloaded_version"] = int(window_id) - int(s_max)
                    usable["model_age"] = float(s_max)
            # Fixed-prestate MC q (formal M_MC)
            q_true = estimate_q_true_mc(
                prestate={
                    "registration_time": reg,
                    "window_deadline": deadline,
                    "window_id": window_id,
                    "s_max": s_max,
                    "align_disadvantage": _block_from_stratum(stratum) in {2, 3},
                    "has_observations": len(observed) > 0,
                    "device_tier_prior": usable["device_tier"],
                },
                m_mc=int(m_mc),
                mc_seed=int(seed) * 10007 + window_id * 97 + client_ids.index(client_id),
            )

            opp_rows.append(
                {
                    "dataset": dataset,
                    "seed": int(seed),
                    "window": int(window_id),
                    "client": client_id,
                    "opportunity_stratum": stratum,
                    "pi_opp_joint": pi_joint,
                    "pi_opp_conditional": float(cond[s_idx]),
                    "p_client": 1.0 / len(client_ids),
                    "generator_version": GENERATOR_VERSION,
                }
            )
            for uid, p in p_obs_by_unit.items():
                pobs_rows.append(
                    {
                        "dataset": dataset,
                        "seed": int(seed),
                        "client_id": client_id,
                        "window": int(window_id),
                        "atomic_unit_id": uid,
                        "p_obs_true": p,
                    }
                )
            # EventTrace schema requires oracle_p/q > 0; true MC q may be 0 when
            # has_observations=False (store eps floor; atomic truth stays in features).
            q_store = float(max(q_true["q_true"], 1e-12))
            p_mean = float(np.mean(list(p_obs_by_unit.values()))) if p_obs_by_unit else mean_observation_rate
            p_store = float(max(p_mean, 1e-12))
            event_rows.append(
                {
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
                        "generator_version": GENERATOR_VERSION,
                        "drift_period": period if period > 0 else None,
                        "drift_magnitude": float(drift_magnitude) if period > 0 else 0.0,
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
                    "oracle_p": p_store,
                    "oracle_q": q_store,
                    "hidden_confounder": 0.0,
                }
            )

    events = pd.DataFrame(event_rows)
    meta = EventTraceMetadata(
        dataset=dataset,
        seed=int(seed),
        num_windows=int(num_windows),
        num_clients=len(client_ids),
        s_max=int(s_max),
        generator=GENERATOR_VERSION,
        notes=("joint pi_opp", "atomic p_obs", "staleness>S_max possible", "MC q")
        + (("opportunity_drift",) if period > 0 else ()),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    audit = {
        "sum_pi_opp_joint": float(sum(pi_opp_joint.values())),
        "n_pairs": len(pi_opp_joint),
        "staleness_gt_smax_rate": float(np.mean(events["tau"].to_numpy() > s_max)),
        "generator_version": GENERATOR_VERSION,
        "drift_period": period if period > 0 else None,
        "drift_magnitude": float(drift_magnitude) if period > 0 else 0.0,
    }
    return trace, pd.DataFrame(opp_rows), pd.DataFrame(pobs_rows), audit


def materialize_r3_trace(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
    out_dir,
    seed: int,
    num_windows: int,
    m_mc: int = 2000,
    delivery_mode: str = "nominal",
    drift_period: int | None = None,
    drift_magnitude: float = 0.0,
) -> dict[str, Any]:
    from pathlib import Path
    import shutil

    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    trace, opp, pobs, audit = generate_complete_aligned_r3(
        dataset=dataset,
        atomic=atomic,
        spatial_to_client=spatial_to_client,
        seed=seed,
        num_windows=num_windows,
        m_mc=m_mc,
        delivery_mode=delivery_mode,
        drift_period=drift_period,
        drift_magnitude=drift_magnitude,
    )
    et_dir = out_dir / "training_eventtrace"
    if et_dir.exists():
        shutil.rmtree(et_dir, ignore_errors=True)
    identity = freeze_event_trace(trace, et_dir)
    opp.to_parquet(out_dir / "opportunity_events.parquet", index=False)
    pobs.to_parquet(out_dir / "atomic_p_obs_true.parquet", index=False)
    return {"identity": identity, "audit": audit, "status": "READY"}
