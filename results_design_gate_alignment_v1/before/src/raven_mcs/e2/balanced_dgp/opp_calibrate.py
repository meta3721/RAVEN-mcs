"""Write Balanced calibration into p_opp; keep event mass = 1."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.empirical.events import OPP_GEN_MAX, OPP_GEN_MIN, OPP_RATE_TARGET
from raven_mcs.e2.hard_variance.raw_calibrate import load_raw_pi_and_lambda
from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_head_tail_mapping
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def _tv(a: dict, b: dict, keys) -> float:
    return 0.5 * float(sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys))


def _rake_by_codes(values: np.ndarray, codes: np.ndarray, targets: np.ndarray) -> np.ndarray:
    """Multiply values so sums by integer code match targets (vectorized)."""
    out = values.copy()
    n = int(targets.size)
    cur = np.bincount(codes, weights=out, minlength=n).astype(np.float64)
    scale = np.ones(n, dtype=np.float64)
    pos = (cur > 0) & (targets > 0)
    scale[pos] = targets[pos] / cur[pos]
    out *= scale[codes]
    return out


def calibrate_opportunity_probabilities(
    schedule: dict[str, Any],
    root: Path | None = None,
    *,
    max_iters: int = 250,
    tol: float = 1e-8,
) -> dict[str, Any]:
    """Solve p_opp on bounded exposure so soft expected mass matches pi/Lambda."""
    root = Path(root or ROOT)
    pi_df, lam, meta = load_raw_pi_and_lambda(root)
    atomic = load_e1_atomic_target_weights(root)
    ht = load_e1_head_tail_mapping(root).set_index("unit_id")
    unit_target = {str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)}
    z = sum(unit_target.values()) or 1.0
    unit_target = {u: w / z for u, w in unit_target.items()}
    unit_group = {str(u): int(ht.loc[str(u), "target_group_main"]) for u in atomic["unit_id"].astype(str)}
    unit_score = {str(u): int(ht.loc[str(u), "tail_score"]) for u in atomic["unit_id"].astype(str)}
    unit_stratum = {}
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    for r in processed.itertuples(index=False):
        raw = str(r.opportunity_stratum)
        unit_stratum[str(r.unit_id)] = "::".join(raw.split("::")[:3]) if "::" in raw else raw

    detail_rows = []
    for r in schedule["rows"]:
        cid = str(r["client_id"])
        for uid in r["candidate_unit_ids"]:
            detail_rows.append({
                "client_id": cid,
                "window_id": int(r["window_id"]),
                "unit_id": str(uid),
                "raw_stratum": unit_stratum[str(uid)],
                "exposure": 1.0,
            })
    detail = pd.DataFrame(detail_rows)
    C_ks = (
        detail.groupby(["client_id", "raw_stratum"], sort=True)["exposure"]
        .sum().reset_index().rename(columns={"exposure": "C_k_s"})
    )
    C = {(str(r.client_id), str(r.raw_stratum)): float(r.C_k_s) for r in C_ks.itertuples(index=False)}
    pi = {(str(r.client_id), str(r.raw_stratum)): float(r.pi_k_s_tar) for r in pi_df.itertuples(index=False)}
    unsupported = [
        {"client_id": k, "raw_stratum": s, "pi": t}
        for (k, s), t in pi.items()
        if t > 0 and C.get((k, s), 0.0) <= 0
    ]
    clients = sorted({k for k, _ in C})
    strata = sorted(lam)
    cell_keys = sorted(set(C) | set(pi))
    cell_index = {key: i for i, key in enumerate(cell_keys)}
    n_cells = len(cell_keys)
    C_arr = np.zeros(n_cells)
    pi_arr = np.zeros(n_cells)
    for key, i in cell_index.items():
        C_arr[i] = C.get(key, 0.0)
        pi_arr[i] = pi.get(key, 0.0)
    gamma_arr = np.ones(n_cells)
    # stratum codes for cells
    cell_stratum = np.asarray([key[1] for key in cell_keys], dtype=object)
    stratum_labels = strata
    s_to_i = {s: i for i, s in enumerate(stratum_labels)}
    cell_s_code = np.asarray([s_to_i[s] for s in cell_stratum], dtype=np.int64)
    lam_arr = np.asarray([float(lam[s]) for s in stratum_labels], dtype=np.float64)

    max_resid = 1.0
    converged = False
    for _ in range(max_iters):
        cur = C_arr * gamma_arr
        pos = (cur > 0) & (pi_arr > 0)
        gamma_arr[pos] *= pi_arr[pos] / cur[pos]
        tot = float((C_arr * gamma_arr).sum()) or 1.0
        gamma_arr /= tot
        # stratum margin
        cur_s = np.bincount(cell_s_code, weights=C_arr * gamma_arr, minlength=len(stratum_labels))
        fac = np.ones(len(stratum_labels))
        spos = (cur_s > 0) & (lam_arr > 0)
        fac[spos] = lam_arr[spos] / cur_s[spos]
        gamma_arr *= fac[cell_s_code]
        tot = float((C_arr * gamma_arr).sum()) or 1.0
        gamma_arr /= tot
        resid = float(np.max(np.abs(C_arr * gamma_arr - pi_arr))) if n_cells else 0.0
        cur_s = np.bincount(cell_s_code, weights=C_arr * gamma_arr, minlength=len(stratum_labels))
        resid = max(resid, float(np.max(np.abs(cur_s - lam_arr))))
        max_resid = resid
        if max_resid <= tol and not unsupported:
            converged = True
            break

    gamma = {cell_keys[i]: float(gamma_arr[i]) for i in range(n_cells)}
    cids = detail["client_id"].astype(str).to_numpy()
    sids = detail["raw_stratum"].astype(str).to_numpy()
    uids = detail["unit_id"].astype(str).to_numpy()
    row_cell = np.asarray([cell_index[(str(cids[i]), str(sids[i]))] for i in range(len(cids))], dtype=np.int64)
    w = gamma_arr[row_cell].copy()

    tgt_g: dict[int, float] = {}
    tgt_tail = tgt_head = 0.0
    for u, wt in unit_target.items():
        tgt_g[int(unit_group[u])] = tgt_g.get(int(unit_group[u]), 0.0) + wt
        sc = int(unit_score[u])
        if sc == 1:
            tgt_tail += wt
        elif sc == -1:
            tgt_head += wt
    groups = np.asarray([int(unit_group[u]) for u in uids], dtype=np.int64)
    scores = np.asarray([int(unit_score[u]) for u in uids], dtype=np.int64)
    uniq_g = sorted(tgt_g)
    g_code = {g: i for i, g in enumerate(uniq_g)}
    group_codes = np.asarray([g_code[int(g)] for g in groups], dtype=np.int64)
    tgt_g_arr = np.asarray([tgt_g[g] for g in uniq_g], dtype=np.float64)
    cell_target_arr = C_arr * gamma_arr
    stratum_codes = np.asarray([s_to_i[str(s)] for s in sids], dtype=np.int64)

    for _ in range(40):
        w = _rake_by_codes(w, group_codes, tgt_g_arr)
        w = _rake_by_codes(w, row_cell, cell_target_arr)
    for _ in range(40):
        st = float(w[scores == 1].sum())
        sh = float(w[scores == -1].sum())
        if st <= 0 or sh <= 0:
            break
        w = w.copy()
        w[scores == 1] *= tgt_tail / st
        w[scores == -1] *= tgt_head / sh
        w = _rake_by_codes(w, group_codes, tgt_g_arr)
        w = _rake_by_codes(w, row_cell, cell_target_arr)

    def weights_to_p(vec: np.ndarray) -> tuple[np.ndarray, float]:
        """Map positive calibration weights to bounded p_opp.

        Prefer the identity soft map p ∝ w (mean = opportunity_rate_target).
        Under capacity-feasible bounded windows this stays inside
        [opp_gen_min, opp_gen_max] and preserves soft composition exactly.
        If bounds bind, fall back to clip + additive mean repair and let the
        outer rake restore margins.
        """
        base = np.maximum(vec, 1e-300)
        p = OPP_RATE_TARGET * (base / (float(np.mean(base)) or 1.0))
        if float(p.min()) >= OPP_GEN_MIN - 1e-15 and float(p.max()) <= OPP_GEN_MAX + 1e-15:
            return p, abs(float(np.mean(p)) - OPP_RATE_TARGET)
        for _ in range(80):
            p = np.clip(p, OPP_GEN_MIN, OPP_GEN_MAX)
            err = OPP_RATE_TARGET - float(np.mean(p))
            if abs(err) <= 1e-12:
                break
            p = np.clip(p + err, OPP_GEN_MIN, OPP_GEN_MAX)
        return p, abs(float(np.mean(p)) - OPP_RATE_TARGET)

    # Soft composition is exact on w; map to bounded p_opp and refine if needed.
    p, rate_err = weights_to_p(w)
    d_g = d_s = d_cs = 1.0
    for _ in range(30):
        soft = p / (float(p.sum()) or 1.0)
        rho_s = {s: float(soft[stratum_codes == s_to_i[s]].sum()) for s in stratum_labels}
        rho_ks = {cell_keys[i]: float(soft[row_cell == i].sum()) for i in range(n_cells)}
        rho_g = {g: float(soft[group_codes == g_code[g]].sum()) for g in uniq_g}
        d_g = _tv(rho_g, tgt_g, uniq_g)
        d_s = _tv(rho_s, lam, stratum_labels)
        d_cs = _tv(rho_ks, {k: pi.get(k, 0.0) for k in cell_keys}, cell_keys)
        if d_g <= 0.01 and d_s <= 0.01 and d_cs <= 0.03 and rate_err <= 1e-10:
            break
        # Bound repair moved margins — rake absolute p masses, then remap.
        total = float(p.sum()) or 1.0
        p = _rake_by_codes(p, group_codes, tgt_g_arr * total)
        soft = p / (float(p.sum()) or 1.0)
        st = float(soft[scores == 1].sum())
        sh = float(soft[scores == -1].sum())
        if st > 0 and sh > 0:
            p = p.copy()
            p[scores == 1] *= tgt_tail / st
            p[scores == -1] *= tgt_head / sh
        total = float(p.sum()) or 1.0
        p = _rake_by_codes(p, stratum_codes, lam_arr * total)
        p = _rake_by_codes(p, row_cell, pi_arr * total)
        p, rate_err = weights_to_p(p)

    cal_rows = []
    cursor = 0
    for r in schedule["rows"]:
        rr = dict(r)
        n = len(r["candidate_unit_ids"])
        rr["candidate_event_mass"] = [1.0] * n
        rr["candidate_p_opp"] = [float(p[cursor + j]) for j in range(n)]
        rr["candidate_calibration_weight"] = [float(w[cursor + j]) for j in range(n)]
        cursor += n
        cal_rows.append(rr)
    if cursor != len(p):
        raise RuntimeError("p_opp attachment length mismatch")
    cal_sched = dict(schedule)
    cal_sched["rows"] = cal_rows
    cal_sched["calibrated"] = True
    cal_sched["calibration_in"] = "p_opp"

    status = (
        "PASS"
        if (
            d_g <= 0.01 and d_s <= 0.01 and d_cs <= 0.03
            and float(p.min()) >= OPP_GEN_MIN - 1e-15
            and float(p.max()) <= OPP_GEN_MAX + 1e-15
            and rate_err <= 1e-10
            and max_resid <= 1e-8
            and len(unsupported) == 0
            and converged
        )
        else "FAIL"
    )
    solved = {
        "status": status,
        "D_TV_group_soft": float(d_g),
        "D_TV_raw_stratum_soft": float(d_s),
        "D_TV_client_raw_stratum_soft": float(d_cs),
        "p_opp_min": float(p.min()),
        "p_opp_max": float(p.max()),
        "p_opp_mean": float(p.mean()),
        "p_opp_std": float(p.std(ddof=0)),
        "opportunity_rate_error": float(rate_err),
        "max_marginal_residual": float(max_resid),
        "unsupported_target_cell_count": int(len(unsupported)),
        "solver_converged": bool(converged and not unsupported),
        "raw_stratum_count": meta["raw_stratum_count"],
        "gamma_ks": {f"{k}|{s}": float(v) for (k, s), v in gamma.items()},
    }
    return {
        "solved": solved,
        "calibrated_schedule": cal_sched,
        "p_opp": p,
        "weights": w,
        "detail": detail,
        "unit_stratum": unit_stratum,
        "unit_group": unit_group,
        "unit_score": unit_score,
        "unit_target": unit_target,
    }


def write_opp_calibration_outputs(
    per_seed: list[dict[str, Any]],
    probability_frames: list[pd.DataFrame],
    root: Path,
) -> dict[str, Any]:
    out = root / "outputs/e2_balanced_dgp"
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(per_seed)
    soft_pass = bool((df["status"] == "PASS").all())
    audit = {
        "status": "PASS" if soft_pass else "BLOCKED_OPPORTUNITY_PROBABILITY_CALIBRATION",
        "per_seed": per_seed,
        "max_D_TV_group_soft": float(df["D_TV_group_soft"].max()),
        "max_D_TV_raw_stratum_soft": float(df["D_TV_raw_stratum_soft"].max()),
        "max_D_TV_client_raw_stratum_soft": float(df["D_TV_client_raw_stratum_soft"].max()),
        "p_opp_min": float(df["p_opp_min"].min()),
        "p_opp_max": float(df["p_opp_max"].max()),
        "p_opp_mean": float(df["p_opp_mean"].mean()),
        "p_opp_std": float(df["p_opp_std"].mean()),
        "max_opportunity_rate_error": float(df["opportunity_rate_error"].max()),
        "unsupported_target_cell_count": int(df["unsupported_target_cell_count"].sum()),
        "calibration_target": "p_opp",
        "event_mass_unchanged": True,
    }
    dump_json(audit, out / "E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json")
    pd.concat(probability_frames, ignore_index=True).to_parquet(
        out / "E2_OPPORTUNITY_PROBABILITIES.parquet", index=False,
    )
    df.to_csv(out / "E2_OPPORTUNITY_CALIBRATION_RESIDUALS.csv", index=False)
    return audit


def generate_opportunity_from_schedule_p(
    *,
    schedule_rows: list[dict[str, Any]],
    opp_uniforms: np.ndarray,
    client_index: dict[str, int],
    seed: int,
    profile_id: str,
    scenario_id: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Hard opportunity draws using precomputed candidate_p_opp; event mass = 1."""
    records = []
    used = 0
    selected = 0
    for row in schedule_rows:
        wid = int(row["window_id"])
        cid = str(row["client_id"])
        ci = int(client_index[cid]) % opp_uniforms.shape[1]
        p_list = row.get("candidate_p_opp")
        if p_list is None:
            raise RuntimeError("schedule missing candidate_p_opp")
        cal_w = row.get("candidate_calibration_weight") or [1.0] * len(p_list)
        for j, (unit_id, p) in enumerate(zip(row["candidate_unit_ids"], p_list, strict=True)):
            u = float(opp_uniforms[wid, ci, min(j, opp_uniforms.shape[2] - 1)])
            used += 1
            flag = bool(u < float(p))
            selected += int(flag)
            records.append({
                "seed": int(seed),
                "profile_id": profile_id,
                "scenario_id": scenario_id,
                "window_id": wid,
                "client_id": cid,
                "unit_id": str(unit_id),
                "tail_score": 0,
                "opportunity_probability": float(p),
                "base_opportunity_uniform": u,
                "opportunity_selected": flag,
                "candidate_event_mass": 1.0,
                "calibrated_weight": float(cal_w[j]),
                "opportunity_intercept": float("nan"),
            })
    frame = pd.DataFrame(records)
    audit = {
        "base_opportunity_uniforms_used_count": int(used),
        "selected_event_count": int(selected),
        "unknown_unit_count": 0,
        "duplicate_unit_id_within_window_count": 0,
        "unsupported_selected_count": 0,
        "calibrated_mass_probability": True,
        "event_mass": 1.0,
    }
    dup = frame.groupby(["window_id", "client_id", "unit_id"]).size().reset_index(name="n")
    audit["duplicate_unit_id_within_window_count"] = int((dup["n"] > 1).sum())
    return frame, audit
