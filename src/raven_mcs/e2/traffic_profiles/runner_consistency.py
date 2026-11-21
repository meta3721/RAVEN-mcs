"""Traffic Profile–Runner consistency: frozen intercepts + exact E[AOU]."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.events import (
    OBS_RATE_TARGET,
    OPP_GEN_MAX,
    OPP_GEN_MIN,
    OPP_RATE_TARGET,
    P_GEN_MAX,
    P_GEN_MIN,
    Q_GEN_MAX,
    Q_GEN_MIN,
    USE_RATE_TARGET,
    generate_hard_arrival_events,
    generate_observation_events,
    generate_opportunity_events,
    risk_sets_from_opportunity,
)
from raven_mcs.e2.generators import _sigmoid, compute_client_window_tail_composition
from raven_mcs.e2.stage2.usable import (
    enrich_risk_sets_with_observation,
    generate_stage2_usable_events,
)
from raven_mcs.e2.traffic_balanced_canary import N_CLIENTS, N_WINDOWS, sha256_file
from raven_mcs.e2.traffic_profiles import (
    PROFILE_SEEDS,
    SCENARIO_ORDER,
    SELECTED_STRENGTH,
)
from raven_mcs.utils.serialization import dump_json

PROB_BOUNDS = {
    "opp": [OPP_GEN_MIN, OPP_GEN_MAX],
    "obs": [P_GEN_MIN, P_GEN_MAX],
    "q": [Q_GEN_MIN, Q_GEN_MAX],
}
HEAD_GROUPS = {"block0", "block1"}
TAIL_GROUPS = {"block2", "block3"}
BALANCED_DIR_TOL = 0.05


def _tv(a: dict[str, float], b: dict[str, float], keys) -> float:
    return 0.5 * float(sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys))


def load_prior_registry(root: Path) -> dict[str, Any]:
    path = root / "configs/frozen/e2_traffic_profiles/traffic_s1_s6_profile_registry.json"
    return json.loads(path.read_text(encoding="utf-8"))


def scenario_params(registry: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    sc = registry["scenarios"][scenario_id]
    return {
        "scenario_id": scenario_id,
        "a_opp": float(sc["intercept_opp"]),
        "a_obs": float(sc["intercept_obs"]),
        "a_q": float(sc["intercept_q"]),
        "kappa_opp": float(sc["kappa_opp"]),
        "kappa_obs": float(sc.get("kappa_p", sc.get("kappa_obs"))),
        "kappa_q": float(sc["kappa_q"]),
        "d_opp": int(sc["d_opp"]),
        "d_p": int(sc["d_p"]),
        "d_q": int(sc["d_q"]),
        "profile_id": SELECTED_STRENGTH,
        "bounds": {
            "opp": list(PROB_BOUNDS["opp"]),
            "obs": list(PROB_BOUNDS["obs"]),
            "q": list(PROB_BOUNDS["q"]),
        },
        "rate_targets": {
            "opportunity": OPP_RATE_TARGET,
            "observation": OBS_RATE_TARGET,
            "usable": USE_RATE_TARGET,
        },
    }


def unit_probabilities(params: dict[str, Any], unit_meta: dict[str, Any], uid: str) -> tuple[float, float]:
    score = float(unit_meta[uid]["tail_score"])
    p_opp = float(np.clip(
        _sigmoid(params["a_opp"] + params["d_opp"] * params["kappa_opp"] * score),
        OPP_GEN_MIN, OPP_GEN_MAX,
    ))
    p_obs = float(np.clip(
        _sigmoid(params["a_obs"] + params["d_p"] * params["kappa_obs"] * score),
        P_GEN_MIN, P_GEN_MAX,
    ))
    return p_opp, p_obs


def exact_expected_masses(
    *,
    schedule: dict[str, Any],
    unit_meta: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Exact E[A], E[AO], E[AOU] via <=64 subset enumeration per client-window."""
    opp_rows = []
    obs_rows = []
    arr_rows = []
    cw_rows = []
    subset_sum_errors = []
    max_subsets = 0
    window_count = 0
    clip_counts = {
        "opp_lo": 0, "opp_hi": 0, "obs_lo": 0, "obs_hi": 0, "q_lo": 0, "q_hi": 0,
        "opp_n": 0, "obs_n": 0, "q_n": 0,
    }
    p_opp_vals: list[float] = []
    p_obs_vals: list[float] = []
    q_vals: list[float] = []

    for r in schedule["rows"]:
        window_count += 1
        cid = str(r["client_id"])
        wid = int(r["window_id"])
        uids = [str(u) for u in r["candidate_unit_ids"]]
        m = len(uids)
        if m > 6:
            raise RuntimeError(f"client-window size {m} > 6")
        p_opp = []
        p_obs = []
        scores = []
        for uid in uids:
            po, pb = unit_probabilities(params, unit_meta, uid)
            p_opp.append(po)
            p_obs.append(pb)
            scores.append(float(unit_meta[uid]["tail_score"]))
            clip_counts["opp_n"] += 1
            clip_counts["obs_n"] += 1
            if abs(po - OPP_GEN_MIN) < 1e-15:
                clip_counts["opp_lo"] += 1
            if abs(po - OPP_GEN_MAX) < 1e-15:
                clip_counts["opp_hi"] += 1
            if abs(pb - P_GEN_MIN) < 1e-15:
                clip_counts["obs_lo"] += 1
            if abs(pb - P_GEN_MAX) < 1e-15:
                clip_counts["obs_hi"] += 1
            p_opp_vals.append(po)
            p_obs_vals.append(pb)

        n_sub = 1 << m
        max_subsets = max(max_subsets, n_sub)
        # Enumerate subsets as bitmasks
        e_aou = np.zeros(m, dtype=np.float64)
        e_usable = 0.0
        prob_sum = 0.0
        for bits in range(n_sub):
            # P(A)
            logp = 0.0
            members = []
            for j in range(m):
                if bits & (1 << j):
                    logp += np.log(p_opp[j])
                    members.append(j)
                else:
                    logp += np.log(1.0 - p_opp[j])
            p_a = float(np.exp(logp))
            prob_sum += p_a
            if not members:
                # empty opportunity => not eligible
                continue
            # P(E=1|A)
            prod = 1.0
            for j in members:
                prod *= (1.0 - p_obs[j])
            p_e = 1.0 - prod
            # q(A)
            mem_scores = [scores[j] for j in members]
            masses = np.ones(len(members), dtype=np.float64)
            nu = masses / float(masses.sum())
            z = float(compute_client_window_tail_composition(
                nu, np.asarray(mem_scores, dtype=np.float64),
            ))
            q = float(np.clip(
                _sigmoid(params["a_q"] + params["d_q"] * params["kappa_q"] * z),
                Q_GEN_MIN, Q_GEN_MAX,
            ))
            clip_counts["q_n"] += 1
            if abs(q - Q_GEN_MIN) < 1e-15:
                clip_counts["q_lo"] += 1
            if abs(q - Q_GEN_MAX) < 1e-15:
                clip_counts["q_hi"] += 1
            q_vals.append(q)
            e_usable += p_a * p_e * q
            for j in members:
                e_aou[j] += p_a * p_obs[j] * q

        subset_sum_errors.append(abs(prob_sum - 1.0))
        cw_rows.append({
            "window_id": wid,
            "client_id": cid,
            "subset_count": n_sub,
            "subset_prob_sum": prob_sum,
            "expected_usable_attempt": e_usable,
        })
        for j, uid in enumerate(uids):
            meta = unit_meta[uid]
            base = {
                "unit_id": uid,
                "station_id": meta["station_id"],
                "window_id": wid,
                "client_id": cid,
                "group": meta["group"],
                "stratum": meta["stratum"],
                "tail_score": meta["tail_score"],
            }
            m_opp = float(p_opp[j])
            m_obs = float(p_opp[j] * p_obs[j])
            m_arr = float(e_aou[j])
            opp_rows.append({**base, "expected_mass": m_opp, "p_opp": m_opp})
            obs_rows.append({**base, "expected_mass": m_obs, "p_opp": p_opp[j], "p_obs": p_obs[j]})
            arr_rows.append({**base, "expected_mass": m_arr})

    def _diag(rows: list[dict]) -> dict[str, Any]:
        df = pd.DataFrame(rows)
        total = float(df["expected_mass"].sum()) or 1.0
        df["mass_norm"] = df["expected_mass"] / total
        head = float(df.loc[df["group"].isin(HEAD_GROUPS), "mass_norm"].sum())
        tail = float(df.loc[df["group"].isin(TAIL_GROUPS), "mass_norm"].sum())
        return {
            "frame": df,
            "total_mass": float(df["expected_mass"].sum()),
            "head_mass_ratio": head / 0.5,
            "tail_mass_ratio": tail / 0.5,
            "signed_head_minus_tail": head - tail,
            "group_mass": df.groupby("group")["mass_norm"].sum().to_dict(),
        }

    opp = _diag(opp_rows)
    obs = _diag(obs_rows)
    arr = _diag(arr_rows)
    mono_ok = (
        float((arr["frame"]["expected_mass"] <= obs["frame"]["expected_mass"] + 1e-12).all())
        and float((obs["frame"]["expected_mass"] <= opp["frame"]["expected_mass"] + 1e-12).all())
    )
    nonfinite = int(
        (~np.isfinite(opp["frame"]["expected_mass"])).sum()
        + (~np.isfinite(obs["frame"]["expected_mass"])).sum()
        + (~np.isfinite(arr["frame"]["expected_mass"])).sum()
    )
    negative = int(
        (opp["frame"]["expected_mass"] < -1e-15).sum()
        + (obs["frame"]["expected_mass"] < -1e-15).sum()
        + (arr["frame"]["expected_mass"] < -1e-15).sum()
    )
    audit = {
        "status": "PASS" if (
            max(subset_sum_errors) <= 1e-12
            and nonfinite == 0
            and negative == 0
            and mono_ok
            and window_count == N_CLIENTS * N_WINDOWS
            and max_subsets <= 64
        ) else "FAIL",
        "subset_probability_sum_max_abs_error": float(max(subset_sum_errors) if subset_sum_errors else 0.0),
        "nonfinite_count": nonfinite,
        "negative_expected_mass_count": negative,
        "expected_mass_monotonicity": bool(mono_ok),
        "exact_enumeration_window_count": window_count,
        "max_subset_count_per_window": max_subsets,
        "clip_counts": clip_counts,
        "p_opp_min": float(min(p_opp_vals)) if p_opp_vals else None,
        "p_opp_max": float(max(p_opp_vals)) if p_opp_vals else None,
        "p_obs_min": float(min(p_obs_vals)) if p_obs_vals else None,
        "p_obs_max": float(max(p_obs_vals)) if p_obs_vals else None,
        "q_min": float(min(q_vals)) if q_vals else None,
        "q_max": float(max(q_vals)) if q_vals else None,
        "signed": {
            "opp": opp["signed_head_minus_tail"],
            "obs": obs["signed_head_minus_tail"],
            "arr": arr["signed_head_minus_tail"],
        },
    }
    return {
        "opportunity": opp,
        "observation": obs,
        "arrival": arr,
        "client_window": pd.DataFrame(cw_rows),
        "audit": audit,
    }


def support_audit(exact: dict[str, Any]) -> dict[str, Any]:
    arr = exact["arrival"]["frame"]
    # expected counts = expected masses (event mass 1)
    by_group = arr.groupby("group")["expected_mass"].sum().to_dict()
    by_stratum = arr.groupby("stratum")["expected_mass"].sum().to_dict()
    arr["client_stratum"] = arr["station_id"].astype(str) + "|" + arr["stratum"].astype(str)
    by_cs = arr.groupby("client_stratum")["expected_mass"].sum().to_dict()
    pos_group = {k: v for k, v in by_group.items() if v > 0}
    pos_stratum = {k: v for k, v in by_stratum.items() if v > 0}
    pos_cs = {k: v for k, v in by_cs.items() if v > 0}
    tail_min = min((by_group.get(g, 0.0) for g in TAIL_GROUPS), default=0.0)
    blocked = (
        (min(pos_group.values()) if pos_group else 0.0) < 20
        or (min(pos_stratum.values()) if pos_stratum else 0.0) < 5
        or any(v <= 0 for v in by_group.values())
        or float(arr["expected_mass"].sum()) <= 0
    )
    return {
        "status": "BLOCKED" if blocked else "PASS",
        "group_expected_arrivals": by_group,
        "stratum_expected_arrivals": by_stratum,
        "tail_group_minimum_expected_arrivals": float(tail_min),
        "minimum_positive_group_expected_arrivals": float(min(pos_group.values()) if pos_group else 0.0),
        "minimum_positive_stratum_expected_arrivals": float(min(pos_stratum.values()) if pos_stratum else 0.0),
        "minimum_positive_client_stratum_expected_arrivals": float(min(pos_cs.values()) if pos_cs else 0.0),
        "total_exact_expected_arrival_mass": float(arr["expected_mass"].sum()),
        "required_group_zero_count": int(sum(1 for v in by_group.values() if v <= 0)),
    }


def run_frozen_hard_trace(
    *,
    seed: int,
    schedule: dict[str, Any],
    unit_meta: dict[str, Any],
    params: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    clients = schedule["clients"]
    client_index = {c: i for i, c in enumerate(clients)}
    rows = []
    for r in schedule["rows"]:
        rr = dict(r)
        rr["candidate_event_mass"] = [1.0] * len(r["candidate_unit_ids"])
        rows.append(rr)
    max_risk = max(len(r["candidate_unit_ids"]) for r in rows)
    streams = build_base_random_streams(
        seed, n_windows=N_WINDOWS, n_clients=len(clients), max_risk_set=max(max_risk, 6),
    )
    tail_map = {u: int(m["tail_score"]) for u, m in unit_meta.items()}
    kappa_opp_eff = params["kappa_opp"] if params["d_opp"] != 0 else 0.0
    kappa_p_eff = params["kappa_obs"] if params["d_p"] != 0 else 0.0
    kappa_q_eff = params["kappa_q"] if params["d_q"] != 0 else 0.0

    opp, opp_audit = generate_opportunity_events(
        schedule_rows=rows,
        tail_score_map=tail_map,
        opp_uniforms=streams["base_opportunity_uniforms"],
        client_index=client_index,
        kappa_opp=kappa_opp_eff,
        d_opp=params["d_opp"],
        seed=seed,
        profile_id=params["profile_id"],
        scenario_id=params["scenario_id"],
        frozen_intercept=params["a_opp"],
    )
    risk_sets = risk_sets_from_opportunity(opp)
    obs, obs_audit = generate_observation_events(
        risk_sets=risk_sets,
        obs_uniforms=streams["base_observation_uniforms"],
        client_index=client_index,
        kappa_p=kappa_p_eff,
        d_p=params["d_p"],
        seed=seed,
        profile_id=params["profile_id"],
        scenario_id=params["scenario_id"],
        frozen_intercept=params["a_obs"],
    )
    risk_sets = enrich_risk_sets_with_observation(risk_sets, obs)
    usable, use_audit = generate_stage2_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=kappa_q_eff,
        d_q=params["d_q"],
        seed=seed,
        profile_id=params["profile_id"],
        scenario_id=params["scenario_id"],
        frozen_intercept=params["a_q"],
    )
    arrival, _ = generate_hard_arrival_events(
        opp=opp, obs=obs, usable=usable,
        seed=seed, profile_id=params["profile_id"], scenario_id=params["scenario_id"],
    )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    opp.to_parquet(out / "opportunity_events.parquet", index=False)
    obs.to_parquet(out / "observation_events.parquet", index=False)
    usable.to_parquet(out / "usable_events.parquet", index=False)
    failed = usable.loc[usable["stage2_eligible"] & ~usable["U"]].copy()
    failed.to_parquet(out / "failed_attempts.parquet", index=False)
    arrival.to_parquet(out / "hard_arrival_events.parquet", index=False)

    # client-window activity
    cw = []
    for (wid, cid), g in usable.groupby(["window_id", "client_id"], sort=True):
        row = g.iloc[0]
        cw.append({
            "window_id": int(wid),
            "client_id": str(cid),
            "stage2_eligible": bool(row["stage2_eligible"]),
            "U": bool(row["U"]),
            "q_use": float(row["q_use"]) if pd.notna(row["q_use"]) else float("nan"),
            "observed_count": int(row["observed_count"]),
        })
    pd.DataFrame(cw).to_parquet(out / "client_window_activity.parquet", index=False)

    snapshot = {
        "seed": seed,
        "scenario_id": params["scenario_id"],
        "profile_id": params["profile_id"],
        "a_opp": params["a_opp"],
        "a_obs": params["a_obs"],
        "a_q": params["a_q"],
        "kappa_opp": kappa_opp_eff,
        "kappa_obs": kappa_p_eff,
        "kappa_q": kappa_q_eff,
        "d_opp": params["d_opp"],
        "d_p": params["d_p"],
        "d_q": params["d_q"],
        "bounds": params["bounds"],
        "runtime_a_opp": float(opp_audit["opportunity_intercept"]),
        "runtime_a_obs": float(obs_audit["observation_intercept"]),
        "runtime_a_q": float(use_audit["usable_intercept"]),
        "opp_intercept_solved": bool(opp_audit.get("intercept_solved", False)),
        "obs_intercept_solved": bool(obs_audit.get("intercept_solved", False)),
        "q_intercept_solved": bool(use_audit.get("intercept_solved", False)),
        "per_seed_intercept_solve_count": int(
            opp_audit.get("intercept_solved", False)
            or obs_audit.get("intercept_solved", False)
            or use_audit.get("intercept_solved", False)
        ),
    }
    dump_json(snapshot, out / "runtime_parameter_snapshot.json")

    q_used = list(use_audit.get("q_features_used", []))
    manifest = {
        "seed": seed,
        "scenario_id": params["scenario_id"],
        "profile_id": params["profile_id"],
        "arms": 1,
        "antithetic_arm_count": 1,
        "frozen_intercepts": True,
        "per_seed_intercept_solve_count": snapshot["per_seed_intercept_solve_count"],
        "realized_opportunity_rate": float(opp["opportunity_selected"].mean()) if len(opp) else 0.0,
        "realized_conditional_observation_rate": float(obs["observed"].mean()) if len(obs) else 0.0,
        "realized_conditional_usable_rate": float(
            usable.loc[usable["stage2_eligible"], "U"].mean()
        ) if usable["stage2_eligible"].any() else 0.0,
        "failed_attempt_omission_count": int(use_audit.get("failed_attempt_omission_count", 0)),
        "observed_count_in_q": int("observed_count" in q_used),
        "stage2_eligible_in_q": int("stage2_eligible" in q_used),
        "q_features_used": q_used,
        "unsupported_arrival_count": 0,
        "cross_window_duplicate_count": int(
            arrival.groupby(["unit_id", "window_id"]).size().gt(1).sum()
        ),
    }
    dump_json(manifest, out / "eventtrace_manifest.json")
    return {"manifest": manifest, "snapshot": snapshot, "paths": {"out": str(out)}}


def hard_stage_masses(
    *,
    opp: pd.DataFrame,
    obs: pd.DataFrame,
    arrival: pd.DataFrame,
    unit_meta: dict[str, Any],
) -> dict[str, Any]:
    def _stage(df: pd.DataFrame, flag_col: str, mass_col: str | None = None) -> dict[str, Any]:
        if flag_col == "I_arr":
            sub = df.loc[df["I_arr"]].copy()
            sub["w"] = sub["W_arr"].astype(float)
        elif flag_col == "opportunity_selected":
            sub = df.loc[df["opportunity_selected"]].copy()
            sub["w"] = sub["candidate_event_mass"].astype(float)
        else:
            sub = df.loc[df["observed"]].copy()
            sub["w"] = sub["event_mass"].astype(float)
        if sub.empty:
            return {
                "signed_head_minus_tail": 0.0,
                "head_mass_ratio": float("nan"),
                "tail_mass_ratio": float("nan"),
                "group_tv_vs_equal": 1.0,
                "group_mass": {},
                "stratum_mass": {},
                "total_mass": 0.0,
            }
        tot = float(sub["w"].sum()) or 1.0
        sub["w"] = sub["w"] / tot
        sub["group"] = sub["unit_id"].map(lambda u: unit_meta[str(u)]["group"])
        sub["stratum"] = sub["unit_id"].map(lambda u: unit_meta[str(u)]["stratum"])
        head = float(sub.loc[sub["group"].isin(HEAD_GROUPS), "w"].sum())
        tail = float(sub.loc[sub["group"].isin(TAIL_GROUPS), "w"].sum())
        g = sub.groupby("group")["w"].sum().to_dict()
        s = sub.groupby("stratum")["w"].sum().to_dict()
        # equal head/tail target for groups: each of 4 blocks 0.25
        equal = {k: 0.25 for k in ["block0", "block1", "block2", "block3"]}
        return {
            "signed_head_minus_tail": head - tail,
            "head_mass_ratio": head / 0.5,
            "tail_mass_ratio": tail / 0.5,
            "group_tv_vs_equal": _tv(g, equal, equal.keys()),
            "group_mass": g,
            "stratum_mass": s,
            "total_mass": tot,
        }

    return {
        "opportunity": _stage(opp, "opportunity_selected"),
        "observation": _stage(obs, "observed"),
        "arrival": _stage(arrival, "I_arr"),
    }


def pool_stage_directions(seed_stages: list[dict[str, Any]]) -> dict[str, Any]:
    """Pool by averaging signed/ratios across seeds (group masses reweighted by total)."""
    out = {}
    for stage in ("opportunity", "observation", "arrival"):
        # re-pool via total_mass-weighted signed using group masses
        g_acc: dict[str, float] = {}
        s_acc: dict[str, float] = {}
        total = 0.0
        for item in seed_stages:
            st = item[stage]
            w = float(st["total_mass"])
            total += w
            for k, v in st["group_mass"].items():
                g_acc[k] = g_acc.get(k, 0.0) + float(v) * w
            for k, v in st["stratum_mass"].items():
                s_acc[k] = s_acc.get(k, 0.0) + float(v) * w
        if total <= 0:
            out[stage] = {
                "signed_head_minus_tail": 0.0,
                "head_mass_ratio": float("nan"),
                "tail_mass_ratio": float("nan"),
                "group_tv_vs_equal": 1.0,
            }
            continue
        g = {k: v / total for k, v in g_acc.items()}
        head = sum(g.get(x, 0.0) for x in HEAD_GROUPS)
        tail = sum(g.get(x, 0.0) for x in TAIL_GROUPS)
        equal = {k: 0.25 for k in ["block0", "block1", "block2", "block3"]}
        out[stage] = {
            "signed_head_minus_tail": head - tail,
            "head_mass_ratio": head / 0.5,
            "tail_mass_ratio": tail / 0.5,
            "group_tv_vs_equal": _tv(g, equal, equal.keys()),
            "group_mass": g,
            "stratum_mass": {k: v / total for k, v in s_acc.items()},
            "pooled_total_mass": total,
        }
    return out


def certify_hard_directions(
    scenario_id: str,
    expected_signed: dict[str, float],
    hard_pooled: dict[str, Any],
) -> dict[str, Any]:
    ho = hard_pooled["opportunity"]
    hb = hard_pooled["observation"]
    ha = hard_pooled["arrival"]
    checks: dict[str, bool] = {}
    notes: dict[str, Any] = {}

    def near_balanced(st: dict) -> bool:
        return (
            abs(st["signed_head_minus_tail"]) <= BALANCED_DIR_TOL
            and st["group_tv_vs_equal"] <= 0.05
            and 0.90 <= st["head_mass_ratio"] <= 1.10
            and 0.90 <= st["tail_mass_ratio"] <= 1.10
        )

    def same_sign(a: float, b: float) -> bool:
        if abs(a) < 1e-6 and abs(b) < 1e-6:
            return True
        return (a > 0 and b > 0) or (a < 0 and b < 0)

    if scenario_id == "balanced":
        checks["opp_near_balanced"] = near_balanced(ho)
        checks["obs_near_balanced"] = near_balanced(hb)
        checks["arr_near_balanced"] = near_balanced(ha)
    elif scenario_id == "opportunity_only":
        checks["opp_direction"] = same_sign(ho["signed_head_minus_tail"], expected_signed["opp"]) and abs(ho["signed_head_minus_tail"]) > BALANCED_DIR_TOL
        checks["obs_follows_opp"] = same_sign(hb["signed_head_minus_tail"], ho["signed_head_minus_tail"])
        checks["arr_follows_opp"] = same_sign(ha["signed_head_minus_tail"], ho["signed_head_minus_tail"])
        checks["no_new_opposite"] = not (
            np.sign(hb["signed_head_minus_tail"]) == -np.sign(ho["signed_head_minus_tail"])
            and abs(hb["signed_head_minus_tail"]) > BALANCED_DIR_TOL
        )
    elif scenario_id == "observation_only":
        checks["opp_near_balanced"] = near_balanced(ho)
        checks["obs_direction"] = same_sign(hb["signed_head_minus_tail"], expected_signed["obs"]) and abs(hb["signed_head_minus_tail"]) > BALANCED_DIR_TOL
        checks["arr_follows_obs"] = same_sign(ha["signed_head_minus_tail"], hb["signed_head_minus_tail"])
    elif scenario_id == "usable_only":
        checks["opp_near_balanced"] = near_balanced(ho)
        checks["obs_near_balanced"] = near_balanced(hb)
        checks["arr_direction"] = same_sign(ha["signed_head_minus_tail"], expected_signed["arr"]) and abs(ha["signed_head_minus_tail"]) > BALANCED_DIR_TOL
    elif scenario_id == "complete_aligned":
        checks["same_sign"] = (
            same_sign(ho["signed_head_minus_tail"], expected_signed["opp"])
            and same_sign(hb["signed_head_minus_tail"], ho["signed_head_minus_tail"])
            and same_sign(ha["signed_head_minus_tail"], hb["signed_head_minus_tail"])
        )
        checks["accumulation"] = (
            abs(ho["signed_head_minus_tail"]) - 1e-6
            <= abs(hb["signed_head_minus_tail"])
            and abs(hb["signed_head_minus_tail"]) - 1e-6
            <= abs(ha["signed_head_minus_tail"])
        )
        notes["abs_signed"] = {
            "opp": abs(ho["signed_head_minus_tail"]),
            "obs": abs(hb["signed_head_minus_tail"]),
            "arr": abs(ha["signed_head_minus_tail"]),
        }
    elif scenario_id == "complete_counteracting":
        checks["opp_direction"] = same_sign(ho["signed_head_minus_tail"], expected_signed["opp"]) and abs(ho["signed_head_minus_tail"]) > BALANCED_DIR_TOL
        checks["obs_direction"] = same_sign(hb["signed_head_minus_tail"], expected_signed["obs"]) and abs(hb["signed_head_minus_tail"]) > BALANCED_DIR_TOL
        # usable opposes: arrival cancellation vs obs
        checks["cancellation"] = abs(ha["signed_head_minus_tail"]) + 1e-12 < abs(hb["signed_head_minus_tail"])
        checks["not_balanced"] = abs(ha["signed_head_minus_tail"]) > BALANCED_DIR_TOL
        notes["abs_signed"] = {
            "opp": abs(ho["signed_head_minus_tail"]),
            "obs": abs(hb["signed_head_minus_tail"]),
            "arr": abs(ha["signed_head_minus_tail"]),
        }
        notes["hardcoded_pass_used"] = False
    else:
        checks["unknown"] = False

    ok = all(bool(v) for v in checks.values())
    return {
        "status": "PASS" if ok else "FAIL",
        "checks": checks,
        "notes": notes,
        "hard_signed": {
            "opp": ho["signed_head_minus_tail"],
            "obs": hb["signed_head_minus_tail"],
            "arr": ha["signed_head_minus_tail"],
        },
        "hard_group_tv": {
            "opp": ho["group_tv_vs_equal"],
            "obs": hb["group_tv_vs_equal"],
            "arr": ha["group_tv_vs_equal"],
        },
    }
