"""W1 same-support frontier and necessity ladder — Phase 1/3 driver.

Protocol: raven-mcs-w1-ladder-frontier-execution-prompt.md (attachment, sha256 a26c6388…).
Round v1 (results_w1_ladder/round_v1/) implemented Phase 1 as specified and stopped at G1
because raven_wo_inst stores an empty p2_invocation_states.json.  The user approved amending
G1; round v2 (results_w1_ladder/round_v2/PREREG.md, sha256 48fc1f3f…) restricts the
cross-arm invariance check to the state-bearing Design-on arms (wo_debt, wo_use, wo_obs) and
records raven_wo_inst as excluded.  Everything else is unchanged.

Phase 3 (this file) computes the same-support hindsight frontier per ruler:
  d*_group = min_{alpha_r in C_r} || (1/S) sum_r M_r alpha_r - mu ||_1
  d*_cs    = min_{alpha_r in C_r} sum_{k,s} | (1/S) sum_r alpha_{k,r} w_{k,r,s} - pi^tar_{k,s} |
plus the joint sweep min d_group + lambda d_cs, the uniform anchor, the group-myopic sequence
and the arm-level G_F fractions.  C_r uses raven_mcs.aggregation.feasibility with
alpha_max = 0.5 and e_min = 3 (== min(3, K_r) inside ess_ball_bound); solver CLARABEL.

Read-only with respect to the repository: writes only inside results_w1_ladder/<round>/.
No training, no src/ or manuscript edits, no writes to artifacts/ or existing result dirs.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import cvxpy as cp
import numpy as np
import pandas as pd
from scipy import sparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.aggregation import alpha_bar, ess_ball_bound                            # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client  # noqa: E402
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import build_pi_tar_client_stratum          # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v2"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
DS = ("sensorscope", "uair")
SEEDS = list(range(30001, 30021))
TUNE, REPORT = SEEDS[:10], SEEDS[10:]
TOL_M, TOL_ENDPOINT = 1e-12, 1e-9

# --- G1 (amended in round v2): state-bearing Design-on arms only -------------------------
G1_ARMS = ("raven_wo_debt", "raven_wo_use", "raven_wo_obs")
G1_EXCLUDED = ("raven_wo_inst",)          # empty p2_invocation_states.json (0 vs 92-98 / 66-74)
STATE_ARMS = G1_ARMS
R_ON_SOURCE = "raven_wo_debt"
G2_E4 = ("raven_wo_debt", "raven_wo_use", "raven_wo_obs", "raven_wo_design")
G2_E3 = ("raven", "inst_cal", "twostage_hajek", "local_hajek")

# --- Phase 3 constants -------------------------------------------------------------------
ALPHA_MAX = 0.5
E_MIN = 3.0
LAMBDAS = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0, float("inf"))
RULERS = (("R_on", "raven_wo_debt"), ("R_offp", "raven_wo_design"))
ARMS_E4 = ("raven_wo_debt", "raven_wo_use", "raven_wo_obs", "raven_wo_design")
ARMS_E3 = ("raven", "inst_cal", "debt_cal", "twostage_hajek", "local_hajek")
# Arms that solve P2 themselves (must live in C_r up to solver tolerance) vs baselines that
# do not (their alpha is outside C_r by construction; the F1 gate must not bind on them).
P2_ARMS = ("raven_wo_debt", "raven_wo_use", "raven_wo_obs", "raven_wo_design", "raven",
           "inst_cal", "debt_cal")
BASELINE_ARMS = ("twostage_hajek", "local_hajek")
BALL_VIOL_TOL = 1e-7
G_F_DEGENERATE = 1e-6

_myopic_cache: dict = {}


def load_json(p: pathlib.Path):
    return json.loads(p.read_text(encoding="utf-8"))


def active_windows(wm: list) -> list:
    return [w for w in wm if w.get("active")]


def pi_tar_for(ds_name: str) -> dict:
    ds = load_paper_dataset(ROOT, ds_name)
    mapping = load_spatial_to_client(ROOT, ds_name)
    atomic = pd.read_parquet(ROOT / "data/processed" / ds_name / "atomic_units.parquet")
    return build_pi_tar_client_stratum(atomic, mapping, split="test")


def delta_group(mats: list, alphas: list, mu: np.ndarray) -> float:
    omega = np.mean([m @ a for m, a in zip(mats, alphas)], axis=0)
    return float(np.abs(omega - mu).sum())


def delta_cs(pair_state: pd.DataFrame, alphas_by_window: dict, S: int, pi_tar: dict):
    ps = pair_state.copy()
    ps["a"] = [float(alphas_by_window.get(int(w), {}).get(str(c), np.nan))
               for w, c in zip(ps["window"], ps["client_id"])]
    ps = ps[ps["a"].notna()]
    if ps.empty:
        return None
    key = ps["client_id"].astype(str) + "::" + ps["opportunity_stratum_id"].astype(str)
    agg = (ps["a"] * ps["w_atomic"].astype(float)).groupby(key).sum() / float(S)
    tot = float(agg.sum())
    if tot > 0:
        agg = agg / tot
    keys = set(agg.index) | set(pi_tar.keys())
    return float(sum(abs(float(agg.get(k, 0.0)) - float(pi_tar.get(k, 0.0))) for k in keys))


def alpha_map_from_wm(wm_row: dict) -> dict:
    al = list(wm_row.get("alpha") or [])
    cl = list(wm_row.get("active_clients") or [])
    return {str(c): float(v) for c, v in zip(cl, al)}


# =========================================================================================
# Phase 1
# =========================================================================================

def phase1() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pi = {d: pi_tar_for(d) for d in DS}
    ruler_rows, gate_rows, dev_rows = [], [], []
    g1_mismatch = []
    for d in DS:
        for seed in SEEDS:
            base_paths = {a: E4 / d / a / f"seed{seed}" for a in
                          ("raven_wo_debt", "raven_wo_use", "raven_wo_inst",
                           "raven_wo_obs", "raven_wo_design")}
            if not all((p / "window_metrics.json").is_file() for p in base_paths.values()):
                ruler_rows.append({"dataset": d, "seed": seed, "status": "missing_runs"})
                continue
            wms = {a: load_json(p / "window_metrics.json") for a, p in base_paths.items()}
            states = {a: (load_json(base_paths[a] / "p2_invocation_states.json")
                          if (base_paths[a] / "p2_invocation_states.json").is_file() else [])
                      for a in base_paths}
            counts = {a: (len(states[a]), len(active_windows(wms[a]))) for a in G1_ARMS}
            bad = {a: v for a, v in counts.items() if v[0] != v[1]}
            if bad:
                g1_mismatch.append({"dataset": d, "seed": seed,
                                    "counts": {k: list(v) for k, v in bad.items()}})
            # ---- invariance across the state-bearing Design-on arms
            have = [a for a in STATE_ARMS if len(states[a]) > 0]
            dev = {"dataset": d, "seed": seed, "arms_with_states": have,
                   "max_M_diff": None, "max_w_diff": None, "active_clients_equal": None}
            if len(have) >= 2:
                ref = have[0]
                n = min(len(states[a]) for a in have)
                max_m, clients_equal = 0.0, True
                for j in range(n):
                    cls = [tuple(active_windows(wms[a])[j]["active_clients"]) for a in have]
                    if len(set(cls)) != 1:
                        clients_equal = False
                    for a in have[1:]:
                        Ma = np.asarray(states[ref][j]["M"], dtype=float)
                        Mb = np.asarray(states[a][j]["M"], dtype=float)
                        max_m = (max(max_m, float(np.max(np.abs(Ma - Mb))))
                                 if Ma.shape == Mb.shape else float("inf"))
                max_w = 0.0
                pss = {}
                for a in have:
                    f = base_paths[a] / "pair_state.parquet"
                    pss[a] = pd.read_parquet(f) if f.is_file() else None
                if all(v is not None and len(v) for v in pss.values()):
                    kc = ["window", "client_id", "atomic_unit_id"]
                    merged = pss[ref][kc + ["w_atomic"]].rename(columns={"w_atomic": "w0"})
                    for a in have[1:]:
                        m = merged.merge(pss[a][kc + ["w_atomic"]].rename(columns={"w_atomic": "wa"}),
                                         on=kc, how="outer")
                        max_w = (float("inf") if m[["w0", "wa"]].isna().any().any()
                                 else max(max_w, float(np.max(np.abs(m["w0"] - m["wa"])))))
                dev.update({"max_M_diff": max_m, "max_w_diff": max_w,
                            "active_clients_equal": clients_equal,
                            "n_windows_compared": n})
            ruler_rows.append({"dataset": d, "seed": seed,
                               "status": "STOP_G1_count_mismatch" if bad else
                                         ("ok" if dev.get("max_M_diff") is not None else "no_states"),
                               "counts": {k: list(v) for k, v in counts.items()},
                               "arms_with_states": ",".join(have)})
            dev_rows.append(dev)

            # ---- G2: self-replay for arms with states
            for a in G2_E4:
                p = base_paths[a]
                if not len(states[a]):
                    gate_rows.append({"dataset": d, "arm": a, "seed": seed, "ruler": "self",
                                      "aligned_windows": 0, "n_active": len(active_windows(wms[a])),
                                      "d_group_err": None, "d_cs_err": None, "pass": False,
                                      "note": "no_states"})
                    continue
                act = active_windows(wms[a])
                n = min(len(states[a]), len(act))
                mats = [np.asarray(states[a][j]["M"], dtype=float) for j in range(n)]
                alps = [np.asarray(act[j]["alpha"], dtype=float) for j in range(n)]
                mu = np.asarray(states[a][0]["mu"], dtype=float)
                dg = delta_group(mats, alps, mu)
                psf = p / "pair_state.parquet"
                dcs = None
                if psf.is_file():
                    amap = {int(act[j]["window_id"]): alpha_map_from_wm(act[j]) for j in range(n)}
                    dcs = delta_cs(pd.read_parquet(psf), amap, n, pi[d])
                fm = load_json(p / "final_metrics.json")
                eg = abs(dg - float(fm["Delta_group"]))
                ec = abs(dcs - float(fm["Delta_c_s"])) if dcs is not None else None
                gate_rows.append({"dataset": d, "arm": a, "seed": seed, "ruler": "self",
                                  "aligned_windows": n, "n_active": len(act),
                                  "d_group_err": eg, "d_cs_err": ec,
                                  "pass": bool(eg <= TOL_ENDPOINT and ec is not None and ec <= TOL_ENDPOINT)})

            # ---- G2: E3 arms on the borrowed R_on ruler
            ref_states = states[R_ON_SOURCE]
            ref_act = active_windows(wms[R_ON_SOURCE])
            for a in G2_E3:
                p = E3 / d / a / f"seed{seed}"
                if not (p / "final_metrics.json").is_file():
                    continue
                wm = load_json(p / "window_metrics.json")
                act = active_windows(wm)
                aligned = (len(act) == len(ref_act) and
                           all(tuple(x["active_clients"]) == tuple(y["active_clients"])
                               for x, y in zip(act, ref_act)))
                fm = load_json(p / "final_metrics.json")
                if not aligned or not len(ref_states):
                    gate_rows.append({"dataset": d, "arm": a, "seed": seed, "ruler": "R_on",
                                      "aligned_windows": 0, "n_active": len(act),
                                      "d_group_err": None, "d_cs_err": None, "pass": False,
                                      "note": "ruler_misaligned" if not aligned else "no_states"})
                    continue
                n = min(len(ref_states), len(act))
                mats = [np.asarray(ref_states[j]["M"], dtype=float) for j in range(n)]
                alps = [np.asarray(act[j]["alpha"], dtype=float) for j in range(n)]
                mu = np.asarray(ref_states[0]["mu"], dtype=float)
                dg = delta_group(mats, alps, mu)
                psf = p / "pair_state.parquet"
                dcs = None
                if psf.is_file():
                    amap = {int(act[j]["window_id"]): alpha_map_from_wm(act[j]) for j in range(n)}
                    dcs = delta_cs(pd.read_parquet(psf), amap, n, pi[d])
                eg = abs(dg - float(fm["Delta_group"]))
                ec = abs(dcs - float(fm["Delta_c_s"])) if dcs is not None else None
                gate_rows.append({"dataset": d, "arm": a, "seed": seed, "ruler": "R_on",
                                  "aligned_windows": n, "n_active": len(act),
                                  "d_group_err": eg, "d_cs_err": ec,
                                  "pass": bool(eg <= TOL_ENDPOINT and ec is not None and ec <= TOL_ENDPOINT)})

    ruler = pd.DataFrame(ruler_rows)
    gate = pd.DataFrame(gate_rows)
    dev = pd.DataFrame(dev_rows)
    ruler.to_csv(OUT / "RULER_CHECK_seedlevel.csv", index=False)
    gate.to_csv(OUT / "REPLAY_GATE.csv", index=False)
    dev.to_csv(OUT / "RULER_INVARIANCE_deviation.csv", index=False)

    def col(df, name):
        return df[name] if name in df.columns else pd.Series(dtype=float)

    summary = {
        "round": OUT.name,
        "g1_arms": list(G1_ARMS),
        "g1_excluded_missing_states": list(G1_EXCLUDED),
        "status": "STOP_G1_count_mismatch" if g1_mismatch else "G1_v2_pass",
        "g1_count_mismatch_cells": len(g1_mismatch),
        "g1_mismatch_examples": g1_mismatch[:4],
        "invariance_max_M_diff": float(np.nanmax(col(dev, "max_M_diff").astype(float))) if len(dev) and col(dev, "max_M_diff").notna().any() else None,
        "invariance_max_w_diff": float(np.nanmax(col(dev, "max_w_diff").astype(float))) if len(dev) and col(dev, "max_w_diff").notna().any() else None,
        "invariance_active_clients_all_equal": bool(col(dev, "active_clients_equal").dropna().all()) if len(dev) and col(dev, "active_clients_equal").notna().any() else None,
        "g2_rows": int(len(gate)),
        "g2_pass": int(col(gate, "pass").sum()) if len(gate) else 0,
        "g2_max_d_group_err": float(col(gate, "d_group_err").dropna().max()) if len(gate) and col(gate, "d_group_err").notna().any() else None,
        "g2_max_d_cs_err": float(col(gate, "d_cs_err").dropna().max()) if len(gate) and col(gate, "d_cs_err").notna().any() else None,
        "g2_notes": col(gate, "note").value_counts().to_dict() if "note" in gate.columns else {},
    }
    (OUT / "RULER_CHECK.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))
    if len(gate):
        bad = gate[~gate["pass"]]
        if len(bad):
            print("non-passing G2 rows:", len(bad))
            print(bad.head(12).to_string())


# =========================================================================================
# Phase 3
# =========================================================================================

def build_case(d: str, ruler: str, src_arm: str, seed: int, pi_tar: dict) -> dict | None:
    """Assemble M_r, mu, alpha_r and the c-s structure on one ruler for one seed."""
    p = E4 / d / src_arm / f"seed{seed}"
    if not (p / "p2_invocation_states.json").is_file():
        return None
    states = load_json(p / "p2_invocation_states.json")
    act = active_windows(load_json(p / "window_metrics.json"))
    n = min(len(states), len(act))
    if n == 0:
        return None
    M = [np.asarray(states[j]["M"], dtype=float) for j in range(n)]
    mu = np.asarray(states[0]["mu"], dtype=float)
    G = mu.shape[0]
    clients = [[str(c) for c in act[j]["active_clients"]] for j in range(n)]
    wids = [int(act[j]["window_id"]) for j in range(n)]
    a_bar = [alpha_bar(alpha_max=ALPHA_MAX, n_active=len(c)) for c in clients]
    e_bar = [ess_ball_bound(e_min=E_MIN, n_active=len(c)) for c in clients]

    ps = pd.read_parquet(p / "pair_state.parquet")
    ps["client_id"] = ps["client_id"].astype(str)
    W, wsum, units, eta = [], [], [], []
    for j in range(n):
        sub = ps[(ps["window"] == wids[j]) & (ps["client_id"].isin(clients[j]))]
        key = sub["client_id"] + "::" + sub["opportunity_stratum_id"].astype(str)
        g = sub["w_atomic"].astype(float).groupby(key).sum()
        W.append({str(k): float(v) for k, v in g.items()})
        wsum.append(float(g.sum()))
        cnt = sub.groupby("client_id").size()
        units.append([int(cnt.get(c, 0)) for c in clients[j]])
        eta.append(float(sub["eta_r"].iloc[0]) if len(sub) else 1.0)

    beta = [np.asarray(states[j]["beta"], dtype=float) for j in range(n)]
    variance = [np.asarray(states[j]["variance"], dtype=float) for j in range(n)]
    staleness = [np.asarray(states[j]["staleness"], dtype=float) for j in range(n)]
    debt = [np.asarray(states[j]["debt"], dtype=float) for j in range(n)]
    lams = dict(states[0]["lambdas"])

    keys = {str(k): i for i, k in enumerate(pi_tar.keys())}
    rows, cols, vals, col = [], [], [], 0
    A_g_cols = []
    for j in range(n):
        for i, c in enumerate(clients[j]):
            A_g_cols.append(M[j][:, i].reshape(-1, 1) / float(n))
            for k, w in W[j].items():
                if k.split("::")[0] == c:
                    idx = keys.setdefault(k, len(keys))
                    rows.append(idx)
                    cols.append(col)
                    vals.append(w / float(n))
            col += 1
    N = col
    A_g = np.concatenate(A_g_cols, axis=1) if A_g_cols else np.zeros((G, 0))
    A_cs = sparse.csr_matrix((vals, (rows, cols)), shape=(len(keys), N))
    pi_vec = np.zeros(len(keys))
    for k, i in keys.items():
        pi_vec[i] = float(pi_tar.get(k, 0.0))

    alpha_arm = np.concatenate([np.asarray(act[j]["alpha"], dtype=float) for j in range(n)])
    return dict(dataset=d, ruler=ruler, seed=seed, src_arm=src_arm, M=M, mu=mu, G=G,
                clients=clients, wids=wids, a_bar=a_bar, e_bar=e_bar, W=W, wsum=wsum,
                units=units, eta=eta, beta=beta, variance=variance, staleness=staleness,
                debt=debt, lambdas=lams,
                A_g=A_g, A_cs=A_cs, pi_vec=pi_vec, alpha_arm=alpha_arm, n=n, N=N,
                pair_state=ps, pi_tar=pi_tar)


def cr_violation(alpha: np.ndarray, case: dict) -> dict:
    """Max violation of an alpha sequence against C_r = {sum=1, a>=0, a<=a_bar, ||a||^2<=1/e_bar}."""
    off, v_sum, v_lo, v_hi, v_ball = 0, 0.0, 0.0, 0.0, 0.0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        a = alpha[off:off + K]
        off += K
        v_sum = max(v_sum, abs(float(a.sum()) - 1.0))
        v_lo = max(v_lo, float(max(0.0, -a.min())))
        v_hi = max(v_hi, float(max(0.0, a.max() - case["a_bar"][j])))
        v_ball = max(v_ball, float(max(0.0, float(a @ a) - 1.0 / case["e_bar"][j])))
    return {"sum": v_sum, "lower": v_lo, "upper": v_hi, "ball": v_ball,
            "max": max(v_sum, v_lo, v_hi, v_ball)}


def solve_joint(case: dict, lams=LAMBDAS) -> list:
    alpha = cp.Variable(case["N"], nonneg=True)
    cons, off = [], 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        blk = alpha[off:off + K]
        cons += [cp.sum(blk) == 1.0, blk <= case["a_bar"][j],
                 cp.sum_squares(blk) <= 1.0 / case["e_bar"][j]]
        off += K
    g_expr = cp.norm1(cp.Constant(case["A_g"]) @ alpha - case["mu"])
    cs_expr = cp.norm1(cp.Constant(case["A_cs"]) @ alpha - case["pi_vec"])
    lam_par = cp.Parameter(nonneg=True)
    prob = cp.Problem(cp.Minimize(g_expr + lam_par * cs_expr), cons)
    prob_inf = cp.Problem(cp.Minimize(cs_expr), cons)
    out = []
    for lam in lams:
        t0 = time.perf_counter()
        if lam == float("inf"):
            prob_inf.solve(solver=cp.CLARABEL, verbose=False)
            status, gv, cv_, av = prob_inf.status, float(g_expr.value), float(cs_expr.value), alpha.value
        else:
            lam_par.value = float(lam)
            prob.solve(solver=cp.CLARABEL, verbose=False)
            status, gv, cv_, av = prob.status, float(g_expr.value), float(cs_expr.value), alpha.value
        out.append({"lambda": lam, "front_group": gv, "front_cs": cv_, "status": str(status),
                    "alpha": None if av is None else np.asarray(av, dtype=float),
                    "solve_s": time.perf_counter() - t0})
    return out


def myopic_group(case: dict) -> np.ndarray:
    """Per-window argmin of ||M_r alpha - mu||_1 over C_r (protocol F3)."""
    out, off = [], 0
    for j in range(case["n"]):
        Mj, K = case["M"][j], len(case["clients"][j])
        ck = (case["G"], K)
        if ck not in _myopic_cache:
            par = cp.Parameter((case["G"], K))
            a = cp.Variable(K, nonneg=True)
            pr = cp.Problem(cp.Minimize(cp.norm1(par @ a - case["mu"])),
                            [cp.sum(a) == 1.0, a <= case["a_bar"][j],
                             cp.sum_squares(a) <= 1.0 / case["e_bar"][j]])
            _myopic_cache[ck] = (par, a, pr)
        par, a, pr = _myopic_cache[ck]
        par.value = Mj
        pr.solve(solver=cp.CLARABEL, verbose=False)
        out.append(np.asarray(a.value, dtype=float) if a.value is not None
                   else np.full(K, 1.0 / K))
        off += K
    return np.concatenate(out)


def endpoint_values(case: dict, alpha: np.ndarray) -> tuple:
    g = float(np.abs(case["A_g"] @ alpha - case["mu"]).sum())
    c = float(np.abs(case["A_cs"] @ alpha - case["pi_vec"]).sum())
    return g, c


def arm_endpoints(d: str, seed: int, arm: str, case: dict) -> dict | None:
    """Frozen endpoints of an arm whose support matches this ruler, plus C_r violation."""
    base = E4 if arm in ARMS_E4 else E3
    p = base / d / arm / f"seed{seed}"
    if not (p / "final_metrics.json").is_file():
        return None
    act = active_windows(load_json(p / "window_metrics.json"))
    if len(act) != case["n"] or any(tuple(str(c) for c in x["active_clients"]) !=
                                    tuple(case["clients"][j]) for j, x in enumerate(act)):
        return None
    fm = load_json(p / "final_metrics.json")
    a = np.concatenate([np.asarray(x["alpha"], dtype=float) for x in act])
    v = cr_violation(a, case)
    return {"d_group": float(fm["Delta_group"]), "d_cs": float(fm["Delta_c_s"]),
            "cr_violation_max": v["max"], "cr_violation": v}


def g_fraction(d_rule: float, d_unif: float, d_star: float):
    den = d_unif - d_star
    if den < G_F_DEGENERATE:
        return None
    return float((d_unif - d_rule) / den)


def phase3(limit: int | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pi = {d: pi_tar_for(d) for d in DS}
    front_rows, arm_rows, check_rows = [], [], []
    stop = []
    seeds = SEEDS if not limit else SEEDS[:limit]
    for d in DS:
        for ruler, src in RULERS:
            for seed in seeds:
                t0 = time.perf_counter()
                case = build_case(d, ruler, src, seed, pi[d])
                if case is None:
                    check_rows.append({"dataset": d, "ruler": ruler, "seed": seed,
                                       "status": "no_states"})
                    continue
                # -- C_r precondition: the ruler arm's own alpha must live in C_r
                v_ruler = cr_violation(case["alpha_arm"], case)
                # -- uniform anchor
                unif = np.concatenate([np.full(len(c), 1.0 / len(c)) for c in case["clients"]])
                d_unif_g, d_unif_c = endpoint_values(case, unif)
                # -- myopic (group objective), evaluated on both endpoints
                myo = myopic_group(case)
                d_myo_g, d_myo_c = endpoint_values(case, myo)
                # -- joint sweep
                sweep = solve_joint(case)
                d_star_g = min(r["front_group"] for r in sweep if np.isfinite(r["front_group"]))
                d_star_c = min(r["front_cs"] for r in sweep if np.isfinite(r["front_cs"]))
                st = ";".join(sorted({r["status"] for r in sweep}))
                # -- frozen-endpoint cross-check on the l=inf optimum
                a_inf = [r for r in sweep if r["lambda"] == float("inf")][0]["alpha"]
                cs_cross = None
                if a_inf is not None:
                    amap = {}
                    off = 0
                    for j in range(case["n"]):
                        K = len(case["clients"][j])
                        amap[case["wids"][j]] = {c: float(a_inf[off + i])
                                                 for i, c in enumerate(case["clients"][j])}
                        off += K
                    cs_frozen = delta_cs(case["pair_state"], amap, case["n"], case["pi_tar"])
                    cs_cross = None if cs_frozen is None else abs(cs_frozen - d_star_c)
                cs_unif_frozen = delta_cs(case["pair_state"],
                                          {case["wids"][j]: {c: float(1.0 / len(case["clients"][j]))
                                                             for c in case["clients"][j]}
                                           for j in range(case["n"])}, case["n"], case["pi_tar"])
                g_unif_frozen = delta_group(case["M"],
                                            [np.full(len(c), 1.0 / len(c)) for c in case["clients"]],
                                            case["mu"])
                check_rows.append({
                    "dataset": d, "ruler": ruler, "seed": seed, "status": "ok",
                    "n_windows": case["n"], "n_vars": case["N"], "n_keys": case["A_cs"].shape[0],
                    "n_groups": case["G"],
                    "w_mass_min": float(np.min(case["wsum"])), "w_mass_max": float(np.max(case["wsum"])),
                    "cr_viol_ruler_arm": v_ruler["max"], "cr_viol_parts": json.dumps(v_ruler),
                    "cs_frozen_vs_lp_inf": cs_cross,
                    "cs_unif_frozen_vs_lp": None if cs_unif_frozen is None else abs(cs_unif_frozen - d_unif_c),
                    "group_unif_frozen_vs_lp": abs(g_unif_frozen - d_unif_g),
                    "runtime_s": time.perf_counter() - t0})
                for r in sweep:
                    front_rows.append({"ds": d, "ruler": ruler, "seed": seed,
                                       "d_star_group": d_star_g, "d_star_cs": d_star_c,
                                       "d_unif_group": d_unif_g, "d_unif_cs": d_unif_c,
                                       "d_myo_group": d_myo_g, "d_myo_cs": d_myo_c,
                                       "lambda": r["lambda"], "front_group": r["front_group"],
                                       "front_cs": r["front_cs"], "solver_status": r["status"],
                                       "solve_s": round(r["solve_s"], 3)})
                # -- arms on this ruler + G_F
                for arm in ARMS_E4 + ARMS_E3:
                    ae = arm_endpoints(d, seed, arm, case)
                    if ae is None:
                        continue
                    cls = "p2" if arm in P2_ARMS else "baseline"
                    if ae["cr_violation_max"] > BALL_VIOL_TOL:
                        stop.append({"kind": "Cr_precondition_p2arm" if cls == "p2"
                                     else "Cr_outside_baseline",
                                     "dataset": d, "ruler": ruler, "seed": seed, "arm": arm,
                                     "violation": ae["cr_violation"]})
                    for F, key in (("group", "d_group"), ("cs", "d_cs")):
                        d_rule = ae[key]
                        d_u = d_unif_g if F == "group" else d_unif_c
                        d_s = d_star_g if F == "group" else d_star_c
                        if cls == "p2" and d_s > d_rule + 1e-7:
                            stop.append({"kind": "F1", "dataset": d, "ruler": ruler, "seed": seed,
                                         "arm": arm, "endpoint": F, "d_star": d_s, "d_arm": d_rule})
                        arm_rows.append({"ds": d, "ruler": ruler, "seed": seed, "arm": arm,
                                         "cr_class": cls, "endpoint": F, "d_rule": d_rule,
                                         "d_unif": d_u, "d_star": d_s,
                                         "G_F": g_fraction(d_rule, d_u, d_s),
                                         "cr_violation_max": ae["cr_violation_max"]})
    pd.DataFrame(front_rows).to_csv(OUT / "FRONTIER.csv", index=False)
    pd.DataFrame(arm_rows).to_csv(OUT / "FRONTIER_ARMS.csv", index=False)
    pd.DataFrame(check_rows).to_csv(OUT / "FRONTIER_CHECKS.csv", index=False)

    fr = pd.DataFrame(front_rows)
    ar = pd.DataFrame(arm_rows)
    ch = pd.DataFrame(check_rows)

    # --- G_F under both readings (protocol F2 literal per-seed ratio vs ratio of means) ----
    both = []
    if len(ar):
        for (dd, rr, arm, cls, ep), g in ar.groupby(["ds", "ruler", "arm", "cr_class", "endpoint"]):
            dr, du, dst = float(g["d_rule"].mean()), float(g["d_unif"].mean()), float(g["d_star"].mean())
            den = du - dst
            den_sd = float((g["d_unif"] - g["d_star"]).std(ddof=1)) if len(g) > 1 else float("nan")
            both.append({"ds": dd, "ruler": rr, "arm": arm, "cr_class": cls, "endpoint": ep,
                         "n_seeds": len(g), "d_rule": dr, "d_unif": du, "d_star": dst,
                         "d_unif_minus_rule": du - dr, "den": den, "den_sd": den_sd,
                         "den_cv": (den_sd / den) if den > 0 else float("inf"),
                         "G_ratio": (du - dr) / den if den >= G_F_DEGENERATE else None,
                         "G_meanratio": float(g["G_F"].mean()),
                         "G_meanratio_sd": float(g["G_F"].std(ddof=1)) if len(g) > 1 else None,
                         "G_fragile_small_den": bool(den > 0 and den_sd > 0.25 * den)})
        pd.DataFrame(both).to_csv(OUT / "G_F_BOTH.csv", index=False)

    kinds = pd.Series([s["kind"] for s in stop]).value_counts().to_dict() if stop else {}
    hard = [s for s in stop if s["kind"] in ("F1", "Cr_precondition_p2arm")]
    summary = {
        "round": OUT.name,
        "rulers": [r for r, _ in RULERS],
        "seeds": seeds,
        "status": "STOP_F1_or_Cr" if hard else "phase3_ok",
        "stop_kinds": kinds,
        "n_stop_hard": len(hard),
        "stops": hard[:8],
        "cells": int(ch["status"].eq("ok").sum()) if len(ch) else 0,
        "cs_frozen_vs_lp_inf_max": float(ch["cs_frozen_vs_lp_inf"].dropna().max()) if len(ch) and ch["cs_frozen_vs_lp_inf"].notna().any() else None,
        "cs_unif_frozen_vs_lp_max": float(ch["cs_unif_frozen_vs_lp"].dropna().max()) if len(ch) and ch["cs_unif_frozen_vs_lp"].notna().any() else None,
        "group_unif_frozen_vs_lp_max": float(ch["group_unif_frozen_vs_lp"].dropna().max()) if len(ch) and ch["group_unif_frozen_vs_lp"].notna().any() else None,
        "cr_viol_ruler_arm_max": float(ch["cr_viol_ruler_arm"].dropna().max()) if len(ch) and ch["cr_viol_ruler_arm"].notna().any() else None,
        "w_mass_min": float(ch["w_mass_min"].dropna().min()) if len(ch) and ch["w_mass_min"].notna().any() else None,
        "w_mass_max": float(ch["w_mass_max"].dropna().max()) if len(ch) and ch["w_mass_max"].notna().any() else None,
        "solver_statuses": fr["solver_status"].value_counts().to_dict() if len(fr) else {},
    }
    if len(fr):
        for (d, ruler), g in fr.groupby(["ds", "ruler"]):
            summary[f"mean_d_star_{d}_{ruler}"] = {
                "group": float(g.groupby("seed")["d_star_group"].first().mean()),
                "cs": float(g.groupby("seed")["d_star_cs"].first().mean()),
                "unif_group": float(g.groupby("seed")["d_unif_group"].first().mean()),
                "unif_cs": float(g.groupby("seed")["d_unif_cs"].first().mean()),
                "myo_group": float(g.groupby("seed")["d_myo_group"].first().mean()),
                "myo_cs": float(g.groupby("seed")["d_myo_cs"].first().mean()),
            }
    if len(ar):
        summary["G_F_ratio_of_means"] = {"|".join(str(x) for x in (b["ds"], b["ruler"], b["arm"],
                                                                  b["cr_class"], b["endpoint"])):
                                         b["G_ratio"] for b in both}
        summary["G_F_mean_of_ratios"] = {"|".join(str(x) for x in (b["ds"], b["ruler"], b["arm"],
                                                                   b["cr_class"], b["endpoint"])):
                                          b["G_meanratio"] for b in both}
        summary["G_F_fragile_cells"] = [b for b in both if b["G_fragile_small_den"]]
    (OUT / "FRONTIER_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str),
                                               encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))


def main() -> None:
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="1", choices=["1", "3"])
    ap.add_argument("--round", default="round_v2")
    ap.add_argument("--limit", type=int, default=None,
                    help="phase 3: use only the first N seeds per dataset")
    args = ap.parse_args()
    OUT = ROOT / "results_w1_ladder" / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    if args.phase == "1":
        phase1()
    else:
        phase3(limit=args.limit)


if __name__ == "__main__":
    main()
