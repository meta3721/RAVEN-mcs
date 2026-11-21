"""V0–V3 Balanced hard variance decomposition on audit replicates."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.empirical.events import (
    OBS_RATE_TARGET,
    OPP_GEN_MAX,
    OPP_GEN_MIN,
    OPP_RATE_TARGET,
    USE_RATE_TARGET,
)
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
N_REPS = 200


def _tv(a: np.ndarray, b: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(a - b)))


def _flatten_schedule(
    schedule: dict[str, Any],
    unit_stratum: dict[str, str],
    unit_group: dict[str, int],
    unit_score: dict[str, int],
    unit_index: dict[str, int],
) -> dict[str, Any]:
    cal_w: list[float] = []
    uidx: list[int] = []
    groups: list[int] = []
    scores: list[int] = []
    strata_i: list[int] = []
    wid_cid: list[tuple[int, str]] = []
    stratum_labels = sorted(set(unit_stratum.values()))
    s_index = {s: i for i, s in enumerate(stratum_labels)}
    for r in schedule["rows"]:
        cid = str(r["client_id"])
        wid = int(r["window_id"])
        for uid, mass in zip(r["candidate_unit_ids"], r["candidate_event_mass"], strict=True):
            u = str(uid)
            cal_w.append(max(float(mass), 1e-300))
            uidx.append(unit_index[u])
            groups.append(int(unit_group[u]))
            scores.append(int(unit_score[u]))
            strata_i.append(s_index[unit_stratum[u]])
            wid_cid.append((wid, cid))
    cal_w_arr = np.asarray(cal_w, dtype=np.float64)
    # Constant Balanced probabilities (d=0); calibrated weights ride in event_mass
    # so V0 expected composition matches soft IPF (no p∝w clip distortion).
    p_opp = np.full(len(cal_w_arr), float(np.clip(OPP_RATE_TARGET, OPP_GEN_MIN, OPP_GEN_MAX)))
    p_obs = np.full(len(cal_w_arr), float(OBS_RATE_TARGET))
    p_use = np.full(len(cal_w_arr), float(USE_RATE_TARGET))
    event_mass = cal_w_arr.copy()
    # Map appearance -> client-window id for usable draws
    cw_keys = {}
    cw_id = np.zeros(len(cal_w_arr), dtype=np.int64)
    for i, key in enumerate(wid_cid):
        if key not in cw_keys:
            cw_keys[key] = len(cw_keys)
        cw_id[i] = cw_keys[key]
    return {
        "uidx": np.asarray(uidx, dtype=np.int64),
        "cal_w": cal_w_arr,
        "event_mass": event_mass,
        "group": np.asarray(groups, dtype=np.int64),
        "score": np.asarray(scores, dtype=np.int64),
        "stratum_i": np.asarray(strata_i, dtype=np.int64),
        "cw_id": cw_id,
        "n_cw": len(cw_keys),
        "p_opp": p_opp,
        "p_obs": p_obs,
        "p_use": p_use,
        "stratum_labels": stratum_labels,
        "event_mass_mode": "calibrated_target_weight",
        "expected_arrival_total_mass": float(np.sum(event_mass * p_opp * p_obs * p_use)),
        "expected_arrival_total_count": float(np.sum(p_opp * p_obs * p_use)),
    }


def _metrics_from_atomic(
    atomic: np.ndarray,
    *,
    target_atomic: np.ndarray,
    group_ids_unit: np.ndarray,
    stratum_ids_unit: np.ndarray,
    scores_unit: np.ndarray,
    target_group: np.ndarray,
    target_stratum: np.ndarray,
    cert_levels: dict[str, tuple[np.ndarray, np.ndarray]],
    arrival_count: float,
) -> dict[str, float]:
    if atomic.sum() <= 0:
        atomic = target_atomic.copy()
    else:
        atomic = atomic / atomic.sum()
    emp_g = np.bincount(group_ids_unit, weights=atomic, minlength=target_group.size)
    emp_s = np.bincount(stratum_ids_unit, weights=atomic, minlength=target_stratum.size)
    head_t = float(target_atomic[scores_unit == -1].sum())
    tail_t = float(target_atomic[scores_unit == 1].sum())
    out = {
        "D_TV_group": _tv(emp_g, target_group),
        "D_TV_raw_stratum": _tv(emp_s, target_stratum),
        "head_mass_ratio": float(atomic[scores_unit == -1].sum() / max(head_t, 1e-15)),
        "tail_mass_ratio": float(atomic[scores_unit == 1].sum() / max(tail_t, 1e-15)),
        "total_hard_arrival_count": float(arrival_count),
    }
    for level, (cids, tcert) in cert_levels.items():
        emp_c = np.bincount(cids, weights=atomic, minlength=tcert.size)
        out[f"D_TV_cert_{level}"] = _tv(emp_c, tcert)
        out[f"head_{level}"] = out["head_mass_ratio"]
        out[f"tail_{level}"] = out["tail_mass_ratio"]
    return out


def simulate_all_versions(
    flat: dict[str, Any],
    *,
    rng: np.random.Generator,
    n_units: int,
    target_atomic: np.ndarray,
    group_ids_unit: np.ndarray,
    stratum_ids_unit: np.ndarray,
    scores_unit: np.ndarray,
    target_group: np.ndarray,
    target_stratum: np.ndarray,
    cert_levels: dict[str, tuple[np.ndarray, np.ndarray]],
) -> dict[str, dict[str, float]]:
    n = len(flat["uidx"])
    uidx = flat["uidx"]
    p_opp, p_obs, p_use = flat["p_opp"], flat["p_obs"], flat["p_use"]
    mass = flat["event_mass"]
    exp_w = mass * p_opp * p_obs * p_use

    # Nested Bernoulli + 2-arm antithetic average (same design used in confirmatory validation).
    u_a = rng.random(n)
    u_o = rng.random(n)
    u_use_cw = rng.random(flat["n_cw"])
    flips = [
        (u_a, u_o, u_use_cw),
        (1.0 - u_a, 1.0 - u_o, 1.0 - u_use_cw),
    ]

    def atomic_from(weights: np.ndarray) -> tuple[np.ndarray, float]:
        atomic = np.bincount(uidx, weights=weights, minlength=n_units).astype(np.float64)
        return atomic, float(weights.sum())

    def norm(x: np.ndarray) -> np.ndarray:
        s = x.sum()
        return x / s if s > 0 else x

    def atomic_anti(weight_list: list[np.ndarray]) -> tuple[np.ndarray, float]:
        atoms = [norm(atomic_from(w)[0]) for w in weight_list]
        tots = [atomic_from(w)[1] for w in weight_list]
        return np.mean(np.stack(atoms, axis=0), axis=0), float(np.mean(tots))

    results = {}
    atomic, tot = atomic_from(exp_w)
    results["V0"] = _metrics_from_atomic(
        atomic, target_atomic=target_atomic, group_ids_unit=group_ids_unit,
        stratum_ids_unit=stratum_ids_unit, scores_unit=scores_unit,
        target_group=target_group, target_stratum=target_stratum,
        cert_levels=cert_levels, arrival_count=tot,
    )
    w1s, w2s, w3s = [], [], []
    for ua, uo, uu in flips:
        a = ua < p_opp
        o = uo < p_obs
        use = uu[flat["cw_id"]] < p_use
        w1s.append(mass * a.astype(np.float64) * p_obs * p_use)
        w2s.append(mass * a.astype(np.float64) * o.astype(np.float64) * p_use)
        w3s.append(mass * a.astype(np.float64) * o.astype(np.float64) * use.astype(np.float64))
    for version, wlist in (("V1", w1s), ("V2", w2s), ("V3", w3s)):
        atomic, tot = atomic_anti(wlist)
        results[version] = _metrics_from_atomic(
            atomic, target_atomic=target_atomic, group_ids_unit=group_ids_unit,
            stratum_ids_unit=stratum_ids_unit, scores_unit=scores_unit,
            target_group=target_group, target_stratum=target_stratum,
            cert_levels=cert_levels, arrival_count=tot,
        )
    return results


def run_variance_decomposition(
    *,
    base_schedule: dict[str, Any],
    unit_stratum: dict[str, str],
    unit_group: dict[str, int],
    unit_score: dict[str, int],
    unit_target: dict[str, float],
    unit_cert_maps: dict[str, dict[str, str]],
    root: Path | None = None,
    n_reps: int = N_REPS,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    out_dir = root / "outputs/e2_hard_variance"
    out_dir.mkdir(parents=True, exist_ok=True)

    unit_ids = sorted(unit_target)
    unit_index = {u: i for i, u in enumerate(unit_ids)}
    target_atomic = np.asarray([unit_target[u] for u in unit_ids], dtype=np.float64)
    target_atomic = target_atomic / target_atomic.sum()
    scores_unit = np.asarray([unit_score[u] for u in unit_ids], dtype=np.int64)
    groups_raw = np.asarray([unit_group[u] for u in unit_ids], dtype=np.int64)
    uniq_g = sorted(set(groups_raw.tolist()))
    g_index = {g: i for i, g in enumerate(uniq_g)}
    group_ids_unit = np.asarray([g_index[int(g)] for g in groups_raw], dtype=np.int64)
    target_group = np.zeros(len(uniq_g))
    for i, g in enumerate(uniq_g):
        target_group[i] = float(target_atomic[groups_raw == g].sum())

    strata = sorted(set(unit_stratum[u] for u in unit_ids))
    s_index = {s: i for i, s in enumerate(strata)}
    stratum_ids_unit = np.asarray([s_index[unit_stratum[u]] for u in unit_ids], dtype=np.int64)
    target_stratum = np.zeros(len(strata))
    for i in range(len(strata)):
        target_stratum[i] = float(target_atomic[stratum_ids_unit == i].sum())

    cert_levels: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for level, umap in unit_cert_maps.items():
        labs = sorted(set(umap.values()))
        cidx = {c: i for i, c in enumerate(labs)}
        cids = np.asarray([cidx[umap[u]] for u in unit_ids], dtype=np.int64)
        tcert = np.zeros(len(labs))
        for i in range(len(labs)):
            tcert[i] = float(target_atomic[cids == i].sum())
        # drop zero-mass cells from target by keeping them (mass 0 ok)
        cert_levels[level] = (cids, tcert)

    flat = _flatten_schedule(
        base_schedule, unit_stratum, unit_group, unit_score, unit_index,
    )

    rows = []
    registry = []
    for rep in range(1, n_reps + 1):
        rep_id = f"audit-rep-{rep:04d}"
        registry.append(rep_id)
        seed_int = int.from_bytes(bytes.fromhex(sha256_json({"r": rep_id})[:16]), "big") % (2**32 - 1)
        rng = np.random.default_rng(seed_int)
        vers = simulate_all_versions(
            flat, rng=rng, n_units=len(unit_ids),
            target_atomic=target_atomic, group_ids_unit=group_ids_unit,
            stratum_ids_unit=stratum_ids_unit, scores_unit=scores_unit,
            target_group=target_group, target_stratum=target_stratum,
            cert_levels=cert_levels,
        )
        for version, metrics in vers.items():
            rows.append({"audit_replicate": rep_id, "version": version, **metrics})

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "E2_BALANCED_VARIANCE_DECOMPOSITION_BY_REPLICATE.csv", index=False)

    def summarize(sub: pd.DataFrame, col: str) -> dict[str, float]:
        x = sub[col].astype(float)
        return {
            "mean": float(x.mean()),
            "std": float(x.std(ddof=0)),
            "p50": float(x.quantile(0.50)),
            "p90": float(x.quantile(0.90)),
            "p95": float(x.quantile(0.95)),
            "max": float(x.max()),
        }

    summary: dict[str, Any] = {
        "n_replicates": n_reps,
        "audit_registry_hash": sha256_json(registry),
        "event_mass_mode": "calibrated_target_weight",
        "hard_mass_estimator": "two_arm_antithetic_average_normalized_atomic_mass",
        "expected_arrival_total_design_mass": flat["expected_arrival_total_mass"],
        "expected_arrival_total_design_count": flat["expected_arrival_total_count"],
        "versions": {},
        "incremental_variance": {},
    }
    for version in ("V0", "V1", "V2", "V3"):
        sub = df[df["version"] == version]
        block = {
            "D_TV_group": summarize(sub, "D_TV_group"),
            "D_TV_raw_stratum": summarize(sub, "D_TV_raw_stratum"),
            "head_mass_ratio": summarize(sub, "head_mass_ratio"),
            "tail_mass_ratio": summarize(sub, "tail_mass_ratio"),
            "total_hard_arrival_count": summarize(sub, "total_hard_arrival_count"),
        }
        for level in cert_levels:
            block[f"D_TV_cert_{level}"] = summarize(sub, f"D_TV_cert_{level}")
        summary["versions"][version] = block

    def var_of(version: str, col: str = "D_TV_group") -> float:
        return float(df.loc[df["version"] == version, col].astype(float).var(ddof=0))

    v0, v1, v2, v3 = var_of("V0"), var_of("V1"), var_of("V2"), var_of("V3")
    summary["incremental_variance"] = {
        "opportunity_contribution": max(0.0, v1 - v0),
        "observation_contribution": max(0.0, v2 - v1),
        "usable_contribution": max(0.0, v3 - v2),
        "metric": "Var(D_TV_group)",
    }
    dump_json(summary, out_dir / "E2_BALANCED_VARIANCE_DECOMPOSITION_SUMMARY.json")
    dump_json(
        {"replicates": registry, "hash": summary["audit_registry_hash"]},
        out_dir / "E2_AUDIT_REPLICATE_REGISTRY.json",
    )
    return {
        "summary": summary,
        "frame": df,
        "registry": registry,
        "flat": flat,
        "cert_levels": cert_levels,
    }
