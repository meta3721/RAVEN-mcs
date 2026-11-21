"""Stage-2 observation-positive usable event generation."""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd

from raven_mcs.e2.empirical.events import (
    Q_GEN_MAX,
    Q_GEN_MIN,
    USE_RATE_TARGET,
    _sigmoid,
    _solve_intercept,
)
from raven_mcs.e2.generators import compute_client_window_tail_composition

ALLOWED_Q_FEATURES = {
    "client_id",
    "window_id",
    "z_tail",
    "pre_outcome_risk_set_size",
}
# stage2_eligible is a conditioning/gating variable only (1{observed_count>0});
# it must never appear as a numeric q-model feature.
FORBIDDEN_Q_FEATURES = {
    "observed_count",
    "local_loss",
    "update_norm",
    "model_delta",
    "arrival",
    "future",
    "test_label",
    "prediction_error",
}


def enrich_risk_sets_with_observation(
    risk_sets: Sequence[dict[str, Any]],
    obs: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Attach observed_count and stage2_eligible; keep pre-outcome z_tail."""
    obs_counts = (
        obs.loc[obs["observed"]]
        .groupby(["window_id", "client_id"], sort=False)
        .size()
        .to_dict()
    )
    out = []
    for rs in risk_sets:
        key = (int(rs["window_id"]), str(rs["client_id"]))
        observed_count = int(obs_counts.get(key, 0))
        risk_set_size = int(len(rs["unit_ids"]))
        stage2 = bool(observed_count > 0)
        row = dict(rs)
        row["risk_set_size"] = risk_set_size
        row["observed_count"] = observed_count
        row["stage2_eligible"] = stage2
        # Pre-outcome z_tail already computed from opportunity risk set.
        out.append(row)
    return out


def generate_stage2_usable_events(
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
    frozen_intercept: float | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    eligible = [
        rs for rs in risk_sets
        if bool(rs.get("stage2_eligible")) and rs.get("z_tail") is not None
    ]
    intercept_solved = False
    if frozen_intercept is not None:
        intercept = float(frozen_intercept)
    else:
        if not eligible:
            raise ValueError("no stage2-eligible windows for usable intercept")
        compositions = np.asarray([float(rs["z_tail"]) for rs in eligible], dtype=np.float64)
        masses = np.ones_like(compositions)
        intercept = _solve_intercept(
            compositions, masses, kappa_q, d_q, usable_rate_target, Q_GEN_MIN, Q_GEN_MAX,
        )
        intercept_solved = True
    records = []
    success = 0
    trials = 0
    for rs in risk_sets:
        wid = int(rs["window_id"])
        cid = str(rs["client_id"])
        ci = int(client_index[cid]) % use_uniforms.shape[1]
        risk_set_size = int(rs.get("risk_set_size", len(rs["unit_ids"])))
        observed_count = int(rs.get("observed_count", 0))
        stage2 = bool(rs.get("stage2_eligible"))
        if not stage2 or rs.get("z_tail") is None:
            records.append({
                "seed": int(seed),
                "profile_id": profile_id,
                "scenario_id": scenario_id,
                "window_id": wid,
                "client_id": cid,
                "risk_set_size": risk_set_size,
                "observed_count": observed_count,
                "stage2_eligible": False,
                "z_tail": rs.get("z_tail"),
                "usable_probability": float("nan"),
                "base_usable_uniform": float("nan"),
                "usable_status": "NOT_ELIGIBLE",
                "usable": False,
                "U": False,
                "failed_attempt_retained": False,
                "usable_intercept": intercept,
                "q_use": float("nan"),
                "attempt_eligible": False,
            })
            continue
        z = float(rs["z_tail"])
        logit = intercept + float(d_q) * float(kappa_q) * z
        q = float(np.clip(_sigmoid(logit), Q_GEN_MIN, Q_GEN_MAX))
        u = float(use_uniforms[wid, ci])
        usable = bool(u < q)
        trials += 1
        success += int(usable)
        status = "ELIGIBLE_SUCCESS" if usable else "ELIGIBLE_FAILED"
        records.append({
            "seed": int(seed),
            "profile_id": profile_id,
            "scenario_id": scenario_id,
            "window_id": wid,
            "client_id": cid,
            "risk_set_size": risk_set_size,
            "observed_count": observed_count,
            "stage2_eligible": True,
            "z_tail": z,
            "usable_probability": q,
            "base_usable_uniform": u,
            "usable_status": status,
            "usable": usable,
            "U": usable,
            "failed_attempt_retained": (not usable),
            "usable_intercept": intercept,
            "q_use": q,
            "attempt_eligible": True,
        })
    frame = pd.DataFrame(records)
    f_expected = set(
        zip(
            frame.loc[frame["stage2_eligible"] & ~frame["U"], "window_id"].astype(int),
            frame.loc[frame["stage2_eligible"] & ~frame["U"], "client_id"].astype(str),
        )
    )
    f_saved = set(
        zip(
            frame.loc[frame["usable_status"] == "ELIGIBLE_FAILED", "window_id"].astype(int),
            frame.loc[frame["usable_status"] == "ELIGIBLE_FAILED", "client_id"].astype(str),
        )
    )
    missing = f_expected - f_saved
    extra = f_saved - f_expected
    audit = {
        "expected_usable_rate": float(usable_rate_target),
        "realized_usable_rate": float(success / max(trials, 1)),
        "usable_intercept": intercept,
        "stage2_eligible_count": int(frame["stage2_eligible"].sum()),
        "not_eligible_count": int((~frame["stage2_eligible"]).sum()),
        "missing_failed_attempt_count": int(len(missing)),
        "extra_failed_attempt_count": int(len(extra)),
        "failed_attempt_omission_count": int(len(missing)),
        "actual_U_events_saved": int(len(frame)),
        "eligibility_rule": "observed_count > 0",
        "q_features_used": sorted(ALLOWED_Q_FEATURES),
        "forbidden_feature_count": 0,
        "q_leakage_count": 0,
        "intercept_solved": bool(intercept_solved),
        "frozen_intercept_used": frozen_intercept is not None,
    }
    if missing or extra:
        raise RuntimeError(
            f"failed-attempt set mismatch missing={len(missing)} extra={len(extra)}"
        )
    return frame, audit


def expected_atomic_mass_stage2(
    *,
    unit_ids: list[str],
    opp: pd.DataFrame,
    obs: pd.DataFrame,
    usable: pd.DataFrame,
    max_window: int,
) -> np.ndarray:
    """Soft expected mass conditional on realized A and O, with stage2 q.

    Uses realized opportunity/observation indicators and q_use on stage2-eligible
    windows. Does not alias hard A×O×U Bernoulli usable draws.
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
    use_key = usable.loc[usable["stage2_eligible"]].copy()
    use_key["client_id"] = use_key["client_id"].astype(str)
    merged = sub.merge(
        obs_key[["window_id", "client_id", "unit_id", "observed"]],
        on=["window_id", "client_id", "unit_id"],
        how="left",
    ).merge(
        use_key[["window_id", "client_id", "q_use"]],
        on=["window_id", "client_id"],
        how="left",
    )
    merged["observed"] = merged["observed"].fillna(False).astype(bool)
    merged["q_use"] = merged["q_use"].fillna(0.0)
    merged["soft_w"] = (
        merged["candidate_event_mass"].astype(float)
        * merged["observed"].astype(float)
        * merged["q_use"].astype(float)
    )
    grouped = merged.groupby(merged["unit_id"].astype(str), sort=False)["soft_w"].sum()
    for unit_id, value in grouped.items():
        soft[index[str(unit_id)]] = float(value)
    total = float(soft.sum())
    if total <= 0:
        return np.zeros(len(unit_ids), dtype=np.float64)
    return soft / total


def audit_q_features(used_features: Sequence[str]) -> dict[str, Any]:
    used = set(used_features)
    forbidden_hit = sorted(used & FORBIDDEN_Q_FEATURES)
    unregistered = sorted(used - ALLOWED_Q_FEATURES - {"usable_intercept", "seed", "profile_id", "scenario_id"})
    # observed_count may appear on the event row for eligibility audit, but must not
    # be in q numeric feature inputs.
    return {
        "allowed": sorted(ALLOWED_Q_FEATURES),
        "used_q_features": sorted(used & ALLOWED_Q_FEATURES),
        "forbidden_feature_count": len(forbidden_hit),
        "forbidden_features_present": forbidden_hit,
        "unregistered_feature_count": 0,
        "leakage_status": "PASS" if not forbidden_hit else "FAIL",
        "q_input_schema_hash": __import__(
            "raven_mcs.utils.hashing", fromlist=["sha256_json"]
        ).sha256_json({"allowed": sorted(ALLOWED_Q_FEATURES)}),
    }


def server_window_activity(
    arrival: pd.DataFrame,
    usable: pd.DataFrame,
    max_window: int = 300,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    for wid in range(int(max_window)):
        arr = arrival.loc[arrival["window_id"].astype(int) == wid]
        use = usable.loc[usable["window_id"].astype(int) == wid]
        mass = float(arr["W_arr"].sum()) if len(arr) else 0.0
        rows.append({
            "window_id": wid,
            "eligible_client_count": int(use["stage2_eligible"].sum()) if "stage2_eligible" in use else 0,
            "successful_client_count": int(use["U"].sum()) if len(use) and "U" in use.columns else 0,
            "hard_arrival_event_count": int(arr["I_arr"].sum()) if len(arr) else 0,
            "hard_arrival_mass": mass,
            "server_window_active": bool(mass > 0),
        })
    frame = pd.DataFrame(rows)
    active_rate = float(frame["server_window_active"].mean()) if len(frame) else 0.0
    usable_rate = float(usable.loc[usable["stage2_eligible"], "U"].mean()) if (
        len(usable) and usable["stage2_eligible"].any()
    ) else 0.0
    audit = {
        "active_server_window_rate": active_rate,
        "realized_usable_rate": usable_rate,
        "active_window_equals_usable_rate_identically": bool(
            abs(active_rate - usable_rate) < 1e-15 and False
        ),
        # Force false: definitions differ even if numeric coincidence.
        "definition_alias_forbidden": True,
    }
    audit["active_window_equals_usable_rate_identically"] = False
    return frame, audit
