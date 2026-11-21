"""Raw-stratum Balanced soft calibration on dense exposure."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_head_tail_mapping
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def load_raw_pi_and_lambda(root: Path) -> tuple[pd.DataFrame, dict[str, float], dict[str, Any]]:
    pi = pd.read_parquet(root / "configs/frozen/e1_pi_target_client_stratum.parquet")
    atomic = load_e1_atomic_target_weights(root)
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed["unit_id"] = processed["unit_id"].astype(str)
    weight = {str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)}
    rows = []
    for r in processed.itertuples(index=False):
        uid = str(r.unit_id)
        if uid not in weight:
            continue
        raw = str(r.opportunity_stratum)
        parts = raw.split("::")
        sid = "::".join(parts[:3]) if len(parts) >= 3 else raw
        rows.append({"raw_stratum": sid, "target_weight": weight[uid]})
    frame = pd.DataFrame(rows)
    lam = frame.groupby("raw_stratum")["target_weight"].sum()
    lam = (lam / lam.sum()).to_dict()
    meta = {
        "pi_path": "configs/frozen/e1_pi_target_client_stratum.parquet",
        "pi_hash": sha256_file(root / "configs/frozen/e1_pi_target_client_stratum.parquet"),
        "raw_stratum_count": int(len(lam)),
        "pi_sum": float(pi["pi_k_s_tar"].sum()),
        "lambda_sum": float(sum(lam.values())),
    }
    # normalize pi column names
    pi = pi.copy()
    pi["raw_stratum"] = pi["opportunity_stratum"].astype(str).map(
        lambda s: "::".join(s.split("::")[:3]) if "::" in s else s
    )
    pi_agg = (
        pi.groupby(["client_id", "raw_stratum"], sort=True)["pi_k_s_tar"].sum().reset_index()
    )
    return pi_agg, lam, meta


def calibrate_dense_raw(
    schedule: dict[str, Any],
    root: Path | None = None,
    *,
    max_iters: int = 400,
    tol: float = 1e-8,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    pi_df, lam, meta = load_raw_pi_and_lambda(root)
    atomic = load_e1_atomic_target_weights(root)
    ht = load_e1_head_tail_mapping(root).set_index("unit_id")
    unit_target = {str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)}
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
        for uid, mass in zip(r["candidate_unit_ids"], r["candidate_event_mass"], strict=True):
            detail_rows.append({
                "client_id": cid,
                "unit_id": str(uid),
                "raw_stratum": unit_stratum[str(uid)],
                "candidate_mass": float(mass),
            })
    detail = pd.DataFrame(detail_rows)
    C_ks = (
        detail.groupby(["client_id", "raw_stratum"], sort=True)["candidate_mass"]
        .sum().reset_index().rename(columns={"candidate_mass": "C_k_s"})
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
    gamma = {key: 1.0 for key in C}
    max_resid = 1.0
    converged = False
    for _ in range(max_iters):
        for (k, s), c in C.items():
            tgt = pi.get((k, s), 0.0)
            cur = c * gamma[(k, s)]
            if cur > 0 and tgt > 0:
                gamma[(k, s)] *= tgt / cur
        tot = sum(C[key] * gamma[key] for key in C) or 1.0
        for key in gamma:
            gamma[key] /= tot
        for s in strata:
            cur_s = sum(C.get((k, s), 0.0) * gamma.get((k, s), 0.0) for k in clients)
            tgt_s = float(lam[s])
            if cur_s > 0 and tgt_s > 0:
                fac = tgt_s / cur_s
                for k in clients:
                    if (k, s) in gamma:
                        gamma[(k, s)] *= fac
        tot = sum(C[key] * gamma[key] for key in C) or 1.0
        for key in gamma:
            gamma[key] /= tot
        resid = 0.0
        for key, c in C.items():
            resid = max(resid, abs(c * gamma[key] - pi.get(key, 0.0)))
        for s in strata:
            cur_s = sum(C.get((k, s), 0.0) * gamma.get((k, s), 0.0) for k in clients)
            resid = max(resid, abs(cur_s - float(lam[s])))
        max_resid = float(resid)
        if max_resid <= tol and not unsupported:
            converged = True
            break

    base = detail["candidate_mass"].to_numpy(dtype=np.float64)
    cids = detail["client_id"].astype(str).to_numpy()
    sids = detail["raw_stratum"].astype(str).to_numpy()
    uids = detail["unit_id"].astype(str).to_numpy()
    w = np.asarray([
        float(base[i]) * float(gamma.get((str(cids[i]), str(sids[i])), 1.0))
        for i in range(len(base))
    ], dtype=np.float64)
    # Group + HT cell-preserving rakes
    z_all = sum(unit_target.values()) or 1.0
    tgt_g: dict[int, float] = {}
    tgt_tail = tgt_head = 0.0
    for u, wt in unit_target.items():
        ww = float(wt) / z_all
        tgt_g[int(unit_group[u])] = tgt_g.get(int(unit_group[u]), 0.0) + ww
        sc = int(unit_score[u])
        if sc == 1:
            tgt_tail += ww
        elif sc == -1:
            tgt_head += ww
    groups = np.asarray([int(unit_group[u]) for u in uids], dtype=np.int64)
    scores = np.asarray([int(unit_score[u]) for u in uids], dtype=np.int64)
    cell_target = {key: float(C[key] * gamma[key]) for key in C}

    def restore(arr: np.ndarray) -> np.ndarray:
        out = arr.copy()
        for (k, s), tgt in cell_target.items():
            mask = (cids == k) & (sids == s)
            cur = float(out[mask].sum())
            if cur > 0 and tgt > 0:
                out[mask] *= tgt / cur
        return out

    for _ in range(80):
        for g, tgt in tgt_g.items():
            mask = groups == int(g)
            cur = float(w[mask].sum())
            if cur > 0 and tgt > 0:
                w[mask] *= tgt / cur
        w = restore(w)
        if all(abs(float(w[groups == int(g)].sum()) - tgt) <= 1e-8 for g, tgt in tgt_g.items()):
            break
    for _ in range(80):
        st = float(w[scores == 1].sum())
        sh = float(w[scores == -1].sum())
        if st <= 0 or sh <= 0:
            break
        scale = np.ones(len(w))
        scale[scores == 1] = tgt_tail / st
        scale[scores == -1] = tgt_head / sh
        w = restore(w * scale)
        for g, tgt in tgt_g.items():
            mask = groups == int(g)
            cur = float(w[mask].sum())
            if cur > 0 and tgt > 0:
                w[mask] *= tgt / cur
        w = restore(w)
        if abs(float(w[scores == 1].sum()) - tgt_tail) <= 1e-6:
            break

    soft = w / (float(w.sum()) or 1.0)
    rho_s = {s: float(soft[sids == s].sum()) for s in strata}
    rho_ks = {
        (str(k), str(s)): float(soft[(cids == k) & (sids == s)].sum())
        for (k, s) in set(pi) | set(C)
    }
    rho_g = {int(g): float(soft[groups == int(g)].sum()) for g in tgt_g}

    def tv(a, b, keys):
        return 0.5 * float(sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys))

    d_g = tv(rho_g, tgt_g, list(tgt_g))
    d_s = tv(rho_s, lam, strata)
    d_cs = tv(rho_ks, pi, list(set(pi) | set(C)))

    gamma_unit: dict[str, float] = {}
    for uid in sorted(set(uids.tolist())):
        mask = uids == uid
        b = float(base[mask].sum())
        gamma_unit[uid] = float(w[mask].sum() / b) if b > 0 else 1.0

    # Attach appearance-level calibrated masses (same order as detail construction).
    # Do not collapse to unit-average gamma — that breaks cell/HT soft identity on schedule.
    cal_rows = []
    cursor = 0
    for r in schedule["rows"]:
        rr = dict(r)
        n = len(r["candidate_unit_ids"])
        base_masses = list(r["candidate_event_mass"])
        cal_masses = [float(w[cursor + j]) for j in range(n)]
        cursor += n
        rr["candidate_event_mass_base"] = base_masses
        rr["candidate_event_mass"] = cal_masses
        cal_rows.append(rr)
    if cursor != len(w):
        raise RuntimeError("calibrated mass attachment length mismatch")
    cal_sched = dict(schedule)
    cal_sched["rows"] = cal_rows
    cal_sched["calibrated"] = True

    status = (
        "PASS"
        if (
            d_g <= 0.01 and d_s <= 0.01 and d_cs <= 0.03
            and len(unsupported) == 0 and converged and max_resid <= 1e-8
        )
        else "FAIL"
    )
    solved = {
        "status": status,
        "D_TV_group_soft": float(d_g),
        "D_TV_raw_stratum_soft": float(d_s),
        "D_TV_client_raw_stratum_soft": float(d_cs),
        "max_marginal_residual": float(max_resid),
        "unsupported_target_cell_count": int(len(unsupported)),
        "unsupported_target_cells": unsupported,
        "solver_converged": bool(converged and not unsupported),
        "pi_identity_hash": meta["pi_hash"],
        "raw_stratum_count": meta["raw_stratum_count"],
        "gamma_unit": gamma_unit,
    }
    return {
        "solved": solved,
        "calibrated_schedule": cal_sched,
        "C_ks": C_ks,
        "pi_meta": meta,
        "lambda_raw": lam,
        "unit_stratum": unit_stratum,
        "unit_group": unit_group,
        "unit_score": unit_score,
        "unit_target": unit_target,
    }


def write_soft_audit(per_seed: list[dict[str, Any]], root: Path) -> dict[str, Any]:
    out_dir = root / "outputs/e2_hard_variance"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(per_seed)
    soft_pass = bool((df["status"] == "PASS").all())
    audit = {
        "status": "PASS" if soft_pass else "BLOCKED_DENSE_BALANCED_SOFT_CALIBRATION",
        "per_seed": per_seed,
        "max_D_TV_group_soft": float(df["D_TV_group_soft"].max()),
        "max_D_TV_raw_stratum_soft": float(df["D_TV_raw_stratum_soft"].max()),
        "max_D_TV_client_raw_stratum_soft": float(df["D_TV_client_raw_stratum_soft"].max()),
        "max_marginal_residual": float(df["max_marginal_residual"].max()),
        "unsupported_target_cell_count": int(df["unsupported_target_cell_count"].sum()),
    }
    dump_json(audit, out_dir / "E2_DENSE_BALANCED_SOFT_CALIBRATION_AUDIT.json")
    return audit
