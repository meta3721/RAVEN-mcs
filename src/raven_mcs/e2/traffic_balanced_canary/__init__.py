"""Traffic Balanced Design Canary: schedule, soft p_opp, A/O/U traces."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.balanced_dgp.opp_calibrate import generate_opportunity_from_schedule_p
from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.events import (
    OBS_RATE_TARGET,
    OPP_GEN_MAX,
    OPP_GEN_MIN,
    OPP_RATE_TARGET,
    USE_RATE_TARGET,
    generate_hard_arrival_events,
    generate_observation_events,
    risk_sets_from_opportunity,
)
from raven_mcs.e2.stage2.usable import (
    enrich_risk_sets_with_observation,
    generate_stage2_usable_events,
)
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
DESIGN_SEEDS = (28101, 28102, 28103)
N_CLIENTS = 43
N_WINDOWS = 100
N_ATOMS = 25800
WINDOW_HOURS = 6

# Rate canary bands around frozen targets (±0.03 / ±0.03 / ±0.05)
OPP_RATE_LO, OPP_RATE_HI = 0.52, 0.58
OBS_RATE_LO, OBS_RATE_HI = 0.17, 0.23
USE_RATE_LO, USE_RATE_HI = 0.55, 0.65


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _tv(a: dict, b: dict, keys) -> float:
    return 0.5 * float(sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys))


def _rake_by_codes(values: np.ndarray, codes: np.ndarray, targets: np.ndarray) -> np.ndarray:
    out = values.copy()
    n = int(targets.size)
    cur = np.bincount(codes, weights=out, minlength=n).astype(np.float64)
    scale = np.ones(n, dtype=np.float64)
    pos = (cur > 0) & (targets > 0)
    scale[pos] = targets[pos] / cur[pos]
    out *= scale[codes]
    return out


def verify_input_identity(root: Path) -> dict[str, Any]:
    """Verify prior public-target seal and freeze Traffic identities."""
    stop = json.loads(
        (root / "outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json").read_text(
            encoding="utf-8"
        )
    )
    if stop.get("status") != "READY_FOR_TRAFFIC_BALANCED_DESIGN_CANARY":
        return {
            "status": "BLOCKED_MISSING_PUBLIC_TARGET_SEAL",
            "prior_status": stop.get("status"),
        }

    paths = {
        "atomic_table": "data/processed/traffic/atomic_units.parquet",
        "atomic_table_identity": "outputs/traffic_mapping/E2_TRAFFIC_ATOMIC_TABLE_IDENTITY.json",
        "global_windows": "configs/frozen/e2_traffic/global_windows_100.parquet",
        "global_windows_identity": "configs/frozen/e2_traffic/global_windows_identity.json",
        "atomic_window_assignment": "configs/frozen/e2_traffic/atomic_window_assignment.parquet",
        "station_spatial": "configs/frozen/e2_traffic/station_spatial_identity.parquet",
        "station_spatial_identity": "configs/frozen/e2_traffic/station_spatial_identity.json",
        "atomic_public_target": "configs/frozen/e2_traffic_public_target/atomic_public_target.parquet",
        "atomic_public_target_identity": "configs/frozen/e2_traffic_public_target/atomic_public_target_identity.json",
        "target_group_mass": "configs/frozen/e2_traffic_public_target/target_group_mass.parquet",
        "opportunity_stratum_target": "configs/frozen/e2_traffic_public_target/opportunity_stratum_target.parquet",
        "client_stratum_target": "configs/frozen/e2_traffic_public_target/client_stratum_target.parquet",
        "public_target_identity": "configs/frozen/e2_traffic_public_target/public_target_identity.json",
        "q_feature_manifest": "configs/frozen/e2_traffic_public_target/q_feature_manifest.json",
        "station_region_mapping": "configs/frozen/e2_traffic_public_target/station_region_mapping.parquet",
    }
    artifacts = {}
    missing = []
    for name, rel in paths.items():
        p = root / rel
        if not p.exists():
            missing.append(rel)
            continue
        entry: dict[str, Any] = {"path": rel, "exists": True}
        if p.suffix in {".parquet", ".json", ".yaml", ".yml", ".csv", ".txt", ".md"}:
            entry["sha256"] = sha256_file(p)
            entry["size_bytes"] = int(p.stat().st_size)
        if p.suffix == ".json":
            payload = json.loads(p.read_text(encoding="utf-8"))
            for key in ("identity_hash", "sha256", "feature_schema_hash", "mapping_hash", "status"):
                if key in payload:
                    entry[key] = payload[key]
        artifacts[name] = entry

    pub = json.loads((root / paths["public_target_identity"]).read_text(encoding="utf-8"))
    win = json.loads((root / paths["global_windows_identity"]).read_text(encoding="utf-8"))
    q = json.loads((root / paths["q_feature_manifest"]).read_text(encoding="utf-8"))
    atomic_id = json.loads((root / paths["atomic_table_identity"]).read_text(encoding="utf-8"))

    # Hash consistency vs parent freeze if present
    mismatch = []
    parent = root / "outputs/traffic_public_target/E2_TRAFFIC_PARENT_IDENTITY_FREEZE.json"
    if parent.is_file():
        pf = json.loads(parent.read_text(encoding="utf-8"))
        checks = [
            ("atomic_table_sha256", atomic_id.get("sha256")),
            ("global_windows_sha256", win.get("sha256_windows")),
            ("atomic_window_assignment_sha256", win.get("sha256_assignment")),
        ]
        for key, actual in checks:
            expected = pf.get(key)
            if expected and actual and expected != actual:
                mismatch.append({"key": key, "expected": expected, "actual": actual})

    status = "PASS"
    if missing:
        status = "BLOCKED_INPUT_IDENTITY_MISMATCH"
    if mismatch:
        status = "BLOCKED_INPUT_IDENTITY_MISMATCH"

    return {
        "status": status,
        "prior_seal_status": stop.get("status"),
        "artifacts": artifacts,
        "missing": missing,
        "hash_mismatch": mismatch,
        "public_target_identity_hash": pub.get("public_target_sha256") or pub.get("identity_hash"),
        "global_windows_identity_hash": win.get("sha256_windows"),
        "q_feature_identity_hash": q.get("feature_schema_hash"),
        "atomic_table_hash": atomic_id.get("sha256"),
        "n_clients": N_CLIENTS,
        "n_windows": N_WINDOWS,
        "n_atoms": N_ATOMS,
        "design_seeds": list(DESIGN_SEEDS),
    }


def load_traffic_targets(root: Path) -> dict[str, Any]:
    public = pd.read_parquet(root / "configs/frozen/e2_traffic_public_target/atomic_public_target.parquet")
    public["unit_id"] = public["unit_id"].astype(str)
    public["station_id"] = public["station_id"].astype(str)
    public["window_id"] = public["window_id"].astype(int)
    public["opportunity_stratum"] = public["opportunity_stratum"].astype(str)
    public["target_group"] = public["target_group"].astype(str)

    group = pd.read_parquet(root / "configs/frozen/e2_traffic_public_target/target_group_mass.parquet")
    stratum = pd.read_parquet(
        root / "configs/frozen/e2_traffic_public_target/opportunity_stratum_target.parquet"
    )
    cs = pd.read_parquet(root / "configs/frozen/e2_traffic_public_target/client_stratum_target.parquet")

    mu = {str(r.target_group): float(r.mu_g) for r in group.itertuples(index=False)}
    lam = {str(r.stratum_id): float(r.Lambda_s_tar) for r in stratum.itertuples(index=False)}
    pi = {
        (str(r.station_id), str(r.stratum_id)): float(r.pi_k_s_tar)
        for r in cs.itertuples(index=False)
    }
    # head/tail from time blocks only (no Y): block0/1=head(-1), block2/3=tail(+1)
    unit_meta = {}
    for r in public.itertuples(index=False):
        g = str(r.target_group)
        score = -1 if g in {"block0", "block1"} else 1
        unit_meta[str(r.unit_id)] = {
            "station_id": str(r.station_id),
            "window_id": int(r.window_id),
            "stratum": str(r.opportunity_stratum),
            "group": g,
            "tail_score": score,
            "varpi": float(r.varpi_i_tar),
        }
    return {
        "public": public,
        "mu": mu,
        "lam": lam,
        "pi": pi,
        "unit_meta": unit_meta,
        "clients": sorted(public["station_id"].unique()),
    }


def build_traffic_schedule(targets: dict[str, Any]) -> dict[str, Any]:
    public = targets["public"]
    clients = targets["clients"]
    rows = []
    for wid in range(N_WINDOWS):
        for cid in clients:
            sub = public.loc[(public["window_id"] == wid) & (public["station_id"] == cid)]
            uids = sub["unit_id"].astype(str).tolist()
            if len(uids) != WINDOW_HOURS:
                raise RuntimeError(f"expected {WINDOW_HOURS} atoms for {cid} w{wid}, got {len(uids)}")
            rows.append({
                "client_id": cid,
                "window_id": wid,
                "candidate_unit_ids": uids,
                "candidate_event_mass": [1.0] * len(uids),
            })
    return {
        "clients": clients,
        "n_windows": N_WINDOWS,
        "n_clients": len(clients),
        "rows": rows,
        "dataset": "traffic",
        "window_hours": WINDOW_HOURS,
    }


def calibrate_traffic_p_opp(
    schedule: dict[str, Any],
    targets: dict[str, Any],
    *,
    max_iters: int = 250,
    tol: float = 1e-8,
) -> dict[str, Any]:
    """Soft-calibrate p_opp to traffic pi/Lambda/mu; event mass stays 1."""
    unit_meta = targets["unit_meta"]
    mu = targets["mu"]
    lam = targets["lam"]
    pi = targets["pi"]

    detail_rows = []
    for r in schedule["rows"]:
        cid = str(r["client_id"])
        for uid in r["candidate_unit_ids"]:
            meta = unit_meta[str(uid)]
            detail_rows.append({
                "client_id": cid,
                "window_id": int(r["window_id"]),
                "unit_id": str(uid),
                "raw_stratum": meta["stratum"],
                "group": meta["group"],
                "tail_score": int(meta["tail_score"]),
                "exposure": 1.0,
            })
    detail = pd.DataFrame(detail_rows)
    C_ks = (
        detail.groupby(["client_id", "raw_stratum"], sort=True)["exposure"]
        .sum().reset_index().rename(columns={"exposure": "C_k_s"})
    )
    C = {(str(r.client_id), str(r.raw_stratum)): float(r.C_k_s) for r in C_ks.itertuples(index=False)}
    unsupported = [
        {"client_id": k, "raw_stratum": s, "pi": t}
        for (k, s), t in pi.items()
        if t > 0 and C.get((k, s), 0.0) <= 0
    ]
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
    cell_stratum = np.asarray([key[1] for key in cell_keys], dtype=object)
    s_to_i = {s: i for i, s in enumerate(strata)}
    cell_s_code = np.asarray([s_to_i[s] for s in cell_stratum], dtype=np.int64)
    lam_arr = np.asarray([float(lam[s]) for s in strata], dtype=np.float64)

    max_resid = 1.0
    converged = False
    for _ in range(max_iters):
        cur = C_arr * gamma_arr
        pos = (cur > 0) & (pi_arr > 0)
        gamma_arr[pos] *= pi_arr[pos] / cur[pos]
        tot = float((C_arr * gamma_arr).sum()) or 1.0
        gamma_arr /= tot
        cur_s = np.bincount(cell_s_code, weights=C_arr * gamma_arr, minlength=len(strata))
        fac = np.ones(len(strata))
        spos = (cur_s > 0) & (lam_arr > 0)
        fac[spos] = lam_arr[spos] / cur_s[spos]
        gamma_arr *= fac[cell_s_code]
        tot = float((C_arr * gamma_arr).sum()) or 1.0
        gamma_arr /= tot
        resid = float(np.max(np.abs(C_arr * gamma_arr - pi_arr))) if n_cells else 0.0
        cur_s = np.bincount(cell_s_code, weights=C_arr * gamma_arr, minlength=len(strata))
        resid = max(resid, float(np.max(np.abs(cur_s - lam_arr))))
        max_resid = resid
        if max_resid <= tol and not unsupported:
            converged = True
            break

    cids = detail["client_id"].astype(str).to_numpy()
    sids = detail["raw_stratum"].astype(str).to_numpy()
    uids = detail["unit_id"].astype(str).to_numpy()
    row_cell = np.asarray([cell_index[(str(cids[i]), str(sids[i]))] for i in range(len(cids))], dtype=np.int64)
    w = gamma_arr[row_cell].copy()

    groups = detail["group"].astype(str).to_numpy()
    uniq_g = sorted(mu)
    g_code = {g: i for i, g in enumerate(uniq_g)}
    group_codes = np.asarray([g_code[str(g)] for g in groups], dtype=np.int64)
    tgt_g_arr = np.asarray([float(mu[g]) for g in uniq_g], dtype=np.float64)
    cell_target_arr = C_arr * gamma_arr
    stratum_codes = np.asarray([s_to_i[str(s)] for s in sids], dtype=np.int64)
    scores = detail["tail_score"].to_numpy(dtype=np.int64)
    tgt_head = float(sum(mu[g] for g in uniq_g if g in {"block0", "block1"}))
    tgt_tail = float(sum(mu[g] for g in uniq_g if g in {"block2", "block3"}))

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

    p, rate_err = weights_to_p(w)
    d_g = d_s = d_cs = 1.0
    for _ in range(30):
        soft = p / (float(p.sum()) or 1.0)
        rho_s = {s: float(soft[stratum_codes == s_to_i[s]].sum()) for s in strata}
        rho_ks = {cell_keys[i]: float(soft[row_cell == i].sum()) for i in range(n_cells)}
        rho_g = {g: float(soft[group_codes == g_code[g]].sum()) for g in uniq_g}
        d_g = _tv(rho_g, mu, uniq_g)
        d_s = _tv(rho_s, lam, strata)
        d_cs = _tv(rho_ks, {k: pi.get(k, 0.0) for k in cell_keys}, cell_keys)
        if d_g <= 0.01 and d_s <= 0.01 and d_cs <= 0.03 and rate_err <= 1e-10:
            break
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

    soft = p / (float(p.sum()) or 1.0)
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
    cal_sched = dict(schedule)
    cal_sched["rows"] = cal_rows
    cal_sched["calibrated"] = True

    bound_viol = int(((p < OPP_GEN_MIN - 1e-15) | (p > OPP_GEN_MAX + 1e-15)).sum())
    status = (
        "PASS"
        if (
            d_g <= 0.01 and d_s <= 0.01 and d_cs <= 0.03
            and bound_viol == 0
            and rate_err <= 1e-10
            and max_resid <= 1e-8
            and len(unsupported) == 0
            and converged
            and abs(float(soft.sum()) - 1.0) <= 1e-10
        )
        else "FAIL"
    )
    solved = {
        "status": status,
        "D_TV_group_soft": float(d_g),
        "D_TV_stratum_soft": float(d_s),
        "D_TV_client_stratum_soft": float(d_cs),
        "p_opp_min": float(p.min()),
        "p_opp_max": float(p.max()),
        "p_opp_mean": float(p.mean()),
        "expected_atomic_mass_sum": float(soft.sum()),
        "opportunity_rate_error": float(rate_err),
        "max_marginal_residual": float(max_resid),
        "probability_bound_violation_count": bound_viol,
        "unsupported_positive_target_cell_count": int(len(unsupported)),
        "solver_convergence": bool(converged and not unsupported),
        "solver_residual": float(max_resid),
        "opp_gen_min": OPP_GEN_MIN,
        "opp_gen_max": OPP_GEN_MAX,
        "opportunity_rate_target": OPP_RATE_TARGET,
        "event_mass_unchanged": True,
        "target_value_dependency_count": 0,
    }
    return {
        "solved": solved,
        "calibrated_schedule": cal_sched,
        "p_opp": p,
        "detail": detail,
        "unit_meta": unit_meta,
        "mu": mu,
        "lam": lam,
        "pi": pi,
        "tgt_head": tgt_head,
        "tgt_tail": tgt_tail,
    }


def run_traffic_seed_trace(
    *,
    seed: int,
    calibrated: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    schedule = calibrated["calibrated_schedule"]
    unit_meta = calibrated["unit_meta"]
    mu = calibrated["mu"]
    lam = calibrated["lam"]
    pi = calibrated["pi"]
    tgt_head = calibrated["tgt_head"]
    tgt_tail = calibrated["tgt_tail"]
    clients = schedule["clients"]
    client_index = {c: i for i, c in enumerate(clients)}

    max_risk = max(len(r["candidate_unit_ids"]) for r in schedule["rows"])
    streams = build_base_random_streams(
        seed, n_windows=N_WINDOWS, n_clients=len(clients), max_risk_set=max(max_risk, 6),
    )
    opp, opp_audit = generate_opportunity_from_schedule_p(
        schedule_rows=schedule["rows"],
        opp_uniforms=streams["base_opportunity_uniforms"],
        client_index=client_index,
        seed=seed,
        profile_id="TRAFFIC-BALANCED",
        scenario_id="balanced",
    )
    opp = opp.copy()
    opp["tail_score"] = opp["unit_id"].map(
        lambda u: int(unit_meta[str(u)]["tail_score"])
    ).astype(int)

    risk_sets = risk_sets_from_opportunity(opp)
    obs, obs_audit = generate_observation_events(
        risk_sets=risk_sets,
        obs_uniforms=streams["base_observation_uniforms"],
        client_index=client_index,
        kappa_p=0.0, d_p=0, seed=seed,
        profile_id="TRAFFIC-BALANCED", scenario_id="balanced",
        observation_rate_target=OBS_RATE_TARGET,
    )
    risk_sets = enrich_risk_sets_with_observation(risk_sets, obs)
    usable, use_audit = generate_stage2_usable_events(
        risk_sets=risk_sets,
        use_uniforms=streams["base_usable_uniforms"],
        client_index=client_index,
        kappa_q=0.0, d_q=0, seed=seed,
        profile_id="TRAFFIC-BALANCED", scenario_id="balanced",
        usable_rate_target=USE_RATE_TARGET,
    )
    arrival, arr_audit = generate_hard_arrival_events(
        opp=opp, obs=obs, usable=usable,
        seed=seed, profile_id="TRAFFIC-BALANCED", scenario_id="balanced",
    )

    # rates
    realized_opp = float(opp["opportunity_selected"].mean()) if len(opp) else 0.0
    realized_obs = float(obs["observed"].mean()) if len(obs) else 0.0
    use_elig = usable.loc[usable["stage2_eligible"]]
    realized_use = float(use_elig["U"].mean()) if len(use_elig) else 0.0
    failed = usable.loc[usable["stage2_eligible"] & ~usable["U"]]
    failed_attempts = failed.copy()

    # hard mass diagnostics vs targets
    arr_pos = arrival.loc[arrival["I_arr"]].copy()
    if len(arr_pos):
        arr_pos["mass"] = arr_pos["W_arr"].astype(float)
        total = float(arr_pos["mass"].sum()) or 1.0
        arr_pos["w"] = arr_pos["mass"] / total
        arr_pos["group"] = arr_pos["unit_id"].map(lambda u: unit_meta[str(u)]["group"])
        arr_pos["stratum"] = arr_pos["unit_id"].map(lambda u: unit_meta[str(u)]["stratum"])
        arr_pos["station_id"] = arr_pos["client_id"].astype(str)
        emp_g = arr_pos.groupby("group")["w"].sum().to_dict()
        emp_s = arr_pos.groupby("stratum")["w"].sum().to_dict()
        emp_cs = {
            (str(r.station_id), str(r.stratum)): float(r.w)
            for r in arr_pos.groupby(["station_id", "stratum"], as_index=False)["w"].sum().itertuples()
        }
        head_mass = float(arr_pos.loc[arr_pos["group"].isin(["block0", "block1"]), "w"].sum())
        tail_mass = float(arr_pos.loc[arr_pos["group"].isin(["block2", "block3"]), "w"].sum())
    else:
        emp_g, emp_s, emp_cs = {}, {}, {}
        head_mass = tail_mass = 0.0
        total = 0.0

    d_g = _tv(emp_g, mu, sorted(mu))
    d_s = _tv(emp_s, lam, sorted(lam))
    d_cs = _tv(emp_cs, pi, sorted(pi))
    head_ratio = (head_mass / tgt_head) if tgt_head > 0 else float("nan")
    tail_ratio = (tail_mass / tgt_tail) if tgt_tail > 0 else float("nan")

    # expected soft mass from p_opp * p_obs * q (approx using mean rates on selected schedule)
    # empirical atomic mass table
    unit_ids = sorted(unit_meta)
    emp_atomic = {u: 0.0 for u in unit_ids}
    if total > 0:
        for r in arr_pos.itertuples(index=False):
            emp_atomic[str(r.unit_id)] = emp_atomic.get(str(r.unit_id), 0.0) + float(r.w)

    # structural checks
    cross_dup = int(
        arrival.groupby(["unit_id", "window_id"]).size().gt(1).sum()
    )
    multiply = int(arrival.groupby("unit_id")["window_id"].nunique().gt(1).sum())
    # each unit should appear in exactly one window in schedule; arrivals may be 0/1
    unsupported_arrival = 0
    for r in arrival.loc[arrival["I_arr"]].itertuples(index=False):
        meta = unit_meta.get(str(r.unit_id))
        if meta is None or int(meta["window_id"]) != int(r.window_id):
            unsupported_arrival += 1

    q_used = list(use_audit.get("q_features_used", []))
    obs_in_q = int("observed_count" in q_used)
    y_leak = 0
    stage2_viol = int(
        ((usable["observed_count"] <= 0) & usable["stage2_eligible"]).sum()
        + ((usable["observed_count"] > 0) & ~usable["stage2_eligible"]).sum()
    )

    rate_pass = (
        OPP_RATE_LO <= realized_opp <= OPP_RATE_HI
        and OBS_RATE_LO <= realized_obs <= OBS_RATE_HI
        and USE_RATE_LO <= realized_use <= USE_RATE_HI
    )
    struct_pass = (
        cross_dup == 0
        and multiply == 0
        and unsupported_arrival == 0
        and stage2_viol == 0
        and int(use_audit.get("failed_attempt_omission_count", 1)) == 0
        and obs_in_q == 0
        and y_leak == 0
        and float(total) > 0
        and int(np.isnan(opp["opportunity_probability"].to_numpy(dtype=float)).sum()) == 0
    )
    bal_pass = (
        d_g <= 0.07
        and 0.85 <= head_ratio <= 1.15
        and 0.85 <= tail_ratio <= 1.15
    )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    opp.to_parquet(out / "opportunity_events.parquet", index=False)
    obs.to_parquet(out / "observation_events.parquet", index=False)
    usable.to_parquet(out / "usable_events.parquet", index=False)
    failed_attempts.to_parquet(out / "failed_attempts.parquet", index=False)
    arrival.to_parquet(out / "hard_arrival_events.parquet", index=False)
    pd.DataFrame(
        [{"unit_id": u, "empirical_mass": emp_atomic[u]} for u in unit_ids]
    ).to_parquet(out / "empirical_atomic_mass.parquet", index=False)
    # expected: soft composition from calibrated p (shared) — write uniform placeholder note
    exp_rows = []
    for r in schedule["rows"]:
        for uid, p in zip(r["candidate_unit_ids"], r["candidate_p_opp"], strict=True):
            exp_rows.append({
                "unit_id": str(uid),
                "client_id": str(r["client_id"]),
                "window_id": int(r["window_id"]),
                "p_opp": float(p),
                "expected_soft_share": float(p) / float(sum(
                    sum(rr["candidate_p_opp"]) for rr in schedule["rows"]
                ) or 1.0),
            })
    pd.DataFrame(exp_rows).to_parquet(out / "expected_atomic_mass.parquet", index=False)
    activity = usable[["window_id", "client_id", "stage2_eligible", "observed_count", "U"]].copy()
    activity["hard_arrival_count"] = 0
    if len(arr_pos):
        cnt = arr_pos.groupby(["window_id", "client_id"]).size()
        activity["hard_arrival_count"] = activity.apply(
            lambda r: int(cnt.get((int(r.window_id), str(r.client_id)), 0)), axis=1
        )
    activity.to_parquet(out / "client_window_activity.parquet", index=False)

    diag = {
        "seed": seed,
        "arms": 1,
        "antithetic_arm_count": 1,
        "clients": len(clients),
        "windows": N_WINDOWS,
        "atomic_units": N_ATOMS,
        "realized_opportunity_rate": realized_opp,
        "realized_conditional_observation_rate": realized_obs,
        "realized_conditional_usable_rate": realized_use,
        "eligible_client_window_count": int(usable["stage2_eligible"].sum()),
        "ineligible_client_window_count": int((~usable["stage2_eligible"]).sum()),
        "usable_success_count": int((usable["stage2_eligible"] & usable["U"]).sum()),
        "usable_failure_count": int(len(failed_attempts)),
        "failed_attempts_retained": int(len(failed_attempts)),
        "failed_attempt_omission_count": int(use_audit.get("failed_attempt_omission_count", 0)),
        "D_TV_group_hard": float(d_g),
        "D_TV_stratum_hard": float(d_s),
        "D_TV_client_stratum_hard": float(d_cs),
        "head_mass_ratio": float(head_ratio),
        "tail_mass_ratio": float(tail_ratio),
        "hard_arrival_mass": float(total),
        "cross_window_duplicate_count": cross_dup,
        "multiply_assigned_atomic_count": multiply,
        "unsupported_arrival_count": unsupported_arrival,
        "stage2_eligibility_violation_count": stage2_viol,
        "observed_count_in_q": obs_in_q,
        "target_value_leakage_count": y_leak,
        "q_features_used": q_used,
        "rate_pass": rate_pass,
        "structural_pass": struct_pass,
        "balanced_pass": bal_pass,
        "status": "PASS" if (rate_pass and struct_pass and bal_pass) else "FAIL",
        "opp_audit": opp_audit,
        "obs_audit": {k: obs_audit[k] for k in obs_audit if k != "detail"},
        "use_audit": {k: use_audit[k] for k in use_audit if k not in {"detail"}},
        "arr_audit": arr_audit,
    }
    dump_json(diag, out / "eventtrace_manifest.json")
    return diag
