"""Balanced opportunity exposure calibration (IPF / raking, pre-outcome only)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.legal_horizon.stratum100 import load_merged_stratum_100
from raven_mcs.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[4]


def load_pi_target(root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    path = root / "configs/frozen/e1_pi_target_client_stratum.parquet"
    pi = pd.read_parquet(path)
    meta = {
        "path": str(path.as_posix()),
        "hash": sha256_file(path),
        "row_count": int(len(pi)),
        "stratum_count": int(pi["opportunity_stratum"].nunique()),
        "client_count": int(pi["client_id"].nunique()),
        "pi_sum": float(pi["pi_k_s_tar"].sum()),
    }
    return pi, meta


def map_raw_pi_to_merged(
    pi: pd.DataFrame,
    mapping: dict[str, str],
    stratum_mass: dict[str, float],
) -> pd.DataFrame:
    rows = []
    for r in pi.itertuples(index=False):
        raw = str(r.opportunity_stratum)
        merged = mapping.get(raw, raw)
        rows.append({
            "client_id": str(r.client_id),
            "merged_stratum_id": merged,
            "pi_k_s_tar": float(r.pi_k_s_tar),
        })
    agg = (
        pd.DataFrame(rows)
        .groupby(["client_id", "merged_stratum_id"], sort=True)["pi_k_s_tar"]
        .sum()
        .reset_index()
    )
    agg["Lambda_s_tar"] = agg["merged_stratum_id"].map(lambda s: float(stratum_mass[s]))
    return agg


def candidate_exposure_from_schedule(
    schedule: dict[str, Any],
    unit_stratum: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for r in schedule["rows"]:
        cid = str(r["client_id"])
        for uid, mass in zip(r["candidate_unit_ids"], r["candidate_event_mass"], strict=True):
            sid = unit_stratum[str(uid)]
            rows.append({
                "client_id": cid,
                "window_id": int(r["window_id"]),
                "unit_id": str(uid),
                "merged_stratum_id": sid,
                "candidate_mass": float(mass),
            })
    detail = pd.DataFrame(rows)
    by_cs = (
        detail.groupby(["client_id", "merged_stratum_id"], sort=True)["candidate_mass"]
        .sum()
        .reset_index()
        .rename(columns={"candidate_mass": "C_k_s"})
    )
    return detail, by_cs


def solve_balanced_calibration(
    detail: pd.DataFrame,
    C_ks: pd.DataFrame,
    pi_ks: pd.DataFrame,
    *,
    unit_stratum: dict[str, str],
    unit_target: dict[str, float],
    unit_score: dict[str, int],
    unit_group: dict[str, int],
    stratum_mass: dict[str, float],
    max_iters: int = 300,
    tol: float = 1e-8,
) -> dict[str, Any]:
    clients = sorted(set(C_ks["client_id"].astype(str)))
    strata = sorted(stratum_mass)
    C = {
        (str(r.client_id), str(r.merged_stratum_id)): float(r.C_k_s)
        for r in C_ks.itertuples(index=False)
    }
    pi = {
        (str(r.client_id), str(r.merged_stratum_id)): float(r.pi_k_s_tar)
        for r in pi_ks.itertuples(index=False)
    }
    unsupported = [
        {"client_id": k, "merged_stratum_id": s, "pi_k_s_tar": tgt}
        for (k, s), tgt in pi.items()
        if tgt > 0 and C.get((k, s), 0.0) <= 0
    ]
    gamma_cell = {key: 1.0 for key in C}
    max_resid = 1.0
    converged = False
    for _ in range(max_iters):
        for (k, s), c in C.items():
            tgt = pi.get((k, s), 0.0)
            cur = c * gamma_cell[(k, s)]
            if cur > 0 and tgt > 0:
                gamma_cell[(k, s)] *= tgt / cur
        total = sum(C[key] * gamma_cell[key] for key in C) or 1.0
        for key in gamma_cell:
            gamma_cell[key] /= total
        for s in strata:
            cur_s = sum(C.get((k, s), 0.0) * gamma_cell.get((k, s), 0.0) for k in clients)
            tgt_s = float(stratum_mass[s])
            if cur_s > 0 and tgt_s > 0:
                fac = tgt_s / cur_s
                for k in clients:
                    if (k, s) in gamma_cell:
                        gamma_cell[(k, s)] *= fac
        total = sum(C[key] * gamma_cell[key] for key in C) or 1.0
        for key in gamma_cell:
            gamma_cell[key] /= total
        resid = 0.0
        for (k, s), c in C.items():
            resid = max(resid, abs(c * gamma_cell[(k, s)] - pi.get((k, s), 0.0)))
        for s in strata:
            cur_s = sum(C.get((k, s), 0.0) * gamma_cell.get((k, s), 0.0) for k in clients)
            resid = max(resid, abs(cur_s - float(stratum_mass[s])))
        max_resid = float(resid)
        if max_resid <= tol and not unsupported:
            converged = True
            break

    # Sequential within-support raking after cell IPF:
    # 1) group margins (needed when cross-time merges mix ToD groups)
    # 2) head/tail margins
    # Both preserve (client, stratum) cell totals so Lambda / pi stay matched.
    z_all = sum(unit_target.values()) or 1.0
    tgt_tail = 0.0
    tgt_head = 0.0
    tgt_g: dict[int, float] = {}
    for u, wt in unit_target.items():
        ww = float(wt) / z_all
        tgt_g[int(unit_group[u])] = tgt_g.get(int(unit_group[u]), 0.0) + ww
        # E1 tail_score: +1 = tail, -1 = head, 0 = neutral (excluded from HT ratios).
        if int(unit_score[u]) == 1:
            tgt_tail += ww
        elif int(unit_score[u]) == -1:
            tgt_head += ww

    base = np.asarray(detail["candidate_mass"].to_numpy(dtype=np.float64), copy=False)
    cids = detail["client_id"].astype(str).to_numpy()
    sids = detail["merged_stratum_id"].astype(str).to_numpy()
    uids = detail["unit_id"].astype(str).to_numpy()
    scores = np.asarray([int(unit_score[u]) for u in uids], dtype=np.int64)
    groups = np.asarray([int(unit_group[u]) for u in uids], dtype=np.int64)
    cell_target = {
        key: float(C[key] * gamma_cell[key]) for key in C
    }
    w = np.asarray([
        float(base[i]) * float(gamma_cell[(str(cids[i]), str(sids[i]))])
        for i in range(len(base))
    ], dtype=np.float64)

    def _restore_cells(arr: np.ndarray) -> np.ndarray:
        out = arr.copy()
        for (k, s), tgt_cell in cell_target.items():
            mask = (cids == k) & (sids == s)
            cur = float(out[mask].sum())
            if cur > 0 and tgt_cell > 0:
                out[mask] *= tgt_cell / cur
        return out

    for _ in range(60):
        for g, tgt in tgt_g.items():
            mask = groups == int(g)
            cur_g = float(w[mask].sum())
            if cur_g > 0 and tgt > 0:
                w[mask] *= tgt / cur_g
        w = _restore_cells(w)
        if all(abs(float(w[groups == int(g)].sum()) - tgt) <= 1e-8 for g, tgt in tgt_g.items()):
            break

    for _ in range(60):
        soft_tail = float(w[scores == 1].sum())
        soft_head = float(w[scores == -1].sum())
        if soft_tail <= 0 or soft_head <= 0 or tgt_tail <= 0 or tgt_head <= 0:
            break
        scale = np.ones(len(w), dtype=np.float64)
        scale[scores == 1] = tgt_tail / soft_tail
        scale[scores == -1] = tgt_head / soft_head
        w = w * scale
        w = _restore_cells(w)
        # Re-assert group after HT (HT can perturb group slightly)
        for g, tgt in tgt_g.items():
            mask = groups == int(g)
            cur_g = float(w[mask].sum())
            if cur_g > 0 and tgt > 0:
                w[mask] *= tgt / cur_g
        w = _restore_cells(w)
        if (
            abs(float(w[scores == 1].sum()) - tgt_tail) <= 1e-6
            and abs(float(w[scores == -1].sum()) - tgt_head) <= 1e-6
            and all(abs(float(w[groups == int(g)].sum()) - tgt) <= 1e-6 for g, tgt in tgt_g.items())
        ):
            break

    total = float(w.sum()) or 1.0
    soft = w / total

    gamma_unit: dict[str, float] = {}
    for uid in sorted(set(uids.tolist())):
        mask = uids == uid
        b = float(base[mask].sum())
        gamma_unit[uid] = float(w[mask].sum() / b) if b > 0 else 1.0

    detail_soft = detail.copy()
    detail_soft["soft_w"] = soft
    rho_s = detail_soft.groupby("merged_stratum_id")["soft_w"].sum().to_dict()
    rho_ks_df = detail_soft.groupby(["client_id", "merged_stratum_id"], sort=True)["soft_w"].sum().reset_index()
    rho_ks = {
        (str(r.client_id), str(r.merged_stratum_id)): float(r.soft_w)
        for r in rho_ks_df.itertuples(index=False)
    }
    rho_g: dict[int, float] = {}
    soft_tail = 0.0
    soft_head = 0.0
    for r, ww in zip(detail.itertuples(index=False), soft, strict=True):
        uid = str(r.unit_id)
        rho_g[int(unit_group[uid])] = rho_g.get(int(unit_group[uid]), 0.0) + float(ww)
        sc = int(unit_score[uid])
        if sc == 1:
            soft_tail += float(ww)
        elif sc == -1:
            soft_head += float(ww)

    def tv(a: dict, b: dict, keys) -> float:
        return 0.5 * float(sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys))

    d_tv_cs = tv(rho_ks, pi, list(set(pi) | set(C)))
    d_tv_s = tv(rho_s, stratum_mass, strata)
    d_tv_g = tv(rho_g, tgt_g, list(tgt_g.keys()))

    return {
        "gamma_unit": gamma_unit,
        "gamma": {f"{k}|{s}": float(v) for (k, s), v in gamma_cell.items()},
        "rho_ks": {f"{k}|{s}": float(v) for (k, s), v in rho_ks.items()},
        "rho_s": {s: float(v) for s, v in rho_s.items()},
        "D_TV_client_stratum_soft": float(d_tv_cs),
        "D_TV_stratum_soft": float(d_tv_s),
        "D_TV_group_soft": float(d_tv_g),
        "max_marginal_residual": float(max_resid),
        "solver_converged": bool(converged and not unsupported),
        "unsupported_target_cells": unsupported,
        "unsupported_target_cell_count": int(len(unsupported)),
        "finite_status": True,
        "soft_tail_mass": float(soft_tail),
        "soft_head_mass": float(soft_head),
        "target_tail_mass": float(tgt_tail),
        "target_head_mass": float(tgt_head),
    }


def attach_calibrated_masses_unit(
    schedule: dict[str, Any],
    gamma_unit: dict[str, float],
) -> dict[str, Any]:
    rows = []
    for r in schedule["rows"]:
        new_masses = [
            float(mass) * float(gamma_unit.get(str(uid), 1.0))
            for uid, mass in zip(r["candidate_unit_ids"], r["candidate_event_mass"], strict=True)
        ]
        rr = dict(r)
        rr["candidate_event_mass_base"] = list(r["candidate_event_mass"])
        rr["candidate_event_mass"] = new_masses
        rows.append(rr)
    out = dict(schedule)
    out["rows"] = rows
    out["calibrated"] = True
    return out


def run_balanced_calibration_for_seed(
    seed: int,
    schedule: dict[str, Any],
    root: Path | None = None,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    frame, ident = load_merged_stratum_100(root)
    unit_stratum = dict(zip(frame["unit_id"].astype(str), frame["stratum_id"].astype(str), strict=True))
    mapping = {str(r.raw_stratum_id): str(r.merged_stratum_id) for r in frame.itertuples(index=False)}
    pi_raw, pi_meta = load_pi_target(root)
    pi_merged = map_raw_pi_to_merged(pi_raw, mapping, ident["stratum_target_mass"])
    detail, C_ks = candidate_exposure_from_schedule(schedule, unit_stratum)

    from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_head_tail_mapping
    atomic = load_e1_atomic_target_weights(root)
    ht = load_e1_head_tail_mapping(root).set_index("unit_id")
    unit_target = {str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)}
    unit_group = {str(u): int(ht.loc[str(u), "target_group_main"]) for u in atomic["unit_id"].astype(str)}
    unit_score = {str(u): int(ht.loc[str(u), "tail_score"]) for u in atomic["unit_id"].astype(str)}

    solved = solve_balanced_calibration(
        detail, C_ks, pi_merged,
        unit_stratum=unit_stratum,
        unit_target=unit_target,
        unit_score=unit_score,
        unit_group=unit_group,
        stratum_mass=ident["stratum_target_mass"],
    )
    solved["pi_identity_hash"] = pi_meta["hash"]
    solved["seed"] = int(seed)
    solved["status"] = (
        "PASS"
        if (
            solved["D_TV_stratum_soft"] <= 0.01
            and solved["D_TV_group_soft"] <= 0.01
            and solved["D_TV_client_stratum_soft"] <= 0.03
            and solved["unsupported_target_cell_count"] == 0
            and solved["solver_converged"]
            and solved["max_marginal_residual"] <= 1e-8
            and solved["finite_status"]
        )
        else "FAIL"
    )
    return {
        "solved": solved,
        "C_ks": C_ks,
        "pi_merged": pi_merged,
        "detail": detail,
        "calibrated_schedule": attach_calibrated_masses_unit(schedule, solved["gamma_unit"]),
        "unit_stratum": unit_stratum,
        "pi_meta": pi_meta,
        "stratum_identity": ident,
    }
