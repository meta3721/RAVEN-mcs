"""W1 round v5.1a - A1' oracle gates, measurements and the structural re-check (AM-6).

Reruns the v5.1 preregistered gates with the AM-6 oracle:

  O-G0  per window over the same 80 runs / 6558 windows: primal <= 1e-13, stationarity <= 1e-12,
        complementary slackness <= 1e-12.  Stationarity is the KKT violation of the projection at
        the multipliers that built the point, minimised over the equality multiplier (see
        w1_v51a_oracle.kkt_residuals) - the same measure v5.1 used.
  O-G1  200 sampled windows: the oracle objective must be <= a fresh CVXPY CLARABEL solve,
        projected back onto C_r, plus 1e-12.  CLARABEL's own status and raw feasibility are
        reported next to the gate because at tolerance 1e-12 it returns `optimal_inaccurate` on a
        large fraction of windows and its raw point is infeasible by up to ~1e-7.
  O-G2  uniform control for K = 1..64: feeding the uniform vector must return it exactly.
  plus the debt algebra self-check (the debt oracle equals the minimiser of
  -Q^T M a + (1/(2 kappa))||a - beta||^2 on C_r).

Measurements: per arm x dataset x seed, alpha_linf_trained, eps_impl_group/cs (trained vs oracle),
alpha_linf_ref, eps_ref_group/cs (v3/v4 stored reference paths) and first_q_div for the debt arm;
verdict `certified` iff max over seeds of eps_impl <= 5e-6, else `approximate`.

Structural re-check: the Delta_group and Delta_c-s rows of round_v4/TRADEOFF_PAIRED.csv recomputed
with the oracle endpoints, same contrasts, same bootstrap (10 000, seed 20261002), same Wilcoxon,
same Holm families, side by side with v4.

Writes results_w1_ladder/round_v5_1a/ only.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_ladder as L                                                          # noqa: E402
import w1_v4_proj as P                                                         # noqa: E402
import w1_v4_train as T                                                        # noqa: E402
import w1_v51a_oracle as O                                                     # noqa: E402
from raven_mcs.aggregation.base import WindowAggregateInput                    # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5_1a"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
V4 = ROOT / "results_w1_ladder/round_v4"
ARMS = ("proj_beta", "proj_beta_debt")
CLASSES = {"proj_beta": T.ProjBetaAggregator, "proj_beta_debt": T.ProjBetaDebtAggregator}
SEEDS = list(range(30001, 30021))
DSS = ("sensorscope", "uair")
KAPPA, ETA_DEBT = 1000.0, 0.01
EPS_IMPL = 5e-6
TOL_PRIMAL, TOL_STAT, TOL_CS, TOL_OBJ = 1e-13, 1e-12, 1e-12, 1e-12
TOL_CVX = 1e-12
BOOT_N, BOOT_SEED = 10_000, 20261002
PAIRS = (("proj_beta", "uniform_window"), ("raven", "proj_beta"),
         ("proj_beta", "fedavg_window"), ("uniform_window", "fedavg_window"),
         ("proj_beta_debt", "proj_beta"))
ENDPOINTS = (("Delta_group", "d_group_oracle"), ("Delta_c_s", "d_cs_oracle"))


# ---------------------------------------------------------------------------------------
# helpers reused from the v5.1 pipeline
# ---------------------------------------------------------------------------------------

def run_inputs(ds, arm, seed, pi):
    run_dir = TRAIN / ds / arm / f"seed{seed}"
    fm = W.load_json(run_dir / "final_metrics.json")
    wm = W.load_json(run_dir / "window_metrics.json")
    act = W.active_windows(wm)
    ref_act = W.active_windows(W.load_json(E3 / ds / "raven" / f"seed{seed}" /
                                          "window_metrics.json"))
    n_bad = abs(len(act) - len(ref_act)) + sum(
        1 for x, y in zip(act, ref_act)
        if [str(c) for c in x["active_clients"]] != [str(c) for c in y["active_clients"]])
    case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi)
    if case is None:
        return None
    aligned = len(act) == case["n"] and all(
        [str(c) for c in act[j]["active_clients"]] == [str(c) for c in case["clients"][j]]
        for j in range(case["n"]))
    return {"case": case, "fm": fm, "act": act, "aligned": aligned, "b_g1_mismatch": int(n_bad),
            "betas": [np.asarray(w["beta_hat"], dtype=float) for w in act],
            "logged": np.concatenate([np.asarray(w["alpha"], dtype=float) for w in act])}


def trained_alpha(case, act, arm):
    agg = CLASSES[arm]()
    out = []
    for j in range(case["n"]):
        K = len(case["clients"][j])
        payload = WindowAggregateInput(
            client_ids=[str(c) for c in act[j]["active_clients"]],
            raw_counts=np.zeros(K, dtype=np.float64), total_masses=np.zeros(K, dtype=np.float64),
            compositions=np.asarray(case["M"][j], dtype=np.float64),
            beta_hat=np.asarray(act[j]["beta_hat"], dtype=np.float64),
            mu=np.asarray(case["mu"], dtype=np.float64))
        out.append(np.asarray(agg.compute_server_weights(payload), dtype=float))
    return np.concatenate(out)


def reference_alpha(case, betas, arm):
    if arm == "proj_beta":
        return np.asarray(P.proj_seq(case, betas), dtype=float)
    a, _diag, _fails = P.kappa_seq(case, KAPPA, betas)
    return np.asarray(a, dtype=float)


def _q_from_alpha(case, alphas, eta=ETA_DEBT):
    qs, Q, off = [], np.zeros(case["G"]), 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        qs.append(Q.copy())
        a = np.asarray(alphas[off:off + K], dtype=float)
        off += K
        Q = np.maximum(Q + eta * (case["mu"] - case["M"][j] @ a), 0.0)
    return qs


def cvx_compare(kind, K, ab, eb, v=None, M=None, Q=None, beta=None):
    """Fresh CLARABEL solve at the preregistered tolerance; returns (x, status, tier)."""
    import cvxpy as cp
    x = cp.Variable(K)
    if kind == "proj":
        obj = cp.sum_squares(x - np.asarray(v, dtype=float))
    else:
        obj = (-np.asarray(Q, dtype=float) @ (np.asarray(M, dtype=float) @ x)
               + (1.0 / (2.0 * KAPPA)) * cp.sum_squares(x - np.asarray(beta, dtype=float)))
    pr = cp.Problem(cp.Minimize(obj), [cp.sum(x) == 1.0, x >= 0.0, x <= float(ab),
                                       cp.sum_squares(x) <= 1.0 / float(eb)])
    for tier, kw in enumerate(({"tol_gap_abs": TOL_CVX, "tol_gap_rel": TOL_CVX,
                                "tol_feas": TOL_CVX}, {})):
        try:
            pr.solve(solver=cp.CLARABEL, verbose=False, **kw)
        except Exception:                                          # noqa: BLE001
            return None, "exception", tier
        if x.value is not None and np.isfinite(np.asarray(x.value, dtype=float)).all():
            return np.asarray(x.value, dtype=float), str(pr.status), tier
    return None, "no_solution", 1


# ---------------------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------------------

def gate_og2() -> dict:
    rows = []
    for K in range(1, 65):
        hi = float(min(1.0, max(0.5, 1.0 / K)))
        eb = float(min(3.0, K))
        u = np.full(K, 1.0 / K)
        got, kind, mult = O.project_Cr(u, hi, eb)
        d = float(np.max(np.abs(got - u)))
        rows.append({"K": K, "a_bar": hi, "e_bar": eb, "max_abs_diff": d, "kind": kind,
                     "pass": bool(d == 0.0)})
    return {"rows": rows, "observed": max(r["max_abs_diff"] for r in rows),
            "pass": all(r["pass"] for r in rows), "tolerance": 0.0,
            "tolerance_source": ("protocol v5.1 2.2 O-G2: beta = uniform must return the uniform "
                                 "weights exactly when they are feasible")}


def gate_debt_algebra(pi) -> dict:
    case = W.build_case("sensorscope", "R_on", "raven_wo_use", 30001, pi["sensorscope"])
    act = W.active_windows(W.load_json(TRAIN / "sensorscope" / "proj_beta_debt" /
                                       "seed30001" / "window_metrics.json"))
    by = {int(w["window_id"]): w for w in act}
    j = 0
    b = np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
    b = b / b.sum()
    rng = np.random.default_rng(1)
    Q = np.abs(rng.normal(size=case["G"])) * 0.01
    M = case["M"][j]
    hi, eb = case["a_bar"][j], case["e_bar"][j]
    w = b + KAPPA * (M.T @ Q)
    a_or, kind, mult = O.project_Cr(w, hi, eb)
    const = -float(Q @ (M @ b)) - 0.5 * KAPPA * float((M.T @ Q) @ (M.T @ Q))
    lhs = O.debt_objective(a_or, b, M, Q)
    rhs = (1.0 / (2.0 * KAPPA)) * float(((a_or - w) ** 2).sum()) + const
    # perturbation: no feasible point may beat the oracle point
    best, n_feas = lhs, 0
    for _ in range(20000):
        d = rng.normal(size=a_or.size)
        d -= d.mean()
        for t in (1e-6, 1e-4, 1e-3, 1e-2):
            for sgn in (1.0, -1.0):
                cand = np.clip(a_or + sgn * t * d, 0.0, hi)
                tot = float(cand.sum())
                if tot <= 0:
                    continue
                cand = cand / tot
                if float(cand @ cand) > 1.0 / eb:
                    continue
                if O.feasibility(cand, hi, eb) > 1e-14:
                    continue
                n_feas += 1
                ob = O.debt_objective(cand, b, M, Q)
                if ob < best:
                    best = ob
    return {"identity": ("(1/(2k))||a-beta||^2 - Q^T M a = (1/(2k))||a - (beta + k M^T Q)||^2 "
                         "+ const"),
            "kappa": KAPPA, "identity_abs_error": abs(lhs - rhs), "kind": kind,
            "obj_oracle": lhs, "obj_best_perturbation": best,
            "best_improvement": lhs - best, "n_feasible_perturbations": n_feas,
            "perturbation_not_better_1e-12": bool(lhs - best <= 1e-12)}


def gate_og0_windows(pi, dss=DSS, seeds=SEEDS, window_list=None):
    """Per-window KKT audit over the runs (both arms).  Returns (rows, records)."""
    rows, recs = [], []
    for ds in dss:
        for arm in ARMS:
            for seed in seeds:
                ri = run_inputs(ds, arm, seed, pi[ds])
                if ri is None or not ri["aligned"]:
                    continue
                case, betas = ri["case"], ri["betas"]
                if arm == "proj_beta":
                    a_or, diag = O.oracle_proj_beta(betas, case)
                    qs = [None] * case["n"]
                else:
                    a_or, qs, diag = O.oracle_debt_seq(case, betas)
                wmax = {"primal": 0.0, "stationarity": 0.0, "cs": 0.0}
                off = 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    a = a_or[off:off + K]
                    off += K
                    d = diag[j]
                    if arm == "proj_beta":
                        res = O.audit_projection(a, d["v"], case["a_bar"][j],
                                                 case["e_bar"][j], d["mult"])
                    else:
                        res = O.audit_debt(a, case["M"][j], qs[j], d["beta"],
                                           case["a_bar"][j], case["e_bar"][j], d["mult"])
                    recs.append({"ds": ds, "arm": arm, "seed": seed, "j": j, "K": K,
                                 "kind": d["kind"], **{k: res[k] for k in
                                                       ("primal", "stationarity", "stat_raw",
                                                        "stat_fit", "cs")}})
                    for k in wmax:
                        wmax[k] = max(wmax[k], float(res[k]))
                rows.append({"ds": ds, "arm": arm, "seed": int(seed), "n_windows": int(case["n"]),
                             **{("max_" + k): v for k, v in wmax.items()},
                             "pass": bool(wmax["primal"] <= TOL_PRIMAL
                                          and wmax["stationarity"] <= TOL_STAT
                                          and wmax["cs"] <= TOL_CS)})
    return rows, recs


def gate_og1(pi, n=200, seed=20261002):
    """200 sampled windows, fresh CVXPY comparator projected back onto C_r."""
    rng = np.random.default_rng(seed)
    pool = []
    for ds in DSS:
        for arm in ARMS:
            for s in SEEDS:
                ri = run_inputs(ds, arm, s, pi[ds])
                if ri is None or not ri["aligned"]:
                    continue
                case, betas = ri["case"], ri["betas"]
                if arm == "proj_beta":
                    a_or, diag = O.oracle_proj_beta(betas, case)
                    qs = [None] * case["n"]
                else:
                    a_or, qs, diag = O.oracle_debt_seq(case, betas)
                off = 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    pool.append((ds, arm, s, j, case, a_or[off:off + K], qs[j], diag[j]))
                    off += K
                if arm == "proj_beta":
                    break
    pick = rng.choice(len(pool), size=min(n, len(pool)), replace=False)
    rows = []
    for i in pick:
        ds, arm, s, j, case, a_or, Q, d = pool[int(i)]
        K = len(case["clients"][j])
        hi, eb = case["a_bar"][j], case["e_bar"][j]
        if arm == "proj_beta":
            x_cx, status, tier = cvx_compare("proj", K, hi, eb, v=d["v"])
            o_or = O.proj_objective(a_or, d["v"])
            o_cx = None if x_cx is None else O.proj_objective(x_cx, d["v"])
            o_pb = (None if x_cx is None else
                    O.proj_objective(O.project_Cr(x_cx, hi, eb)[0], d["v"]))
        else:
            x_cx, status, tier = cvx_compare("debt", K, hi, eb, M=case["M"][j], Q=Q, beta=d["beta"])
            o_or = O.debt_objective(a_or, d["beta"], case["M"][j], Q)
            o_cx = (None if x_cx is None else
                    O.debt_objective(x_cx, d["beta"], case["M"][j], Q))
            o_pb = (None if x_cx is None else
                    O.debt_objective(O.project_Cr(x_cx, hi, eb)[0], d["beta"], case["M"][j], Q))
        if x_cx is None:
            continue
        rows.append({"ds": ds, "arm": arm, "seed": int(s), "window": int(j), "K": int(K),
                     "kind": d["kind"], "cvxpy_status": status, "cvxpy_tol_tier": int(tier),
                     "cvxpy_raw_feasibility": O.feasibility(x_cx, hi, eb),
                     "obj_oracle": o_or, "obj_cvxpy": o_cx, "obj_cvxpy_projected": o_pb,
                     "gap_vs_projected": o_or - o_pb, "gap_vs_raw": o_or - o_cx,
                     "alpha_linf_vs_projected": float(np.max(np.abs(a_or - O.project_Cr(
                         x_cx, hi, eb)[0]))),
                     "pass": bool(o_or <= o_pb + TOL_OBJ)})
    df = pd.DataFrame(rows)
    return {"n_windows": int(len(df)),
            "observed_max_gap": float(df.gap_vs_projected.max()),
            "n_cvxpy_status_optimal": int((df.cvxpy_status == "optimal").sum()),
            "n_cvxpy_status_optimal_inaccurate": int((df.cvxpy_status ==
                                                      "optimal_inaccurate").sum()),
            "max_cvxpy_raw_feasibility": float(df.cvxpy_raw_feasibility.max()),
            "max_cvxpy_gap_vs_raw_infeasible_point": float(df.gap_vs_raw.max()),
            "max_alpha_linf_vs_projected": float(df.alpha_linf_vs_projected.max()),
            "pass": bool(df["pass"].all()), "tolerance": TOL_OBJ,
            "tolerance_source": ("protocol v5.1 2.2 O-G1: oracle objective <= fresh CVXPY "
                                 "CLARABEL value (projected back onto C_r) + 1e-12")}, df


# ---------------------------------------------------------------------------------------
# measurements
# ---------------------------------------------------------------------------------------

def measurements(pi) -> tuple:
    impl_rows, g0_rows = [], []
    for ds in DSS:
        for arm in ARMS:
            for seed in SEEDS:
                ri = run_inputs(ds, arm, seed, pi[ds])
                if ri is None or not ri["aligned"]:
                    impl_rows.append({"ds": ds, "arm": arm, "seed": seed, "verdict": "misaligned"})
                    continue
                case, betas = ri["case"], ri["betas"]
                a_tr = trained_alpha(case, ri["act"], arm)
                a_ref = reference_alpha(case, betas, arm)
                if arm == "proj_beta":
                    a_or, diag = O.oracle_proj_beta(betas, case)
                    qs_or = None
                else:
                    a_or, qs_or, diag = O.oracle_debt_seq(case, betas)
                g_or, c_or = L.endpoints(case, a_or)
                g_tr, c_tr = L.endpoints(case, a_tr)
                g_rf, c_rf = L.endpoints(case, a_ref)
                wmax = {"primal": 0.0, "stationarity": 0.0, "cs": 0.0}
                off = 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    a = a_or[off:off + K]
                    off += K
                    d = diag[j]
                    if arm == "proj_beta":
                        res = O.audit_projection(a, d["v"], case["a_bar"][j],
                                                 case["e_bar"][j], d["mult"])
                    else:
                        res = O.audit_debt(a, case["M"][j], qs_or[j], d["beta"],
                                           case["a_bar"][j], case["e_bar"][j], d["mult"])
                    for k in wmax:
                        wmax[k] = max(wmax[k], float(res[k]))
                g0_rows.append({"ds": ds, "arm": arm, "seed": int(seed),
                                "n_windows": int(case["n"]),
                                **{("max_" + k): v for k, v in wmax.items()},
                                "pass": bool(wmax["primal"] <= TOL_PRIMAL
                                             and wmax["stationarity"] <= TOL_STAT
                                             and wmax["cs"] <= TOL_CS)})
                fq = None
                if arm == "proj_beta_debt":
                    Qtr = _q_from_alpha(case, a_tr)
                    for j in range(case["n"]):
                        if float(np.max(np.abs(qs_or[j] - Qtr[j]))) > 1e-12:
                            fq = int(j)
                            break
                a_linf = float(np.max(np.abs(a_tr - ri["logged"])))
                eps = max(abs(g_tr - g_or), abs(c_tr - c_or))
                impl_rows.append({
                    "ds": ds, "arm": arm, "seed": int(seed),
                    "alpha_linf_trained": a_linf,
                    "eps_impl_group": abs(g_tr - g_or), "eps_impl_cs": abs(c_tr - c_or),
                    "alpha_linf_ref": float(np.max(np.abs(a_ref - a_or))),
                    "eps_ref_group": abs(g_rf - g_or), "eps_ref_cs": abs(c_rf - c_or),
                    "first_q_div": fq,
                    "d_group_oracle": g_or, "d_cs_oracle": c_or,
                    "d_group_trained": g_tr, "d_cs_trained": c_tr,
                    "d_group_reference": g_rf, "d_cs_reference": c_rf,
                    "err_self_group": abs(g_tr - float(ri["fm"]["Delta_group"])),
                    "err_self_cs": abs(c_tr - float(ri["fm"]["Delta_c_s"])),
                    "b_g1_mismatch_windows": int(ri["b_g1_mismatch"]),
                    "verdict": "certified" if eps <= EPS_IMPL else "approximate"})
                print("A1' %-6s %-16s %d alinf_tr=%.3g eps_impl=(%.3g,%.3g) alinf_ref=%.3g "
                      "eps_ref=(%.3g,%.3g) fq=%s"
                      % (ds, arm, seed, a_linf, abs(g_tr - g_or), abs(c_tr - c_or),
                         float(np.max(np.abs(a_ref - a_or))), abs(g_rf - g_or),
                         abs(c_rf - c_or), fq), flush=True)
    # analytic uniform_window rows and frozen comparator rows (needed for every v4 contrast)
    for ds in DSS:
        for seed in SEEDS:
            case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
            fm = W.load_json(TRAIN / ds / "uniform_window" / f"seed{seed}" / "final_metrics.json")
            a = np.concatenate([np.full(len(case["clients"][j]), 1.0 / len(case["clients"][j]))
                                for j in range(case["n"])])
            g, c = L.endpoints(case, a)
            impl_rows.append({"ds": ds, "arm": "uniform_window", "seed": int(seed),
                              "alpha_linf_trained": 0.0, "eps_impl_group": 0.0,
                              "eps_impl_cs": 0.0, "alpha_linf_ref": 0.0, "eps_ref_group": 0.0,
                              "eps_ref_cs": 0.0, "first_q_div": np.nan,
                              "d_group_oracle": g, "d_cs_oracle": c, "d_group_trained": g,
                              "d_cs_trained": c, "d_group_reference": g, "d_cs_reference": c,
                              "err_self_group": abs(g - float(fm["Delta_group"])),
                              "err_self_cs": abs(c - float(fm["Delta_c_s"])),
                              "b_g1_mismatch_windows": 0, "verdict": "certified"})
            for arm in ("fedavg_window", "inst_cal", "raven"):
                f = W.load_json(E3 / ds / arm / f"seed{seed}" / "final_metrics.json")
                impl_rows.append({"ds": ds, "arm": arm, "seed": int(seed),
                                  "alpha_linf_trained": 0.0, "eps_impl_group": 0.0,
                                  "eps_impl_cs": 0.0, "alpha_linf_ref": 0.0, "eps_ref_group": 0.0,
                                  "eps_ref_cs": 0.0, "first_q_div": np.nan,
                                  "d_group_oracle": float(f["Delta_group"]),
                                  "d_cs_oracle": float(f["Delta_c_s"]),
                                  "d_group_trained": float(f["Delta_group"]),
                                  "d_cs_trained": float(f["Delta_c_s"]),
                                  "d_group_reference": float(f["Delta_group"]),
                                  "d_cs_reference": float(f["Delta_c_s"]),
                                  "err_self_group": 0.0, "err_self_cs": 0.0,
                                  "b_g1_mismatch_windows": 0, "verdict": "comparator"})
    return pd.DataFrame(impl_rows), pd.DataFrame(g0_rows)


def holm(p):
    order = np.argsort(p)
    adj = np.empty_like(p)
    run, m = 0.0, len(p)
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * p[i])
        run = max(run, val)
        adj[i] = run
    return adj


def verdict(pp, p_holm):
    if p_holm <= 0.05 and pp > 0:
        return "rule_better"
    if p_holm <= 0.05 and pp < 0:
        return "reference_better"
    return "not_significant"


def structural(imp: pd.DataFrame) -> pd.DataFrame:
    v4 = pd.read_csv(V4 / "TRADEOFF_PAIRED.csv")
    v4 = v4[v4.endpoint.isin(["Delta_group", "Delta_c_s"])]
    out = []
    for ds in DSS:
        sub = imp[imp.ds == ds]
        piv = {a: g.set_index("seed") for a, g in sub.groupby("arm")}
        for ep_name, col in ENDPOINTS:
            for a, b in PAIRS:
                if a not in piv or b not in piv:
                    out.append({"ds": ds, "endpoint": ep_name, "contrast": f"{a} - {b}",
                                "status": "missing_oracle_endpoints"})
                    continue
                pa, pb = piv[a], piv[b]
                common = pa.index.intersection(pb.index)
                d = (pa.loc[common, col] - pb.loc[common, col]).to_numpy(float)
                rng = np.random.default_rng(BOOT_SEED)
                boot = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                                 for _ in range(BOOT_N)])
                try:
                    p = float(stats.wilcoxon(d).pvalue)
                except Exception:                                  # noqa: BLE001
                    p = float("nan")
                out.append({"ds": ds, "endpoint": ep_name, "contrast": f"{a} - {b}",
                            "status": "ok", "n_seeds": int(len(d)),
                            "mean_diff_oracle": float(d.mean()),
                            "pp_oracle": float(-100 * d.mean() / 2),
                            "ci_lo_oracle": float(np.percentile(boot, 2.5)),
                            "ci_hi_oracle": float(np.percentile(boot, 97.5)),
                            "p_wilcoxon_oracle": p})
    oa = pd.DataFrame(out)
    ok = oa.status == "ok"
    for ds in DSS:
        for ep in ("Delta_group", "Delta_c_s"):
            sel = ok & (oa.ds == ds) & (oa.endpoint == ep)
            if sel.any():
                oa.loc[sel, "p_holm_oracle"] = holm(
                    oa.loc[sel, "p_wilcoxon_oracle"].to_numpy(float))
    merged = oa.merge(v4[["ds", "endpoint", "contrast", "pp_diff", "ci_lo", "ci_hi",
                          "p_wilcoxon", "p_holm"]]
                      .rename(columns={"pp_diff": "pp_v4", "ci_lo": "ci_lo_v4",
                                       "ci_hi": "ci_hi_v4", "p_wilcoxon": "p_wilcoxon_v4",
                                       "p_holm": "p_holm_v4"}),
                      on=["ds", "endpoint", "contrast"], how="outer", indicator=True)
    merged["verdict_v4"] = [verdict(r.pp_v4, r.p_holm_v4) if pd.notna(r.pp_v4)
                            and pd.notna(r.p_holm_v4) else "missing"
                            for r in merged.itertuples(index=False)]
    merged["verdict_oracle"] = [verdict(r.pp_oracle, r.p_holm_oracle)
                                if pd.notna(r.pp_oracle) and pd.notna(r.p_holm_oracle)
                                else "missing" for r in merged.itertuples(index=False)]
    merged["verdict_changed"] = merged.verdict_v4 != merged.verdict_oracle
    merged["d_pp"] = merged.pp_oracle - merged.pp_v4
    cols = ["ds", "endpoint", "contrast", "n_seeds", "pp_v4", "pp_oracle", "d_pp",
            "ci_lo_v4", "ci_hi_v4", "ci_lo_oracle", "ci_hi_oracle",
            "p_wilcoxon_v4", "p_wilcoxon_oracle", "p_holm_v4", "p_holm_oracle",
            "verdict_v4", "verdict_oracle", "verdict_changed"]
    return merged[cols]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gates-only", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    pi = {d: W.pi_tar_for(d) for d in DSS}
    gates = {"round": "round_v5_1a", "oracle": "scripts/w1_v51a_oracle.py (AM-6)",
             "tol_primal": TOL_PRIMAL, "tol_stationarity": TOL_STAT, "tol_cs": TOL_CS,
             "tol_objective": TOL_OBJ, "eps_impl": EPS_IMPL}

    print("[O-G2] uniform control ...", flush=True)
    gates["O-G2"] = gate_og2()
    print("       observed %.3g pass=%s" % (gates["O-G2"]["observed"], gates["O-G2"]["pass"]),
          flush=True)

    print("[O-G0] per-window KKT audit ...", flush=True)
    g0_rows, g0_recs = gate_og0_windows(pi)
    g0 = pd.DataFrame(g0_rows)
    rec = pd.DataFrame(g0_recs)
    gates["O-G0"] = {
        "n_runs": int(len(g0)), "n_windows": int(g0.n_windows.sum()),
        "observed_primal": float(g0.max_primal.max()),
        "observed_stationarity": float(g0.max_stationarity.max()),
        "observed_cs": float(g0.max_cs.max()),
        "pass": bool(g0["pass"].all()),
        "tolerance_primal": TOL_PRIMAL, "tolerance_stationarity": TOL_STAT,
        "tolerance_cs": TOL_CS,
        "n_failing_runs": int((~g0["pass"]).sum()),
        "worst_windows": rec.sort_values("stationarity", ascending=False).head(10).to_dict("records"),
        "tolerance_source": ("protocol v5.1 2.2 O-G0: per window, primal <= 1e-13, stationarity "
                             "<= 1e-12, complementary slackness <= 1e-12")}
    print("       primal %.3g stat %.3g cs %.3g pass=%s"
          % (gates["O-G0"]["observed_primal"], gates["O-G0"]["observed_stationarity"],
             gates["O-G0"]["observed_cs"], gates["O-G0"]["pass"]), flush=True)

    print("[O-G1] CVXPY comparator ...", flush=True)
    gates["O-G1"], og1 = gate_og1(pi)
    print("       max gap %.3g pass=%s (status optimal %d, optimal_inaccurate %d)"
          % (gates["O-G1"]["observed_max_gap"], gates["O-G1"]["pass"],
             gates["O-G1"]["n_cvxpy_status_optimal"],
             gates["O-G1"]["n_cvxpy_status_optimal_inaccurate"]), flush=True)

    print("[debt algebra] ...", flush=True)
    gates["self_check_debt_algebra"] = gate_debt_algebra(pi)
    print("       identity err %.3g improvement %.3g"
          % (gates["self_check_debt_algebra"]["identity_abs_error"],
             gates["self_check_debt_algebra"]["best_improvement"]), flush=True)

    if args.gates_only:
        (OUT / "O_GATES_RERUN.json").write_text(json.dumps(gates, indent=2, default=str),
                                                encoding="utf-8")
        pd.DataFrame(g0_recs).to_csv(OUT / "A1P_OG0_WINDOWS.csv", index=False)
        og1.to_csv(OUT / "A1P_OG1_SAMPLE.csv", index=False)
        g0.to_csv(OUT / "A1P_OG0_RUNS.csv", index=False)
        print("gates-only done in %.1fs" % (time.perf_counter() - t0))
        return

    print("[A1'] measurements ...", flush=True)
    imp, g0b = measurements(pi)
    imp.to_csv(OUT / "A1P_IMPL_RERUN.csv", index=False)
    pd.DataFrame(g0_recs).to_csv(OUT / "A1P_OG0_WINDOWS.csv", index=False)
    og1.to_csv(OUT / "A1P_OG1_SAMPLE.csv", index=False)

    per_cell = {}
    for d in DSS:
        for a in ARMS:
            sel = imp[(imp.ds == d) & (imp.arm == a)]
            if not len(sel):
                continue
            per_cell["%s|%s" % (a, d)] = {
                "max_eps_impl": float(sel[["eps_impl_group", "eps_impl_cs"]].max().max()),
                "max_eps_impl_group": float(sel.eps_impl_group.max()),
                "max_eps_impl_cs": float(sel.eps_impl_cs.max()),
                "verdict": ("certified" if sel.verdict.eq("certified").all() else "approximate"),
                "n_certified_seeds": int(sel.verdict.eq("certified").sum()), "n_seeds": int(len(sel)),
                "max_alpha_linf_trained": float(sel.alpha_linf_trained.max()),
                "max_alpha_linf_ref": float(sel.alpha_linf_ref.max()),
                "max_eps_ref_group": float(sel.eps_ref_group.max()),
                "max_eps_ref_cs": float(sel.eps_ref_cs.max()),
                "first_q_div_min": (None if sel.first_q_div.dropna().empty
                                    else int(sel.first_q_div.dropna().min()))}
    gates["O-gate"] = {"threshold_eps_impl": EPS_IMPL, "per_cell": per_cell,
                       "observed": max(v["max_eps_impl"] for v in per_cell.values()),
                       "pass": all(v["verdict"] == "certified" for v in per_cell.values()),
                       "tolerance_source": ("protocol v5.1 2.3: certified iff max over seeds of "
                                            "eps_impl <= 5e-6, else approximate")}
    gates["G-self_AM1"] = {
        "observed_alpha_linf": float(imp.alpha_linf_trained.max()),
        "observed_endpoint_err": float(imp[["err_self_group", "err_self_cs"]].max().max()),
        "tolerance_alpha_linf": 1e-8, "tolerance_endpoint": 1e-12,
        "tolerance_source": "AM-1: alpha L-inf <= 1e-8 and both endpoints <= 1e-12 vs final_metrics",
        "pass": bool((imp.alpha_linf_trained <= 1e-8).all()
                     and (imp.err_self_group <= 1e-12).all()
                     and (imp.err_self_cs <= 1e-12).all())}
    gates["B-G1"] = {"observed": int(imp.b_g1_mismatch_windows.sum()), "tolerance": 0,
                     "tolerance_source": ("exact active-set identity vs "
                                          "artifacts/e3_formal_runs_r1/runs/<ds>/raven/seed<seed>/"
                                          "window_metrics.json"),
                     "pass": bool(int(imp.b_g1_mismatch_windows.sum()) == 0)}
    gates["seconds"] = time.perf_counter() - t0

    print("[A1' structural re-check] ...", flush=True)
    st = structural(imp)
    st.to_csv(OUT / "A1P_STRUCT_PAIRED_RERUN.csv", index=False)
    changed = st[st.verdict_changed.fillna(False).astype(bool)]
    summary = {"rows": int(len(st)), "verdict_changes": int(len(changed)),
               "changed_rows": changed.to_dict("records"),
               "max_abs_d_pp": float(st.d_pp.abs().max()),
               "max_abs_d_pp_by_endpoint": {ep: float(st[st.endpoint == ep].d_pp.abs().max())
                                            for ep in ("Delta_group", "Delta_c_s")}}
    gates["A1P_STRUCT"] = summary
    (OUT / "A1P_STRUCT_SUMMARY_RERUN.json").write_text(json.dumps(summary, indent=2, default=str),
                                                       encoding="utf-8")
    (OUT / "O_GATES_RERUN.json").write_text(json.dumps(gates, indent=2, default=str),
                                            encoding="utf-8")
    print(json.dumps({k: v for k, v in gates.items() if k != "worst_windows"},
                     indent=2, default=str))


if __name__ == "__main__":
    main()
