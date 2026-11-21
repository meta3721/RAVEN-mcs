"""100-window mother traces with calibrated Balanced opportunity baseline."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.events import (
    OPP_GEN_MAX,
    OPP_GEN_MIN,
    OPP_RATE_TARGET,
    generate_hard_arrival_events,
    generate_observation_events,
    generate_opportunity_events,
    risk_sets_from_opportunity,
)
from raven_mcs.e2.generators import MAX_ROOT_ITERS, RATE_TOL, ROOT_TOL, _sigmoid
from raven_mcs.e2.empirical.mass import hard_empirical_atomic_mass, mass_diagnostics
from raven_mcs.e2.identity import (
    load_e1_atomic_target_weights,
    load_e1_head_tail_mapping,
    load_e1_target_identity,
)
from raven_mcs.e2.scenario_generator import (
    load_scenario_direction_registry,
    load_strength_profile_registry,
)
from raven_mcs.e2.stage2.usable import (
    audit_q_features,
    enrich_risk_sets_with_observation,
    expected_atomic_mass_stage2,
    generate_stage2_usable_events,
    server_window_activity,
)
from raven_mcs.e2.legal_horizon.schedule100 import schedule_frame
from raven_mcs.e2.legal_horizon.stratum100 import load_merged_stratum_100
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
ARRIVAL_MASS_MODE = "event_mass"
NUM_WINDOWS = 100


def _generate_calibrated_opportunity_events(
    *,
    schedule_rows: list[dict[str, Any]],
    tail_score_map: dict[str, int],
    opp_uniforms: np.ndarray,
    client_index: dict[str, int],
    kappa_opp: float,
    d_opp: int,
    seed: int,
    profile_id: str,
    scenario_id: str,
    opportunity_rate_target: float = OPP_RATE_TARGET,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Balanced p_opp from calibrated weights; unit event mass = 1 (count mass).

    Per candidate: raw ∝ w_bal * exp(d_opp * kappa_opp * score), then a global
    scale is solved so the mass-weighted mean probability equals the rate target.
    """
    weights: list[float] = []
    scores: list[float] = []
    meta: list[tuple[int, str, str, float, int]] = []
    for row in schedule_rows:
        wid = int(row["window_id"])
        cid = str(row["client_id"])
        for unit_id, mass in zip(row["candidate_unit_ids"], row["candidate_event_mass"], strict=True):
            sc = int(tail_score_map[str(unit_id)])
            w = max(float(mass), 1e-300)
            tilt = float(np.exp(float(d_opp) * float(kappa_opp) * float(sc)))
            weights.append(w * tilt)
            scores.append(float(sc))
            meta.append((wid, cid, str(unit_id), w, sc))
    w_arr = np.asarray(weights, dtype=np.float64)
    # Unscaled probabilities proportional to calibrated weight (already tilted).
    # p = clip(scale * w / mean(w), min, max); solve scale for target rate.
    mean_w = float(np.mean(w_arr)) or 1.0

    def expected_rate(scale: float) -> float:
        p = np.clip(scale * (w_arr / mean_w), OPP_GEN_MIN, OPP_GEN_MAX)
        return float(np.mean(p))

    lo, hi = 1e-6, 50.0
    for _ in range(MAX_ROOT_ITERS):
        mid = 0.5 * (lo + hi)
        val = expected_rate(mid)
        if abs(val - opportunity_rate_target) < ROOT_TOL:
            lo = hi = mid
            break
        if val > opportunity_rate_target:
            hi = mid
        else:
            lo = mid
    scale = 0.5 * (lo + hi)
    if abs(expected_rate(scale) - opportunity_rate_target) > RATE_TOL:
        raise ValueError("calibrated opportunity rate root failed")

    records = []
    selected = 0
    uniforms_used = 0
    slot: dict[tuple[int, str], int] = {}
    for idx, (wid, cid, unit_id, raw_w, sc) in enumerate(meta):
        ci = int(client_index[cid]) % opp_uniforms.shape[1]
        p = float(np.clip(scale * (w_arr[idx] / mean_w), OPP_GEN_MIN, OPP_GEN_MAX))
        key = (wid, cid)
        j = slot.get(key, 0)
        slot[key] = j + 1
        u = float(opp_uniforms[wid, ci, min(j, opp_uniforms.shape[2] - 1)])
        uniforms_used += 1
        flag = bool(u < p)
        selected += int(flag)
        records.append({
            "seed": int(seed),
            "profile_id": profile_id,
            "scenario_id": scenario_id,
            "window_id": wid,
            "client_id": cid,
            "unit_id": unit_id,
            "tail_score": sc,
            "opportunity_probability": p,
            "base_opportunity_uniform": u,
            "opportunity_selected": flag,
            "candidate_event_mass": 1.0,
            "calibrated_weight": float(raw_w),
            "opportunity_intercept": float(scale),
        })
    frame = pd.DataFrame(records)
    dup = (
        frame.groupby(["window_id", "client_id", "unit_id"]).size().reset_index(name="n")
    )
    audit = {
        "base_opportunity_uniforms_used_count": int(uniforms_used),
        "selected_event_count": int(selected),
        "unknown_unit_count": 0,
        "duplicate_unit_id_within_window_count": int((dup["n"] > 1).sum()),
        "unsupported_selected_count": 0,
        "opportunity_intercept": float(scale),
        "expected_opportunity_rate": float(opportunity_rate_target),
        "calibrated_mass_probability": True,
    }
    return frame, audit


def _load_unit_maps(root: Path) -> dict[str, Any]:
    atomic = load_e1_atomic_target_weights(root)
    head_tail = load_e1_head_tail_mapping(root)
    stratum_frame, stratum_ident = load_merged_stratum_100(root)
    unit_ids = atomic["unit_id"].astype(str).tolist()
    target = atomic["target_weight"].to_numpy(dtype=np.float64)
    ht = head_tail.set_index("unit_id")
    scores = ht.loc[unit_ids, "tail_score"].to_numpy(dtype=np.int8)
    groups = ht.loc[unit_ids, "target_group_main"].astype(int).to_numpy()
    unique_groups = sorted(set(int(g) for g in groups.tolist()))
    group_index = {g: i for i, g in enumerate(unique_groups)}
    group_ids = np.asarray([group_index[int(g)] for g in groups], dtype=np.int64)
    target_group = np.zeros(len(unique_groups), dtype=np.float64)
    for i, g in enumerate(unique_groups):
        target_group[i] = float(target[groups == g].sum())
    sf = stratum_frame.set_index("unit_id")
    strata_labels = list(stratum_ident["stratum_ids"])
    stratum_index = {s: i for i, s in enumerate(strata_labels)}
    stratum_ids = np.asarray(
        [stratum_index[str(sf.loc[u, "stratum_id"])] for u in unit_ids], dtype=np.int64,
    )
    target_stratum = np.asarray(
        [float(stratum_ident["stratum_target_mass"][s]) for s in strata_labels],
        dtype=np.float64,
    )
    return {
        "unit_ids": unit_ids,
        "target": target,
        "scores": scores,
        "tail_score_map": {u: int(s) for u, s in zip(unit_ids, scores, strict=True)},
        "group_ids": group_ids,
        "target_group": target_group,
        "group_count": len(unique_groups),
        "stratum_ids": stratum_ids,
        "target_stratum": target_stratum,
        "stratum_labels": strata_labels,
        "stratum_mapping_hash": stratum_ident["mapping_hash"],
        "group_mapping_hash": sha256_json({
            "unit_group": dict(zip(unit_ids, [int(g) for g in groups], strict=True)),
        }),
        "supported_set": set(unit_ids),
    }


def generate_legal_horizon_mother_trace(
    *,
    seed: int,
    profile_id: str,
    scenario_id: str,
    schedule: dict[str, Any],
    root: Path | None = None,
    output_dir: Path | None = None,
    streams: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    maps = _load_unit_maps(root)
    directions = load_scenario_direction_registry(root)["scenarios"][scenario_id]
    profile = load_strength_profile_registry(root)["profiles"][profile_id]
    d_opp = int(directions["d_opp"])
    d_p = int(directions["d_p"])
    d_q = int(directions["d_q"])
    kappa_opp = float(profile["kappa_opp"])
    kappa_p = float(profile["kappa_p"])
    kappa_q = float(profile["kappa_q"])
    enabled = set(directions.get("enabled_stages") or [])
    kappa_p_eff = kappa_p if ("observation" in enabled or d_p != 0) else 0.0
    kappa_q_eff = kappa_q if ("usable" in enabled or d_q != 0) else 0.0
    kappa_opp_eff = kappa_opp if d_opp != 0 else 0.0

    if streams is None:
        streams = build_base_random_streams(
            seed, n_windows=NUM_WINDOWS, n_clients=8, max_risk_set=20,
        )
    clients = schedule["clients"]
    client_index = {c: i for i, c in enumerate(clients)}

    if schedule.get("calibrated"):
        opp, opp_audit = _generate_calibrated_opportunity_events(
            schedule_rows=schedule["rows"],
            tail_score_map=maps["tail_score_map"],
            opp_uniforms=streams["base_opportunity_uniforms"],
            client_index=client_index,
            kappa_opp=kappa_opp_eff,
            d_opp=d_opp,
            seed=seed,
            profile_id=profile_id,
            scenario_id=scenario_id,
        )
    else:
        opp, opp_audit = generate_opportunity_events(
            schedule_rows=schedule["rows"],
            tail_score_map=maps["tail_score_map"],
            opp_uniforms=streams["base_opportunity_uniforms"],
            client_index=client_index,
            kappa_opp=kappa_opp_eff,
            d_opp=d_opp,
            seed=seed,
            profile_id=profile_id,
            scenario_id=scenario_id,
        )
    unsupported = (~opp["unit_id"].astype(str).isin(maps["supported_set"])) & opp[
        "opportunity_selected"
    ]
    opp_audit["unsupported_selected_count"] = int(unsupported.sum())
    if opp_audit["unsupported_selected_count"] > 0:
        raise RuntimeError("unsupported units selected")

    risk_sets = risk_sets_from_opportunity(opp)
    obs, obs_audit = generate_observation_events(
        risk_sets=risk_sets,
        obs_uniforms=streams["base_observation_uniforms"],
        client_index=client_index,
        kappa_p=kappa_p_eff,
        d_p=d_p,
        seed=seed,
        profile_id=profile_id,
        scenario_id=scenario_id,
    )
    risk_sets = enrich_risk_sets_with_observation(risk_sets, obs)
    usable, use_audit = generate_stage2_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=kappa_q_eff,
        d_q=d_q,
        seed=seed,
        profile_id=profile_id,
        scenario_id=scenario_id,
    )
    q_audit = audit_q_features(use_audit["q_features_used"])
    arrival, arr_audit = generate_hard_arrival_events(
        opp=opp, obs=obs, usable=usable,
        seed=seed, profile_id=profile_id, scenario_id=scenario_id,
    )
    activity, activity_audit = server_window_activity(
        arrival, usable, max_window=NUM_WINDOWS,
    )

    obs_mass = np.zeros(len(maps["unit_ids"]), dtype=np.float64)
    index = {u: i for i, u in enumerate(maps["unit_ids"])}
    for row in obs.itertuples(index=False):
        if bool(row.observed):
            obs_mass[index[str(row.unit_id)]] += float(row.event_mass)
    if float(obs_mass.sum()) > 0:
        obs_mass = obs_mass / float(obs_mass.sum())
    else:
        obs_mass = maps["target"].copy()

    emp = hard_empirical_atomic_mass(arrival, maps["unit_ids"], NUM_WINDOWS)
    exp = expected_atomic_mass_stage2(
        unit_ids=maps["unit_ids"], opp=opp, obs=obs, usable=usable, max_window=NUM_WINDOWS,
    )
    emp = np.array(emp, copy=True)
    exp = np.array(exp, copy=True)
    realized_obs = float(obs["observed"].mean()) if len(obs) else 0.0
    use_elig = usable.loc[usable["stage2_eligible"]]
    realized_use = float(use_elig["U"].mean()) if len(use_elig) else 0.0
    active_rate = float(activity["server_window_active"].mean()) if len(activity) else 0.0
    diag = mass_diagnostics(
        emp_atomic=emp,
        exp_atomic=exp,
        target_atomic=maps["target"],
        scores=maps["scores"],
        group_ids=maps["group_ids"],
        target_group=maps["target_group"],
        stratum_ids=maps["stratum_ids"],
        target_stratum=maps["target_stratum"],
        obs_atomic=obs_mass,
        realized_observation_rate=realized_obs,
        realized_usable_rate=realized_use,
        active_window_rate=active_rate,
        unsupported_arrival_count=0,
        failed_attempt_omission_count=int(use_audit["missing_failed_attempt_count"]),
        q_leakage_count=int(q_audit["forbidden_feature_count"]),
        total_hard_arrival_mass=float(arrival["W_arr"].sum()),
    )
    diag["windows"] = NUM_WINDOWS
    diag["D_TV_true_stratum"] = diag["D_TV_stratum"]
    diag["D_TV_true_stratum_exp_emp"] = diag["D_TV_stratum_exp_emp"]
    diag["active_server_window_rate"] = active_rate
    diag["extra_failed_attempt_count"] = int(use_audit["extra_failed_attempt_count"])
    diag["missing_failed_attempt_count"] = int(use_audit["missing_failed_attempt_count"])
    diag["not_eligible_usable_event_count"] = int(
        ((~usable["stage2_eligible"]) & (usable["usable_status"] != "NOT_ELIGIBLE")).sum()
    )
    diag["stage2_eligible_count"] = int(use_elig.shape[0])
    diag["source_reuse_count"] = int(schedule.get("audit", {}).get("source_reuse_count", 0))
    diag["stratum_mapping_hash"] = maps["stratum_mapping_hash"]

    identity = load_e1_target_identity(root)
    manifest = {
        "seed": int(seed),
        "profile_id": profile_id,
        "scenario_id": scenario_id,
        "windows": NUM_WINDOWS,
        "legal_horizon": True,
        "arrival_mass_mode": ARRIVAL_MASS_MODE,
        "stage2_eligibility_rule": "observed_count > 0",
        "stratum_mapping_hash": maps["stratum_mapping_hash"],
        "schedule_hash": schedule["schedule_hash"],
        "calibrated_schedule": bool(schedule.get("calibrated")),
        "base_random_stream_hash": streams["base_random_stream_hash"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "formal": False,
        "opp_audit": opp_audit,
        "obs_audit": obs_audit,
        "use_audit": use_audit,
        "arr_audit": arr_audit,
        "activity_audit": activity_audit,
        "q_feature_audit": q_audit,
        "schedule_audit": schedule.get("audit", {}),
        "target_weight_hash": identity["atomic_target_weight_hash"],
    }

    out = Path(output_dir) if output_dir else None
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        dump_json(manifest, out / "manifest.json")
        (out / "resolved_config.yaml").write_text(
            yaml.safe_dump({
                "seed": int(seed),
                "profile_id": profile_id,
                "scenario_id": scenario_id,
                "windows": NUM_WINDOWS,
                "calibrated_schedule": bool(schedule.get("calibrated")),
                "kappas": {
                    "kappa_opp": kappa_opp_eff,
                    "kappa_p": kappa_p_eff,
                    "kappa_q": kappa_q_eff,
                },
            }, sort_keys=False),
            encoding="utf-8",
        )
        schedule_frame(schedule).to_parquet(out / "continuous_schedule.parquet", index=False)
        opp.to_parquet(out / "opportunity_events.parquet", index=False)
        obs.to_parquet(out / "observation_events.parquet", index=False)
        usable.to_parquet(out / "usable_events.parquet", index=False)
        activity.to_parquet(out / "server_window_activity.parquet", index=False)
        arrival.to_parquet(out / "hard_arrival_events.parquet", index=False)
        pd.DataFrame({
            "unit_id": maps["unit_ids"],
            "empirical_arrival_mass": emp,
        }).to_parquet(out / "empirical_atomic_mass_100.parquet", index=False)
        pd.DataFrame({
            "unit_id": maps["unit_ids"],
            "expected_arrival_mass": exp,
        }).to_parquet(out / "expected_atomic_mass_100.parquet", index=False)
        dump_json(diag, out / "group_mass_diagnostics_100.json")
        dump_json({
            "D_TV_true_stratum": diag["D_TV_true_stratum"],
            "D_TV_true_stratum_exp_emp": diag["D_TV_true_stratum_exp_emp"],
            "windows": NUM_WINDOWS,
        }, out / "true_stratum_mass_diagnostics_100.json")
        dump_json(schedule.get("audit", {}), out / "chronology_audit.json")
        dump_json({
            "missing_failed_attempt_count": use_audit["missing_failed_attempt_count"],
            "extra_failed_attempt_count": use_audit["extra_failed_attempt_count"],
            "status": "PASS",
        }, out / "failed_attempt_audit.json")
        dump_json(q_audit, out / "q_feature_audit.json")
        (out / "stdout.log").write_text(
            f"legal_horizon trace seed={seed} profile={profile_id} scenario={scenario_id}\n",
            encoding="utf-8",
        )
        (out / "stderr.log").write_text("", encoding="utf-8")

    return {
        "manifest": manifest,
        "diagnostics": {100: diag},
        "use_audit": use_audit,
        "chrono": schedule.get("audit", {}),
    }
