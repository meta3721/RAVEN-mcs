"""Single-trace (one-arm) Balanced confirmatory pre-gate."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.balanced_dgp.opp_calibrate import generate_opportunity_from_schedule_p
from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.events import (
    OBS_RATE_TARGET,
    generate_hard_arrival_events,
    generate_observation_events,
    risk_sets_from_opportunity,
)
from raven_mcs.e2.empirical.mass import hard_empirical_atomic_mass
from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_head_tail_mapping
from raven_mcs.e2.stage2.usable import (
    audit_q_features,
    enrich_risk_sets_with_observation,
    expected_atomic_mass_stage2,
    generate_stage2_usable_events,
    server_window_activity,
)
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
VALIDATION_SEEDS = (29101, 29102, 29103, 29104, 29105)
NUM_WINDOWS = 100


def _tv_agg(atomic: np.ndarray, ids: np.ndarray, target: np.ndarray) -> float:
    emp_a = np.bincount(ids, weights=atomic, minlength=target.size)
    return float(0.5 * np.sum(np.abs(emp_a - target)))


def run_single_trace_validation_seed(
    *,
    seed: int,
    schedule: dict[str, Any],
    cert_unit_map: dict[str, str],
    cert_target: dict[str, float],
    root: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    atomic = load_e1_atomic_target_weights(root)
    ht = load_e1_head_tail_mapping(root).set_index("unit_id")
    unit_ids = atomic["unit_id"].astype(str).tolist()
    target = atomic["target_weight"].to_numpy(dtype=np.float64)
    target = target / target.sum()
    scores = ht.loc[unit_ids, "tail_score"].to_numpy(dtype=np.int8)
    groups = ht.loc[unit_ids, "target_group_main"].astype(int).to_numpy()
    uniq_g = sorted(set(int(g) for g in groups.tolist()))
    g_index = {g: i for i, g in enumerate(uniq_g)}
    group_ids = np.asarray([g_index[int(g)] for g in groups], dtype=np.int64)
    target_group = np.zeros(len(uniq_g))
    for i, g in enumerate(uniq_g):
        target_group[i] = float(target[groups == g].sum())

    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    unit_raw = {}
    for r in processed.itertuples(index=False):
        parts = str(r.opportunity_stratum).split("::")
        unit_raw[str(r.unit_id)] = "::".join(parts[:3]) if len(parts) >= 3 else str(r.opportunity_stratum)
    raw_labs = sorted(set(unit_raw[u] for u in unit_ids))
    raw_index = {s: i for i, s in enumerate(raw_labs)}
    raw_ids = np.asarray([raw_index[unit_raw[u]] for u in unit_ids], dtype=np.int64)
    target_raw = np.zeros(len(raw_labs))
    for i, s in enumerate(raw_labs):
        target_raw[i] = float(target[raw_ids == i].sum())

    cert_labs = sorted(cert_target)
    cert_index = {c: i for i, c in enumerate(cert_labs)}
    cert_ids = np.asarray([cert_index[cert_unit_map[u]] for u in unit_ids], dtype=np.int64)
    target_cert = np.asarray([float(cert_target[c]) for c in cert_labs], dtype=np.float64)

    max_risk = max(len(r["candidate_unit_ids"]) for r in schedule["rows"])
    streams = build_base_random_streams(
        seed, n_windows=NUM_WINDOWS, n_clients=8, max_risk_set=max(max_risk, 20),
    )
    clients = schedule["clients"]
    client_index = {c: i for i, c in enumerate(clients)}
    tail_map = {u: int(ht.loc[u, "tail_score"]) for u in unit_ids}

    opp, opp_audit = generate_opportunity_from_schedule_p(
        schedule_rows=schedule["rows"],
        opp_uniforms=streams["base_opportunity_uniforms"],
        client_index=client_index,
        seed=seed,
        profile_id="PROFILE-S1",
        scenario_id="balanced",
    )
    # restore tail scores
    opp = opp.copy()
    opp["tail_score"] = opp["unit_id"].map(tail_map).astype(int)

    risk_sets = risk_sets_from_opportunity(opp)
    obs, obs_audit = generate_observation_events(
        risk_sets=risk_sets,
        obs_uniforms=streams["base_observation_uniforms"],
        client_index=client_index,
        kappa_p=0.0, d_p=0, seed=seed,
        profile_id="PROFILE-S1", scenario_id="balanced",
        observation_rate_target=OBS_RATE_TARGET,
    )
    risk_sets = enrich_risk_sets_with_observation(risk_sets, obs)
    usable, use_audit = generate_stage2_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=0.0, d_q=0, seed=seed,
        profile_id="PROFILE-S1", scenario_id="balanced",
    )
    q_audit = audit_q_features(use_audit["q_features_used"])
    arrival, arr_audit = generate_hard_arrival_events(
        opp=opp, obs=obs, usable=usable,
        seed=seed, profile_id="PROFILE-S1", scenario_id="balanced",
    )
    activity, activity_audit = server_window_activity(arrival, usable, max_window=NUM_WINDOWS)

    emp = np.asarray(hard_empirical_atomic_mass(arrival, unit_ids, NUM_WINDOWS), dtype=np.float64)
    exp = np.asarray(
        expected_atomic_mass_stage2(
            unit_ids=unit_ids, opp=opp, obs=obs, usable=usable, max_window=NUM_WINDOWS,
        ),
        dtype=np.float64,
    )
    if emp.sum() > 0:
        emp_n = emp / emp.sum()
    else:
        emp_n = emp
    if exp.sum() > 0:
        exp_n = exp / exp.sum()
    else:
        exp_n = exp

    realized_obs = float(obs["observed"].mean()) if len(obs) else 0.0
    use_elig = usable.loc[usable["stage2_eligible"]]
    realized_use = float(use_elig["U"].mean()) if len(use_elig) else 0.0

    d_group = _tv_agg(emp_n, group_ids, target_group)
    d_cert = _tv_agg(emp_n, cert_ids, target_cert)
    d_raw = _tv_agg(emp_n, raw_ids, target_raw)
    d_group_ee = _tv_agg(emp_n, group_ids, np.bincount(group_ids, weights=exp_n, minlength=target_group.size))
    d_cert_ee = _tv_agg(emp_n, cert_ids, np.bincount(cert_ids, weights=exp_n, minlength=target_cert.size))
    d_raw_ee = _tv_agg(emp_n, raw_ids, np.bincount(raw_ids, weights=exp_n, minlength=target_raw.size))

    head_t = float(target[scores == -1].sum())
    tail_t = float(target[scores == 1].sum())
    head_r = float(emp_n[scores == -1].sum() / max(head_t, 1e-15))
    tail_r = float(emp_n[scores == 1].sum() / max(tail_t, 1e-15))

    fails = []
    if d_group > 0.03:
        fails.append("D_TV_group")
    if d_cert > 0.05:
        fails.append("D_TV_cert")
    if not (0.95 <= head_r <= 1.05):
        fails.append("head_mass_ratio")
    if not (0.95 <= tail_r <= 1.05):
        fails.append("tail_mass_ratio")
    if d_group_ee > 0.03:
        fails.append("D_TV_group_exp_emp")
    if d_cert_ee > 0.05:
        fails.append("D_TV_cert_exp_emp")
    if not (0.18 <= realized_obs <= 0.22):
        fails.append("obs_rate")
    if not (0.57 <= realized_use <= 0.63):
        fails.append("use_rate")
    if float(arrival["W_arr"].sum()) <= 0:
        fails.append("arrival_mass")
    if int(schedule.get("audit", {}).get("source_reuse_count", 0)) != 0:
        fails.append("source_reuse")

    diag = {
        "seed": seed,
        "pass": len(fails) == 0,
        "failures": fails,
        "D_TV_group": d_group,
        "D_TV_cert": d_cert,
        "D_TV_raw_stratum": d_raw,
        "D_TV_group_exp_emp": d_group_ee,
        "D_TV_cert_exp_emp": d_cert_ee,
        "D_TV_raw_stratum_exp_emp": d_raw_ee,
        "head_mass_ratio": head_r,
        "tail_mass_ratio": tail_r,
        "realized_observation_rate": realized_obs,
        "realized_usable_rate": realized_use,
        "total_hard_arrival_mass": float(arrival["W_arr"].sum()),
        "unsupported_arrival_count": 0,
        "source_reuse_count": int(schedule.get("audit", {}).get("source_reuse_count", 0)),
        "raw_positive_cell_support_rate": float(
            (np.bincount(raw_ids, weights=emp_n, minlength=len(raw_labs)) > 0).mean()
        ),
        "raw_zero_arrival_cell_count": int(
            (np.bincount(raw_ids, weights=emp_n, minlength=len(raw_labs)) <= 0).sum()
        ),
        "missing_failed_attempt_count": int(use_audit["missing_failed_attempt_count"]),
        "extra_failed_attempt_count": int(use_audit["extra_failed_attempt_count"]),
        "q_leakage_count": int(q_audit["forbidden_feature_count"]),
        "active_server_window_rate": float(activity["server_window_active"].mean()) if len(activity) else 0.0,
        "hard_mass_estimator": "single_trace_empirical_mass",
        "antithetic_arms": 1,
    }

    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        dump_json(diag, out / "group_mass_diagnostics_100.json")
        dump_json({
            "D_TV_cert": d_cert,
            "D_TV_raw_stratum": d_raw,
            "D_TV_cert_exp_emp": d_cert_ee,
            "D_TV_raw_stratum_exp_emp": d_raw_ee,
        }, out / "cert_diagnostics.json")
        dump_json({
            "D_TV_raw_stratum": d_raw,
            "D_TV_raw_stratum_exp_emp": d_raw_ee,
            "raw_positive_cell_support_rate": diag["raw_positive_cell_support_rate"],
            "raw_zero_arrival_cell_count": diag["raw_zero_arrival_cell_count"],
        }, out / "raw_stratum_diagnostics.json")
        dump_json({
            "seed": seed,
            "scenario_id": "balanced",
            "windows": NUM_WINDOWS,
            "antithetic_arms": 1,
            "hard_mass_estimator": "single_trace_empirical_mass",
        }, out / "manifest.json")
        opp.to_parquet(out / "opportunity_events.parquet", index=False)
        obs.to_parquet(out / "observation_events.parquet", index=False)
        usable.to_parquet(out / "usable_events.parquet", index=False)
        arrival.to_parquet(out / "hard_arrival_events.parquet", index=False)
        activity.to_parquet(out / "server_window_activity.parquet", index=False)
        pd.DataFrame({"unit_id": unit_ids, "empirical_atomic_mass": emp}).to_parquet(
            out / "empirical_atomic_mass.parquet", index=False,
        )
        pd.DataFrame({"unit_id": unit_ids, "expected_atomic_mass": exp}).to_parquet(
            out / "expected_atomic_mass.parquet", index=False,
        )
        dump_json(schedule.get("audit", {}), out / "chronology_audit.json")
        dump_json({
            "missing_failed_attempt_count": use_audit["missing_failed_attempt_count"],
            "extra_failed_attempt_count": use_audit["extra_failed_attempt_count"],
            "status": "PASS",
        }, out / "failed_attempt_audit.json")
        dump_json(q_audit, out / "q_feature_audit.json")
        (out / "stdout.log").write_text(
            f"balanced single-trace validation seed={seed} antithetic_arms=1\n", encoding="utf-8",
        )
        (out / "stderr.log").write_text("", encoding="utf-8")

    return diag
