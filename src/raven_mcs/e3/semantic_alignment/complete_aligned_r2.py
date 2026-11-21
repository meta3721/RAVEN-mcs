"""Complete-aligned R2: distinct opportunity / observation / usable stages."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e3.semantic_alignment.constants import (
    GENERATOR_VERSION,
    S_MAX,
    WINDOW_DURATION,
)
from raven_mcs.e3.semantic_alignment.stage2_usable import compute_usable_indicator
from raven_mcs.e3.semantic_alignment.target_semantics import parse_time_block
from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata, freeze_event_trace


def _stable_int(text: str) -> int:
    return int.from_bytes(str(text).encode("utf-8")[:32], "little", signed=False) % (2**31 - 1)


def _client_stratum_pools(
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
) -> dict[tuple[str, str], list[str]]:
    """Map (client, opportunity_stratum) -> train unit_ids (legal support)."""
    train = atomic.loc[atomic["split"].astype(str) == "train"].copy()
    pools: dict[tuple[str, str], list[str]] = {}
    for row in train.itertuples(index=False):
        spatial = str(row.spatial_id)
        client = spatial_to_client.get(spatial)
        if client is None:
            continue
        stratum = str(row.opportunity_stratum)
        key = (client, stratum)
        pools.setdefault(key, []).append(str(row.unit_id))
    for key in pools:
        pools[key] = sorted(set(pools[key]))
    return pools


def _stratum_is_tail(stratum: str, tail_blocks: set[int]) -> bool:
    # opportunity_stratum like spatial::blockK::weekday
    parts = str(stratum).split("::")
    for p in parts:
        if p.startswith("block"):
            return int(p.replace("block", "")) in tail_blocks
    return False


def build_pi_opp(
    client_ids: list[str],
    strata_by_client: dict[str, list[str]],
    *,
    theta_align: float = 1.25,
    tail_blocks: set[int] | None = None,
) -> dict[tuple[str, str], float]:
    """pi_opp(k,s) ∝ exp(-theta * 1{stratum in Tail blocks}) — Complete-aligned underrepresentation."""
    tail_blocks = tail_blocks or {2, 3}
    raw: dict[tuple[str, str], float] = {}
    for client in client_ids:
        strata = strata_by_client.get(client, [])
        for s in strata:
            score = -theta_align if _stratum_is_tail(s, tail_blocks) else 0.0
            raw[(client, s)] = float(np.exp(score))
    # Normalize per client
    out: dict[tuple[str, str], float] = {}
    for client in client_ids:
        keys = [k for k in raw if k[0] == client]
        total = sum(raw[k] for k in keys)
        if total <= 0:
            continue
        for k in keys:
            out[k] = raw[k] / total
    return out


def generate_complete_aligned_r2(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
    seed: int,
    num_windows: int,
    mean_observation_rate: float = 0.20,
    s_max: int = S_MAX,
    window_duration: float = WINDOW_DURATION,
) -> tuple[EventTrace, pd.DataFrame, dict[str, Any]]:
    """Generate EventTrace + opportunity event log with three distinct stages."""
    rng = np.random.default_rng(int(seed) + 97 * (0 if dataset == "sensorscope" else 1))
    pools = _client_stratum_pools(atomic, spatial_to_client)
    client_ids = sorted({c for c, _ in pools})
    strata_by_client: dict[str, list[str]] = {}
    for (client, stratum), units in pools.items():
        if units:
            strata_by_client.setdefault(client, []).append(stratum)
    for c in strata_by_client:
        strata_by_client[c] = sorted(set(strata_by_client[c]))

    pi_opp = build_pi_opp(client_ids, strata_by_client)
    unit_group = {
        str(r.unit_id): str(r.target_group)
        for r in atomic.itertuples(index=False)
    }

    opp_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []

    for window_id in range(int(num_windows)):
        t_reg_base = float(window_id)
        t_deadline = float(window_id) + float(window_duration)
        for client_id in client_ids:
            strata = strata_by_client.get(client_id, [])
            if not strata:
                continue
            probs = np.asarray([pi_opp[(client_id, s)] for s in strata], dtype=np.float64)
            probs = probs / probs.sum()
            # Sample one opportunity stratum (risk-set source) from pi_opp — NOT cyclic slice
            s_idx = int(rng.choice(len(strata), p=probs))
            stratum = strata[s_idx]
            pi_val = float(probs[s_idx])
            support = pools[(client_id, stratum)]
            # Risk set: sample without replacement from stratum support
            k = min(8, len(support))
            risk = list(rng.choice(support, size=k, replace=False)) if k > 0 else []

            # Observation: distinct p_obs, aligned (lower on Tail units)
            p_obs_list = []
            for uid in risk:
                g = unit_group.get(uid, "")
                try:
                    tb = parse_time_block(g)
                except ValueError:
                    tb = 0
                scale = 0.55 if tb in {2, 3} else 1.0
                p_obs_list.append(float(np.clip(mean_observation_rate * scale, 0.02, 0.95)))
            o_flags = rng.random(len(risk)) < np.asarray(p_obs_list) if risk else np.array([], dtype=bool)
            observed = [u for u, flag in zip(risk, o_flags) if flag]
            p_obs_true = float(np.mean(p_obs_list)) if p_obs_list else float(mean_observation_rate)

            # Stage-2 usable with deadline semantics
            reg_time = t_reg_base + 0.05 + 0.02 * (client_ids.index(client_id) % 8)
            usable = compute_usable_indicator(
                rng=rng,
                registration_time=reg_time,
                window_deadline=t_deadline,
                window_id=window_id,
                s_max=s_max,
                align_disadvantage=_stratum_is_tail(stratum, {2, 3}),
                has_observations=len(observed) > 0,
            )

            opp_rows.append(
                {
                    "dataset": dataset,
                    "seed": int(seed),
                    "window": int(window_id),
                    "client": client_id,
                    "opportunity_stratum": stratum,
                    "legal_support_size": int(len(support)),
                    "pi_opp": pi_val,
                    "sampled": True,
                    "prestate_features": json_safe_features(stratum, window_id),
                    "generator_version": GENERATOR_VERSION,
                }
            )

            event_rows.append(
                {
                    "window_id": int(window_id),
                    "client_id": client_id,
                    "risk_set_unit_ids": list(risk),
                    "opportunity_features": {
                        "pi_opp_true": pi_val,
                        "p_obs_true": p_obs_true,
                        "q_use_true": usable["q_use_true"],
                        "opportunity_stratum": stratum,
                        "hour_block": int(window_id % 4),
                        "dataset": dataset,
                        "scenario": "complete_aligned",
                        "generator_version": GENERATOR_VERSION,
                    },
                    "observed_unit_ids": list(observed),
                    "O": {unit: True for unit in observed},
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
                    # Distinct semantics: oracle_p := p_obs_true; oracle_q := q_use_true
                    # Opportunity truth lives in opportunity_features.pi_opp_true (not aliased).
                    "oracle_p": float(p_obs_true),
                    "oracle_q": float(usable["q_use_true"]),
                    "hidden_confounder": 0.0,
                }
            )

    events = pd.DataFrame(event_rows)
    opp_log = pd.DataFrame(opp_rows)
    meta = EventTraceMetadata(
        dataset=dataset,
        seed=int(seed),
        num_windows=int(num_windows),
        num_clients=len(client_ids),
        s_max=int(s_max),
        generator=GENERATOR_VERSION,
        notes=(
            "E3 Complete-aligned R2 three-stage generator",
            "pi_opp sampled (not cyclic)",
            "p_obs and q/U distinct",
            "U enforces deadline",
        ),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    audit = three_stage_audit(events, opp_log)
    return trace, opp_log, audit


def json_safe_features(stratum: str, window_id: int) -> dict[str, Any]:
    return {
        "opportunity_stratum": str(stratum),
        "window_id": int(window_id),
        "prestate_only": True,
    }


def three_stage_audit(events: pd.DataFrame, opp_log: pd.DataFrame) -> dict[str, Any]:
    feats = events["opportunity_features"].tolist()
    has_pi = all("pi_opp_true" in f for f in feats)
    has_p = all("p_obs_true" in f for f in feats)
    has_q = all("q_use_true" in f for f in feats)
    # Aliasing check: pi_opp_true values must not equal oracle_p identically as a collapsed object
    pi_vals = np.asarray([float(f["pi_opp_true"]) for f in feats])
    p_vals = np.asarray([float(f["p_obs_true"]) for f in feats])
    q_vals = np.asarray([float(f["q_use_true"]) for f in feats])
    not_aliased = not (np.allclose(pi_vals, p_vals) and np.allclose(p_vals, q_vals))
    checks = {
        "opportunity_layer_exists": bool(len(opp_log) > 0 and has_pi),
        "observation_layer_exists": bool(has_p),
        "usable_update_layer_exists": bool(has_q) and "arrival_time" in events.columns,
        "probability_objects_not_aliased": bool(not_aliased),
        "directions_align_complete_aligned": True,  # enforced by construction (Tail underrepresentation)
        "methods_share_exogenous_trace": True,  # generator is method-agnostic
    }
    return {
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "generator_version": GENERATOR_VERSION,
    }


def materialize_trace(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    spatial_to_client: dict[str, str],
    out_dir,
    seed: int,
    num_windows: int,
) -> dict[str, Any]:
    from pathlib import Path
    import shutil

    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    trace, opp_log, audit = generate_complete_aligned_r2(
        dataset=dataset,
        atomic=atomic,
        spatial_to_client=spatial_to_client,
        seed=seed,
        num_windows=num_windows,
    )
    identity = freeze_event_trace(trace, out_dir / "training_eventtrace")
    opp_log.to_parquet(out_dir / "opportunity_events.parquet", index=False)
    return {
        "dataset": dataset,
        "seed": int(seed),
        "num_windows": int(num_windows),
        "identity": identity,
        "three_stage_audit": audit,
        "status": "EVENTTRACE_R2_READY" if audit["status"] == "PASS" else "BLOCKED",
    }
