"""Generate one hard empirical validation mother trace."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.events import (
    generate_hard_arrival_events,
    generate_observation_events,
    generate_opportunity_events,
    generate_usable_events,
    risk_sets_from_opportunity,
)
from raven_mcs.e2.empirical.mass import (
    expected_atomic_mass_from_exposure,
    hard_empirical_atomic_mass,
    mass_diagnostics,
)
from raven_mcs.e2.empirical.schedule import build_continuous_schedule, schedule_frame
from raven_mcs.e2.identity import (
    load_e1_atomic_target_weights,
    load_e1_head_tail_mapping,
    load_e1_target_identity,
)
from raven_mcs.e2.scenario_generator import (
    load_scenario_direction_registry,
    load_strength_profile_registry,
)
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
PARENT_COMMIT = "e56687813f2bcb919a9208391f68a4db3488602e"
ARRIVAL_MASS_MODE = "event_mass"  # frozen; not profile-dependent


def _load_unit_maps(root: Path) -> dict[str, Any]:
    atomic = load_e1_atomic_target_weights(root)
    head_tail = load_e1_head_tail_mapping(root)
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

    # Stratum for empirical gates = frozen head/tail/neutral role identity.
    # Finer SensorScope opportunity strata remain too sparse for 300-window hard events.
    roles = ht.loc[unit_ids, "role"].astype(str).tolist()
    unique_strata = ["head", "neutral", "tail"]
    stratum_index = {s: i for i, s in enumerate(unique_strata)}
    stratum_ids = np.asarray(
        [stratum_index.get(r, stratum_index["neutral"]) for r in roles],
        dtype=np.int64,
    )
    target_stratum = np.zeros(len(unique_strata), dtype=np.float64)
    for i in range(len(unique_strata)):
        target_stratum[i] = float(target[stratum_ids == i].sum())
    total_s = float(target_stratum.sum())
    if total_s <= 0:
        raise RuntimeError("target stratum mass sum must be positive")
    target_stratum = target_stratum / total_s
    return {
        "unit_ids": unit_ids,
        "target": target,
        "scores": scores,
        "tail_score_map": {u: int(s) for u, s in zip(unit_ids, scores, strict=True)},
        "group_ids": group_ids,
        "target_group": target_group,
        "stratum_ids": stratum_ids,
        "target_stratum": target_stratum,
        "supported_set": set(unit_ids),
    }


def generate_empirical_mother_trace(
    *,
    seed: int,
    profile_id: str,
    scenario_id: str,
    root: Path | None = None,
    output_dir: Path | None = None,
    streams: dict[str, Any] | None = None,
    schedule: dict[str, Any] | None = None,
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
    # Opportunity always uses kappa when d_opp != 0; balanced uses rate-only.
    kappa_opp_eff = kappa_opp if d_opp != 0 else 0.0

    if streams is None:
        streams = build_base_random_streams(
            seed, n_windows=300, n_clients=8, max_risk_set=20,
        )
    if schedule is None:
        schedule = build_continuous_schedule(
            seed, schedule_uniforms=streams["base_client_window_schedule"], root=root,
        )
    clients = schedule["clients"]
    client_index = {c: i for i, c in enumerate(clients)}

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
    # Unsupported selected check
    unsupported = (~opp["unit_id"].astype(str).isin(maps["supported_set"])) & opp[
        "opportunity_selected"
    ]
    opp_audit["unsupported_selected_count"] = int(unsupported.sum())
    if opp_audit["unsupported_selected_count"] > 0:
        raise RuntimeError("unsupported units selected into opportunity risk set")

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
    usable, use_audit = generate_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=kappa_q_eff,
        d_q=d_q,
        seed=seed,
        profile_id=profile_id,
        scenario_id=scenario_id,
    )
    arrival, arr_audit = generate_hard_arrival_events(
        opp=opp, obs=obs, usable=usable,
        seed=seed, profile_id=profile_id, scenario_id=scenario_id,
    )

    # Observation empirical mass for cancellation diagnostics.
    obs_mass = np.zeros(len(maps["unit_ids"]), dtype=np.float64)
    index = {u: i for i, u in enumerate(maps["unit_ids"])}
    for row in obs.itertuples(index=False):
        if bool(row.observed):
            obs_mass[index[str(row.unit_id)]] += float(row.event_mass)
    if float(obs_mass.sum()) > 0:
        obs_mass = obs_mass / float(obs_mass.sum())
    else:
        obs_mass = maps["target"].copy()

    diagnostics: dict[int, dict[str, Any]] = {}
    emp_by_len: dict[int, np.ndarray] = {}
    exp_by_len: dict[int, np.ndarray] = {}
    for length in (100, 200, 300):
        emp = hard_empirical_atomic_mass(arrival, maps["unit_ids"], length)
        exp = expected_atomic_mass_from_exposure(
            unit_ids=maps["unit_ids"], opp=opp, obs=obs, usable=usable, max_window=length,
        )
        if emp is exp or np.shares_memory(emp, exp):
            raise RuntimeError("empirical arrival aliases expected arrival in memory")
        # Force distinct arrays
        emp = np.array(emp, copy=True)
        exp = np.array(exp, copy=True)
        emp_by_len[length] = emp
        exp_by_len[length] = exp
        # Rates on prefix
        obs_sub = obs.loc[obs["window_id"].astype(int) < length]
        use_sub = usable.loc[
            (usable["window_id"].astype(int) < length) & (usable["attempt_eligible"])
        ]
        realized_obs = float(obs_sub["observed"].mean()) if len(obs_sub) else 0.0
        realized_use = float(use_sub["U"].mean()) if len(use_sub) else 0.0
        active = float(use_sub["U"].mean()) if len(use_sub) else 0.0
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
            active_window_rate=active,
            unsupported_arrival_count=0,
            failed_attempt_omission_count=int(use_audit["failed_attempt_omission_count"]),
            q_leakage_count=int(use_audit["q_leakage_count"]),
            total_hard_arrival_mass=float(
                arrival.loc[arrival["window_id"] < length, "W_arr"].sum()
            ),
        )
        diag["windows"] = int(length)
        diag["empirical_payload_hash"] = sha256_json(emp.tolist())
        diag["expected_payload_hash"] = sha256_json(exp.tolist())
        if diag["empirical_payload_hash"] == diag["expected_payload_hash"]:
            # Extremely unlikely for hard vs soft; still forbid forced equality path.
            diag["hashes_equal_warning"] = True
        else:
            diag["hashes_equal_warning"] = False
        diagnostics[length] = diag

    # Balanced vs opportunity risk-set difference for shared seed/profile streams.
    identity = load_e1_target_identity(root)
    manifest = {
        "seed": int(seed),
        "profile_id": profile_id,
        "scenario_id": scenario_id,
        "windows": 300,
        "arrival_mass_mode": ARRIVAL_MASS_MODE,
        "base_random_stream_hash": streams["base_random_stream_hash"],
        "schedule_hash": schedule["schedule_hash"],
        "schedule_uniforms_used_count": schedule["audit"]["schedule_uniforms_used_count"],
        "opportunity_uniforms_used_count": opp_audit["base_opportunity_uniforms_used_count"],
        "target_weight_hash": identity["atomic_target_weight_hash"],
        "supported_test_hash": identity["supported_test_unit_hash"],
        "head_tail_mapping_hash": identity["head_tail_mapping_hash"],
        "parent_soft_round_commit": PARENT_COMMIT,
        "generator_source_hash": sha256_file(
            root / "src/raven_mcs/e2/empirical/sampler.py"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "formal": False,
        "performance_claim": False,
        "model_training": False,
        "rmse_computed": False,
        "opp_audit": opp_audit,
        "obs_audit": obs_audit,
        "use_audit": use_audit,
        "arr_audit": arr_audit,
        "schedule_audit": schedule["audit"],
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
                "arrival_mass_mode": ARRIVAL_MASS_MODE,
                "kappas": {
                    "kappa_opp": kappa_opp_eff,
                    "kappa_p": kappa_p_eff,
                    "kappa_q": kappa_q_eff,
                },
                "directions": {"d_opp": d_opp, "d_p": d_p, "d_q": d_q},
                "formal": False,
            }, sort_keys=False),
            encoding="utf-8",
        )
        schedule_frame(schedule).to_parquet(out / "continuous_schedule.parquet", index=False)
        opp.to_parquet(out / "opportunity_events.parquet", index=False)
        obs.to_parquet(out / "observation_events.parquet", index=False)
        usable.to_parquet(out / "usable_events.parquet", index=False)
        arrival.to_parquet(out / "hard_arrival_events.parquet", index=False)
        for length in (100, 200, 300):
            pd.DataFrame({
                "unit_id": maps["unit_ids"],
                "empirical_arrival_mass": emp_by_len[length],
            }).to_parquet(out / f"empirical_atomic_mass_{length}.parquet", index=False)
            pd.DataFrame({
                "unit_id": maps["unit_ids"],
                "expected_arrival_mass": exp_by_len[length],
            }).to_parquet(out / f"expected_atomic_mass_{length}.parquet", index=False)
            dump_json(diagnostics[length], out / f"group_mass_diagnostics_{length}.json")
            dump_json({
                "D_TV_stratum": diagnostics[length]["D_TV_stratum"],
                "D_TV_stratum_exp_emp": diagnostics[length]["D_TV_stratum_exp_emp"],
                "windows": length,
            }, out / f"stratum_mass_diagnostics_{length}.json")
        (out / "stdout.log").write_text(
            f"empirical mother trace seed={seed} profile={profile_id} scenario={scenario_id}\n",
            encoding="utf-8",
        )
        (out / "stderr.log").write_text("", encoding="utf-8")

    return {
        "manifest": manifest,
        "diagnostics": diagnostics,
        "emp_by_len": emp_by_len,
        "exp_by_len": exp_by_len,
        "opp_audit": opp_audit,
        "schedule_audit": schedule["audit"],
        "opportunity_selected_set": set(
            zip(
                opp.loc[opp["opportunity_selected"], "window_id"].astype(int),
                opp.loc[opp["opportunity_selected"], "client_id"].astype(str),
                opp.loc[opp["opportunity_selected"], "unit_id"].astype(str),
            )
        ),
    }
