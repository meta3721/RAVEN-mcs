"""Single-arm V0–V3 variance audit (no antithetic selection)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.empirical.events import OBS_RATE_TARGET, USE_RATE_TARGET
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
N_REPS = 200


def _tv(a: np.ndarray, b: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(a - b)))


def _flatten(schedule: dict[str, Any], unit_index: dict[str, int], unit_stratum, unit_group, unit_score):
    uidx, groups, scores, strata_i, p_opp, cw_id_list = [], [], [], [], [], []
    stratum_labels = sorted(set(unit_stratum.values()))
    s_index = {s: i for i, s in enumerate(stratum_labels)}
    cw_keys: dict[tuple[int, str], int] = {}
    for r in schedule["rows"]:
        key = (int(r["window_id"]), str(r["client_id"]))
        if key not in cw_keys:
            cw_keys[key] = len(cw_keys)
        cw = cw_keys[key]
        pops = r["candidate_p_opp"]
        for uid, p in zip(r["candidate_unit_ids"], pops, strict=True):
            u = str(uid)
            uidx.append(unit_index[u])
            groups.append(int(unit_group[u]))
            scores.append(int(unit_score[u]))
            strata_i.append(s_index[unit_stratum[u]])
            p_opp.append(float(p))
            cw_id_list.append(cw)
    return {
        "uidx": np.asarray(uidx, dtype=np.int64),
        "group": np.asarray(groups, dtype=np.int64),
        "score": np.asarray(scores, dtype=np.int64),
        "stratum_i": np.asarray(strata_i, dtype=np.int64),
        "p_opp": np.asarray(p_opp, dtype=np.float64),
        "p_obs": np.full(len(uidx), float(OBS_RATE_TARGET)),
        "p_use": np.full(len(uidx), float(USE_RATE_TARGET)),
        "cw_id": np.asarray(cw_id_list, dtype=np.int64),
        "n_cw": len(cw_keys),
        "stratum_labels": stratum_labels,
        "event_mass": np.ones(len(uidx), dtype=np.float64),
    }


def run_single_arm_variance(
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
    out_dir = root / "outputs/e2_balanced_dgp"
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
        cert_levels[level] = (cids, tcert)

    flat = _flatten(base_schedule, unit_index, unit_stratum, unit_group, unit_score)
    mass = flat["event_mass"]
    p_opp, p_obs, p_use = flat["p_opp"], flat["p_obs"], flat["p_use"]
    uidx = flat["uidx"]
    n_units = len(unit_ids)
    expected_count = float(np.sum(p_opp * p_obs * p_use))

    rows = []
    registry = []
    for rep in range(1, n_reps + 1):
        rep_id = f"audit-rep-{rep:04d}"
        registry.append(rep_id)
        seed_int = int.from_bytes(bytes.fromhex(sha256_json({"r": rep_id})[:16]), "big") % (2**32 - 1)
        rng = np.random.default_rng(seed_int)
        n = len(uidx)
        # SINGLE ARM only
        u_a = rng.random(n)
        u_o = rng.random(n)
        u_use = rng.random(flat["n_cw"])
        a = u_a < p_opp
        o = u_o < p_obs
        use = u_use[flat["cw_id"]] < p_use

        def atomic_from(weights: np.ndarray) -> tuple[np.ndarray, float]:
            atomic = np.bincount(uidx, weights=weights, minlength=n_units).astype(np.float64)
            return atomic, float(weights.sum())

        def metrics(atomic: np.ndarray, arrival_count: float) -> dict[str, float]:
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
                # Realized zero-arrival rate over positive-target cert cells
                pos = tcert > 0
                zero = (emp_c <= 0) & pos
                out[f"zero_arrival_rate_{level}"] = float(zero.sum() / max(pos.sum(), 1))
            return out

        exp_w = mass * p_opp * p_obs * p_use
        atomic, tot = atomic_from(exp_w)
        rows.append({"audit_replicate": rep_id, "version": "V0", **metrics(atomic, tot)})
        w1 = mass * a.astype(np.float64) * p_obs * p_use
        w2 = mass * a.astype(np.float64) * o.astype(np.float64) * p_use
        w3 = mass * a.astype(np.float64) * o.astype(np.float64) * use.astype(np.float64)
        for version, w in (("V1", w1), ("V2", w2), ("V3", w3)):
            atomic, tot = atomic_from(w)
            rows.append({"audit_replicate": rep_id, "version": version, **metrics(atomic, tot)})

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "E2_SINGLE_ARM_VARIANCE_BY_REPLICATE.csv", index=False)

    def summarize(sub: pd.DataFrame, col: str) -> dict[str, float]:
        x = sub[col].astype(float)
        return {
            "mean": float(x.mean()), "std": float(x.std(ddof=0)),
            "p50": float(x.quantile(0.50)), "p90": float(x.quantile(0.90)),
            "p95": float(x.quantile(0.95)), "max": float(x.max()),
        }

    summary: dict[str, Any] = {
        "n_replicates": n_reps,
        "audit_registry_hash": sha256_json(registry),
        "estimator": "single_arm",
        "antithetic_used": False,
        "expected_arrival_total_design_count": expected_count,
        "versions": {},
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
            block[f"zero_arrival_rate_{level}"] = summarize(sub, f"zero_arrival_rate_{level}")
        summary["versions"][version] = block

    dump_json(summary, out_dir / "E2_SINGLE_ARM_VARIANCE_SUMMARY.json")
    dump_json(
        {"replicates": registry, "hash": summary["audit_registry_hash"], "antithetic": False},
        out_dir / "E2_AUDIT_REPLICATE_REGISTRY.json",
    )
    # Optional antithetic diagnostic (excluded from selection).
    dump_json({
        "diagnostic_only": True,
        "excluded_from_selection": True,
        "excluded_from_validation_gate": True,
        "status": "NOT_RUN_OPTIONAL",
        "note": "Antithetic sensitivity not required for main selection.",
    }, out_dir / "E2_ANTITHETIC_SENSITIVITY_SUMMARY.json")
    return {
        "summary": summary,
        "frame": df,
        "registry": registry,
        "expected_arrival_total_count": expected_count,
        "cert_levels": cert_levels,
    }
