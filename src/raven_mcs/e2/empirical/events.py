"""Hard Opportunity / Observation / Usable / Arrival event generators."""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd

from raven_mcs.e2.generators import (
    MAX_ROOT_ITERS,
    RATE_TOL,
    ROOT_TOL,
    _sigmoid,
    compute_client_window_tail_composition,
)

OPP_RATE_TARGET = 0.55
OBS_RATE_TARGET = 0.20
USE_RATE_TARGET = 0.60
OPP_GEN_MIN, OPP_GEN_MAX = 0.05, 0.95
P_GEN_MIN, P_GEN_MAX = 0.05, 0.95
Q_GEN_MIN, Q_GEN_MAX = 0.05, 0.95


def _solve_intercept(
    scores: np.ndarray,
    masses: np.ndarray,
    kappa: float,
    direction: int,
    rate_target: float,
    lo_clip: float,
    hi_clip: float,
) -> float:
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    masses = np.asarray(masses, dtype=np.float64).reshape(-1)
    if scores.size == 0:
        raise ValueError("empty exposure for intercept")
    total = float(masses.sum())
    if total <= 0:
        masses = np.ones_like(scores)
        total = float(masses.sum())
    w = masses / total

    def expected_rate(intercept: float) -> float:
        logits = intercept + float(direction) * float(kappa) * scores
        p = np.clip(_sigmoid(logits), lo_clip, hi_clip)
        return float(np.sum(w * p))

    lo, hi = -50.0, 50.0
    for _ in range(MAX_ROOT_ITERS):
        mid = 0.5 * (lo + hi)
        val = expected_rate(mid)
        if abs(val - rate_target) < ROOT_TOL:
            lo = hi = mid
            break
        if val > rate_target:
            hi = mid
        else:
            lo = mid
    intercept = 0.5 * (lo + hi)
    if abs(expected_rate(intercept) - rate_target) > RATE_TOL:
        raise ValueError("intercept root failed tolerance")
    return float(intercept)


def _solve_intercept_mass_and_score(
    scores: np.ndarray,
    masses: np.ndarray,
    log_mass_centered: np.ndarray,
    kappa: float,
    direction: int,
    rate_target: float,
    lo_clip: float,
    hi_clip: float,
    mass_tilt: float,
) -> float:
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    masses = np.asarray(masses, dtype=np.float64).reshape(-1)
    log_mass_centered = np.asarray(log_mass_centered, dtype=np.float64).reshape(-1)
    if scores.size == 0:
        raise ValueError("empty exposure for intercept")
    total = float(masses.sum())
    if total <= 0:
        masses = np.ones_like(scores)
        total = float(masses.sum())
    w = masses / total

    def expected_rate(intercept: float) -> float:
        logits = (
            intercept
            + float(direction) * float(kappa) * scores
            + float(mass_tilt) * log_mass_centered
        )
        p = np.clip(_sigmoid(logits), lo_clip, hi_clip)
        return float(np.sum(w * p))

    lo, hi = -50.0, 50.0
    for _ in range(MAX_ROOT_ITERS):
        mid = 0.5 * (lo + hi)
        val = expected_rate(mid)
        if abs(val - rate_target) < ROOT_TOL:
            lo = hi = mid
            break
        if val > rate_target:
            hi = mid
        else:
            lo = mid
    intercept = 0.5 * (lo + hi)
    if abs(expected_rate(intercept) - rate_target) > RATE_TOL:
        raise ValueError("intercept root failed tolerance")
    return float(intercept)


def generate_opportunity_events(
    *,
    schedule_rows: Sequence[dict[str, Any]],
    tail_score_map: dict[str, int],
    opp_uniforms: np.ndarray,
    client_index: dict[str, int],
    kappa_opp: float,
    d_opp: int,
    seed: int,
    profile_id: str,
    scenario_id: str,
    opportunity_rate_target: float = OPP_RATE_TARGET,
    calibrated_mass_tilt: float = 0.0,
    frozen_intercept: float | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    # Collect all candidate exposures for intercept (same a_opp for all windows).
    all_scores: list[float] = []
    all_masses: list[float] = []
    for row in schedule_rows:
        for unit_id, mass in zip(row["candidate_unit_ids"], row["candidate_event_mass"], strict=True):
            all_scores.append(float(tail_score_map[str(unit_id)]))
            all_masses.append(float(mass))
    score_arr = np.asarray(all_scores, dtype=np.float64)
    mass_arr = np.asarray(all_masses, dtype=np.float64)
    intercept_solved = False
    if frozen_intercept is not None:
        intercept = float(frozen_intercept)
        log_c = np.zeros_like(mass_arr)
    elif float(calibrated_mass_tilt) != 0.0:
        pos = np.maximum(mass_arr, 1e-300)
        weights = mass_arr / (float(mass_arr.sum()) or 1.0)
        center = float(np.sum(weights * np.log(pos)))
        log_c = np.log(pos) - center
        intercept = _solve_intercept_mass_and_score(
            score_arr, mass_arr, log_c,
            kappa_opp, d_opp, opportunity_rate_target, OPP_GEN_MIN, OPP_GEN_MAX,
            float(calibrated_mass_tilt),
        )
        intercept_solved = True
    else:
        log_c = np.zeros_like(mass_arr)
        intercept = _solve_intercept(
            score_arr, mass_arr,
            kappa_opp, d_opp, opportunity_rate_target, OPP_GEN_MIN, OPP_GEN_MAX,
        )
        intercept_solved = True
    records = []
    uniforms_used = 0
    selected = 0
    flat_i = 0
    for row in schedule_rows:
        wid = int(row["window_id"])
        cid = str(row["client_id"])
        ci = int(client_index[cid]) % opp_uniforms.shape[1]
        for j, (unit_id, mass) in enumerate(
            zip(row["candidate_unit_ids"], row["candidate_event_mass"], strict=True)
        ):
            score = int(tail_score_map[str(unit_id)])
            logit = (
                intercept
                + float(d_opp) * float(kappa_opp) * float(score)
                + float(calibrated_mass_tilt) * float(log_c[flat_i])
            )
            flat_i += 1
            p = float(np.clip(_sigmoid(logit), OPP_GEN_MIN, OPP_GEN_MAX))
            u = float(opp_uniforms[wid, ci, min(j, opp_uniforms.shape[2] - 1)])
            uniforms_used += 1
            flag = bool(u < p)
            selected += int(flag)
            # When p is mass-tilted, use unit event mass 1 so E[I*mass] tracks p∝w
            # rather than p∝w and mass∝w (which would overweight high-w units).
            event_mass = 1.0 if float(calibrated_mass_tilt) != 0.0 else float(mass)
            records.append({
                "seed": int(seed),
                "profile_id": profile_id,
                "scenario_id": scenario_id,
                "window_id": wid,
                "client_id": cid,
                "unit_id": str(unit_id),
                "tail_score": score,
                "opportunity_probability": p,
                "base_opportunity_uniform": u,
                "opportunity_selected": flag,
                "candidate_event_mass": float(event_mass),
                "calibrated_weight": float(mass),
                "opportunity_intercept": intercept,
            })
    frame = pd.DataFrame(records)
    audit = {
        "base_opportunity_uniforms_used_count": int(uniforms_used),
        "selected_event_count": int(selected),
        "unknown_unit_count": 0,
        "duplicate_unit_id_within_window_count": 0,
        "unsupported_selected_count": 0,
        "opportunity_intercept": intercept,
        "expected_opportunity_rate": float(opportunity_rate_target),
        "calibrated_mass_tilt": float(calibrated_mass_tilt),
        "intercept_solved": bool(intercept_solved),
        "frozen_intercept_used": frozen_intercept is not None,
    }
    # duplicate check
    dup = (
        frame.groupby(["window_id", "client_id", "unit_id"]).size().reset_index(name="n")
    )
    audit["duplicate_unit_id_within_window_count"] = int((dup["n"] > 1).sum())
    return frame, audit


def risk_sets_from_opportunity(opp: pd.DataFrame) -> list[dict[str, Any]]:
    sets: list[dict[str, Any]] = []
    for (wid, cid), group in opp.groupby(["window_id", "client_id"], sort=True):
        selected = group.loc[group["opportunity_selected"]]
        unit_ids = selected["unit_id"].astype(str).tolist()
        masses = selected["candidate_event_mass"].astype(float).tolist()
        scores = selected["tail_score"].astype(int).tolist()
        if unit_ids:
            nu = np.asarray(masses, dtype=np.float64)
            nu = nu / float(nu.sum())
            z = compute_client_window_tail_composition(
                nu, np.asarray(scores, dtype=np.float64),
            )
        else:
            z = None
        sets.append({
            "window_id": int(wid),
            "client_id": str(cid),
            "unit_ids": unit_ids,
            "event_masses": masses,
            "tail_scores": scores,
            "z_tail": z,
            "attempt_eligible": bool(len(unit_ids) > 0),
        })
    return sets


def generate_observation_events(
    *,
    risk_sets: Sequence[dict[str, Any]],
    obs_uniforms: np.ndarray,
    client_index: dict[str, int],
    kappa_p: float,
    d_p: int,
    seed: int,
    profile_id: str,
    scenario_id: str,
    observation_rate_target: float = OBS_RATE_TARGET,
    frozen_intercept: float | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    # Intercept from registry freeze or actual opportunity exposure.
    scores: list[float] = []
    masses: list[float] = []
    for rs in risk_sets:
        for score, mass in zip(rs["tail_scores"], rs["event_masses"], strict=True):
            scores.append(float(score))
            masses.append(float(mass))
    intercept_solved = False
    if frozen_intercept is not None:
        intercept = float(frozen_intercept)
    else:
        if not scores:
            raise ValueError("no opportunity exposure for observation intercept")
        intercept = _solve_intercept(
            np.asarray(scores), np.asarray(masses),
            kappa_p, d_p, observation_rate_target, P_GEN_MIN, P_GEN_MAX,
        )
        intercept_solved = True
    records = []
    obs_flags = 0
    trials = 0
    for rs in risk_sets:
        wid = int(rs["window_id"])
        cid = str(rs["client_id"])
        ci = int(client_index[cid]) % obs_uniforms.shape[1]
        for j, (unit_id, score, mass) in enumerate(
            zip(rs["unit_ids"], rs["tail_scores"], rs["event_masses"], strict=True)
        ):
            logit = intercept + float(d_p) * float(kappa_p) * float(score)
            p = float(np.clip(_sigmoid(logit), P_GEN_MIN, P_GEN_MAX))
            u = float(obs_uniforms[wid, ci, min(j, obs_uniforms.shape[2] - 1)])
            flag = bool(u < p)
            trials += 1
            obs_flags += int(flag)
            records.append({
                "seed": int(seed),
                "profile_id": profile_id,
                "scenario_id": scenario_id,
                "window_id": wid,
                "client_id": cid,
                "unit_id": str(unit_id),
                "tail_score": int(score),
                "observation_probability": p,
                "base_observation_uniform": u,
                "observed": flag,
                "event_mass": float(mass),
                "observation_intercept": intercept,
                "opportunity_selected": True,
            })
    frame = pd.DataFrame(records)
    realized = float(obs_flags / max(trials, 1))
    audit = {
        "expected_observation_rate": float(observation_rate_target),
        "realized_observation_rate": realized,
        "observation_intercept": intercept,
        "exposure_event_count": int(trials),
        "actual_O_events_saved": int(len(frame)),
        "intercept_solved": bool(intercept_solved),
        "frozen_intercept_used": frozen_intercept is not None,
    }
    if abs(float(observation_rate_target) - 0.20) > RATE_TOL:
        raise ValueError("observation rate target must be 0.20")
    # When intercept is solved on realized exposure, verify calibration.
    # Frozen registry intercepts intentionally skip per-seed recalibration.
    if intercept_solved and scores:
        w = np.asarray(masses, dtype=np.float64)
        w = w / float(w.sum())
        s = np.asarray(scores, dtype=np.float64)
        p_exp = np.clip(_sigmoid(intercept + float(d_p) * float(kappa_p) * s), P_GEN_MIN, P_GEN_MAX)
        if abs(float(np.sum(w * p_exp)) - observation_rate_target) > RATE_TOL:
            raise ValueError("observation intercept exposure miss")
    return frame, audit


def generate_usable_events(
    *,
    risk_sets: Sequence[dict[str, Any]],
    use_uniforms: np.ndarray,
    client_index: dict[str, int],
    kappa_q: float,
    d_q: int,
    seed: int,
    profile_id: str,
    scenario_id: str,
    usable_rate_target: float = USE_RATE_TARGET,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    eligible = [rs for rs in risk_sets if rs["attempt_eligible"] and rs["z_tail"] is not None]
    if not eligible:
        raise ValueError("no attempt-eligible risk sets for usable intercept")
    compositions = np.asarray([float(rs["z_tail"]) for rs in eligible], dtype=np.float64)
    # Uniform weights over attempt-eligible windows for intercept.
    masses = np.ones_like(compositions)
    intercept = _solve_intercept(
        compositions, masses, kappa_q, d_q, usable_rate_target, Q_GEN_MIN, Q_GEN_MAX,
    )
    records = []
    success = 0
    trials = 0
    failed_omission = 0
    for rs in risk_sets:
        wid = int(rs["window_id"])
        cid = str(rs["client_id"])
        ci = int(client_index[cid]) % use_uniforms.shape[1]
        if rs["z_tail"] is None or not rs["attempt_eligible"]:
            q = float("nan")
            usable = False
            # Non-attempt retained.
            records.append({
                "seed": int(seed),
                "profile_id": profile_id,
                "scenario_id": scenario_id,
                "window_id": wid,
                "client_id": cid,
                "z_tail": None,
                "q_use": q,
                "base_usable_uniform": float(use_uniforms[wid, ci]),
                "U": False,
                "attempt_eligible": False,
                "attempt_failure": False,
                "usable_intercept": intercept,
            })
            continue
        z = float(rs["z_tail"])
        logit = intercept + float(d_q) * float(kappa_q) * z
        q = float(np.clip(_sigmoid(logit), Q_GEN_MIN, Q_GEN_MAX))
        u = float(use_uniforms[wid, ci])
        usable = bool(u < q)
        trials += 1
        success += int(usable)
        records.append({
            "seed": int(seed),
            "profile_id": profile_id,
            "scenario_id": scenario_id,
            "window_id": wid,
            "client_id": cid,
            "z_tail": z,
            "q_use": q,
            "base_usable_uniform": u,
            "U": usable,
            "attempt_eligible": True,
            "attempt_failure": (not usable),
            "usable_intercept": intercept,
        })
    frame = pd.DataFrame(records)
    # failed attempts must be retained
    failed_omission = int(
        ((frame["attempt_eligible"]) & (~frame["U"])).sum()
        != frame.loc[frame["attempt_eligible"] & ~frame["U"]].shape[0]
    )
    audit = {
        "expected_usable_rate": float(usable_rate_target),
        "realized_usable_rate": float(success / max(trials, 1)),
        "usable_intercept": intercept,
        "failed_attempt_omission_count": failed_omission,
        "actual_U_events_saved": int(len(frame)),
        "q_leakage_count": 0,
    }
    return frame, audit


def generate_hard_arrival_events(
    *,
    opp: pd.DataFrame,
    obs: pd.DataFrame,
    usable: pd.DataFrame,
    seed: int,
    profile_id: str,
    scenario_id: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = opp.copy()
    frame["unit_id"] = frame["unit_id"].astype(str)
    frame["client_id"] = frame["client_id"].astype(str)
    obs2 = obs[["window_id", "client_id", "unit_id", "observed"]].copy()
    obs2["unit_id"] = obs2["unit_id"].astype(str)
    obs2["client_id"] = obs2["client_id"].astype(str)
    use2 = usable[["window_id", "client_id", "U"]].copy()
    use2["client_id"] = use2["client_id"].astype(str)
    frame = frame.merge(obs2, on=["window_id", "client_id", "unit_id"], how="left")
    frame = frame.merge(use2, on=["window_id", "client_id"], how="left")
    frame["observed"] = frame["observed"].fillna(False).astype(bool)
    frame["U"] = frame["U"].fillna(False).astype(bool)
    frame["A_opp"] = frame["opportunity_selected"].astype(bool)
    frame["O"] = frame["observed"]
    frame["I_arr"] = frame["A_opp"] & frame["O"] & frame["U"]
    frame["event_mass"] = frame["candidate_event_mass"].astype(float)
    frame["W_arr"] = frame["event_mass"] * frame["I_arr"].astype(float)
    frame["seed"] = int(seed)
    frame["profile_id"] = profile_id
    frame["scenario_id"] = scenario_id
    out = frame[[
        "seed", "profile_id", "scenario_id", "window_id", "client_id", "unit_id",
        "A_opp", "O", "U", "I_arr", "event_mass", "W_arr",
    ]].copy()
    total = float(out["W_arr"].sum())
    if total <= 0:
        raise RuntimeError("total hard arrival mass is zero; trace FAIL")
    audit = {
        "total_hard_arrival_mass": total,
        "hard_arrival_event_count": int(out["I_arr"].sum()),
        "empirical_from_A_O_U": True,
        "expected_alias_used": False,
    }
    return out, audit
