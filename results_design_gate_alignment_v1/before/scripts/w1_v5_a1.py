"""W1 round v5 - A1 (R4 + R8): gate re-specification.

Read-only.  Writes only under results_w1_ladder/round_v5/.

A1-G-self : rebuild alpha from the run's own logged inputs (active_clients, beta_hat) and
            M_r/mu from W.build_case, using the SAME aggregator classes imported from
            scripts/w1_v4_train.py (fresh instance per run), and check
            alpha L-inf == 0 and |Delta_group|, |Delta_c-s| <= 1e-12 vs final_metrics.json.
A1-sens   : replay path (proj_seq / kappa_seq problems) on a 12-cell grid
            tol x beta_input x problem-object; per cell alpha L-inf vs trained,
            |d d_group|, |d d_c-s|, first diverging window, and (debt arm) the first
            window where Q differs by > 1e-12.
A1-G-xref : tau_x = 10 x largest endpoint spread across the grid (per arm, dataset);
            residual vs the unmodified replay reference cell R*.

Usage (one part per (arm, dataset) is the intended parallel unit):
    python scripts/w1_v5_a1.py --run --arms proj_beta --datasets sensorscope
    python scripts/w1_v5_a1.py --merge
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

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                       # noqa: E402
import w1_ladder as L                                                       # noqa: E402
import w1_v4_proj as P                                                      # noqa: E402
import w1_v4_train as T                                                     # noqa: E402
from raven_mcs.aggregation.base import WindowAggregateInput                 # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound     # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
ARMS = ("uniform_window", "proj_beta", "proj_beta_debt")
CLASSES = {"uniform_window": T.UniformWindowAggregator,
           "proj_beta": T.ProjBetaAggregator,
           "proj_beta_debt": T.ProjBetaDebtAggregator}
SEEDS = list(range(30001, 30021))
ETA_DEBT, KAPPA = 0.01, 1000.0
TOLS = (None, 1e-10, 1e-12)             # None == CLARABEL default (no tol kwargs)
BETAS = ("raw", "norm")
PROBLEMS = ("cached", "fresh")
GSELF_TOL = 1e-12
TAU_LIMIT = 5e-6
_CACHE: dict = {}


# ---------------------------------------------------------------------------------------
# grid cells: faithful re-implementation of the w1_v4_proj problems with the extra axes
# ---------------------------------------------------------------------------------------

def _solve(prob, tol):
    kw = {} if tol is None else {"tol_gap_abs": tol, "tol_gap_rel": tol, "tol_feas": tol}
    prob.solve(solver=cp.CLARABEL, verbose=False, **kw)


def _beta_in(beta, mode):
    b = np.asarray(beta, dtype=float)
    return b if mode == "raw" else b / b.sum()


def proj_cell(beta, ab, eb, K, tol, fresh, key):
    if fresh:
        par = cp.Parameter(K)
        abp = cp.Parameter(nonneg=True)
        ebp = cp.Parameter(nonneg=True)
        x = cp.Variable(K)
        pr = cp.Problem(cp.Minimize(cp.sum_squares(x - par)),
                        [cp.sum(x) == 1.0, x >= 0.0, x <= abp, cp.sum_squares(x) <= 1.0 / ebp])
    else:
        if key not in _CACHE:
            par = cp.Parameter(K)
            abp = cp.Parameter(nonneg=True)
            ebp = cp.Parameter(nonneg=True)
            x = cp.Variable(K)
            pr = cp.Problem(cp.Minimize(cp.sum_squares(x - par)),
                            [cp.sum(x) == 1.0, x >= 0.0, x <= abp,
                             cp.sum_squares(x) <= 1.0 / ebp])
            _CACHE[key] = (par, abp, ebp, x, pr)
        par, abp, ebp, x, pr = _CACHE[key]
    par.value = np.asarray(beta, dtype=float)
    abp.value = float(ab)
    ebp.value = float(eb)
    _solve(pr, tol)
    return np.asarray(x.value, dtype=float).clip(0.0, None)


def kappa_cell(M, beta, Q, ab, eb, G, K, kappa, tol, fresh, key):
    if fresh:
        Mp = cp.Parameter((G, K))
        bp = cp.Parameter(K)
        qp = cp.Parameter(G)
        kp = cp.Parameter(nonneg=True)
        abp = cp.Parameter(nonneg=True)
        ebp = cp.Parameter(nonneg=True)
        x = cp.Variable(K)
        pr = cp.Problem(cp.Minimize(-qp @ (Mp @ x) + kp * 0.5 * cp.sum_squares(x - bp)),
                        [cp.sum(x) == 1.0, x >= 0.0, x <= abp, cp.sum_squares(x) <= 1.0 / ebp])
    else:
        if key not in _CACHE:
            Mp = cp.Parameter((G, K))
            bp = cp.Parameter(K)
            qp = cp.Parameter(G)
            kp = cp.Parameter(nonneg=True)
            abp = cp.Parameter(nonneg=True)
            ebp = cp.Parameter(nonneg=True)
            x = cp.Variable(K)
            pr = cp.Problem(cp.Minimize(-qp @ (Mp @ x) + kp * 0.5 * cp.sum_squares(x - bp)),
                            [cp.sum(x) == 1.0, x >= 0.0, x <= abp,
                             cp.sum_squares(x) <= 1.0 / ebp])
            _CACHE[key] = (Mp, bp, qp, kp, abp, ebp, x, pr)
        Mp, bp, qp, kp, abp, ebp, x, pr = _CACHE[key]
    Mp.value = np.asarray(M, dtype=float)
    bp.value = np.asarray(beta, dtype=float)
    qp.value = np.asarray(Q, dtype=float)
    kp.value = float("inf") if kappa == 0 else 1.0 / float(kappa)
    abp.value = float(ab)
    ebp.value = float(eb)
    a = None
    fails = 0
    for solver in (cp.CLARABEL, cp.SCS):
        try:
            if solver is cp.CLARABEL:
                _solve(pr, tol)
            else:
                pr.solve(solver=solver, verbose=False)
            a = np.asarray(x.value, dtype=float).clip(0.0, None)
            break
        except Exception:                                        # noqa: BLE001
            a = None
    if a is None:
        fails = 1
        a = proj_cell(beta, ab, eb, K, tol, fresh, ("proj-fb", K, tol, fresh))
    return a, fails


def run_cell(case, betas_logged, arm, beta_mode, tol, problem, kappa=KAPPA):
    """One grid cell over every window of the case; returns alpha, Q trajectory, fails."""
    n = case["n"]
    alphas, qs, fails = [], [], 0
    Q = np.zeros(case["G"])
    for j in range(n):
        K = len(case["clients"][j])
        b = _beta_in(betas_logged[j], beta_mode)
        key = (arm, beta_mode, tol, problem, K)
        if arm == "proj_beta":
            a = proj_cell(b, case["a_bar"][j], case["e_bar"][j], K, tol,
                          problem == "fresh", key)
        elif arm == "proj_beta_debt":
            a, f = kappa_cell(case["M"][j], b, Q, case["a_bar"][j], case["e_bar"][j],
                              case["G"], K, kappa, tol, problem == "fresh", key)
            fails += f
        else:                                                     # pragma: no cover
            raise ValueError(arm)
        qs.append(Q.copy())
        alphas.append(a)
        Q = np.maximum(Q + ETA_DEBT * (case["mu"] - case["M"][j] @ a), 0.0)
    return np.concatenate(alphas), qs, fails


def q_from_alpha(case, alphas):
    """Q recursion driven by a given alpha sequence (used for the trained reference Q)."""
    qs = []
    Q = np.zeros(case["G"])
    off = 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        qs.append(Q.copy())
        a = np.asarray(alphas[off:off + K], dtype=float)
        off += K
        Q = np.maximum(Q + ETA_DEBT * (case["mu"] - case["M"][j] @ a), 0.0)
    return qs


# ---------------------------------------------------------------------------------------
# per-run work
# ---------------------------------------------------------------------------------------

def per_window_linf(logged, rebuilt, case):
    """Per-window alpha L-inf and first index where it is non-zero."""
    out, off, first = [], 0, None
    for j in range(case["n"]):
        K = len(case["clients"][j])
        d = float(np.max(np.abs(np.asarray(rebuilt[off:off + K], dtype=float)
                                - np.asarray(logged[off:off + K], dtype=float)))) if K else 0.0
        out.append(d)
        if first is None and d > 0.0:
            first = j
        off += K
    return out, first


def process_run(ds, arm, seed, pi):
    t0 = time.perf_counter()
    run_dir = TRAIN / ds / arm / f"seed{seed}"
    fm = W.load_json(run_dir / "final_metrics.json")
    wm = W.load_json(run_dir / "window_metrics.json")
    act = W.active_windows(wm)
    ref_act = W.active_windows(W.load_json(E3 / ds / "raven" / f"seed{seed}" / "window_metrics.json"))
    n_bad = 0
    if len(act) == len(ref_act):
        n_bad = sum(1 for x, y in zip(act, ref_act)
                    if [str(c) for c in x["active_clients"]] != [str(c) for c in y["active_clients"]])
    else:
        n_bad = abs(len(act) - len(ref_act)) + sum(
            1 for x, y in zip(act, ref_act)
            if [str(c) for c in x["active_clients"]] != [str(c) for c in y["active_clients"]])
    case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi)
    if case is None:
        return {"status": "no_case", "ds": ds, "arm": arm, "seed": seed}
    aligned = len(act) == case["n"] and all(
        [str(c) for c in act[j]["active_clients"]] == [str(c) for c in case["clients"][j]]
        for j in range(case["n"]))
    if not aligned:
        return {"status": "misaligned", "ds": ds, "arm": arm, "seed": seed,
                "n_act": len(act), "n_case": case["n"]}
    betas = [np.asarray(w["beta_hat"], dtype=float) for w in act]
    logged = np.concatenate([np.asarray(w["alpha"], dtype=float) for w in act])

    # ---------------- A1-G-self: same aggregator class, fresh instance ----------------
    agg = CLASSES[arm]()
    rebuilt = []
    for j in range(case["n"]):
        K = len(case["clients"][j])
        payload = WindowAggregateInput(
            client_ids=[str(c) for c in act[j]["active_clients"]],
            raw_counts=np.zeros(K, dtype=np.float64),
            total_masses=np.zeros(K, dtype=np.float64),
            compositions=np.asarray(case["M"][j], dtype=np.float64),
            beta_hat=betas[j],
            mu=np.asarray(case["mu"], dtype=np.float64),
        )
        rebuilt.append(np.asarray(agg.compute_server_weights(payload), dtype=float))
    rebuilt = np.concatenate(rebuilt)
    per_win, first_div = per_window_linf(logged, rebuilt, case)
    gself_linf = float(np.max(per_win))
    dg_self, dc_self = L.endpoints(case, rebuilt)
    eg = abs(float(dg_self) - float(fm["Delta_group"]))
    ec = abs(float(dc_self) - float(fm["Delta_c_s"]))
    gself = {"ds": ds, "arm": arm, "seed": seed, "n_windows": case["n"],
             "alpha_linf": gself_linf, "first_diverging_window": first_div,
             "per_window_linf_max": gself_linf,
             "d_group": dg_self, "d_cs": dc_self,
             "err_group": eg, "err_cs": ec,
             "stored_group": float(fm["Delta_group"]), "stored_cs": float(fm["Delta_c_s"]),
             "b_g1_mismatch_windows": int(n_bad),
             "pass": bool(gself_linf == 0.0 and eg <= GSELF_TOL and ec <= GSELF_TOL),
             "seconds": None}

    # ---------------- A1-sens grid ----------------
    rows = []
    if arm == "uniform_window":
        cells = [("analytic", None, "analytic")]
        for label, _b, _p in cells:
            dg, dc = dg_self, dc_self
            rows.append({"ds": ds, "arm": arm, "seed": seed, "beta_input": "analytic",
                         "problem": "analytic", "tol": "analytic",
                         "alpha_linf_vs_trained": gself_linf,
                         "first_diverging_window": first_div,
                         "d_group": dg, "d_cs": dc,
                         "abs_dd_group": abs(dg - float(fm["Delta_group"])),
                         "abs_dd_cs": abs(dc - float(fm["Delta_c_s"])),
                         "solver_fails": 0, "first_q_diverging_window": None,
                         "is_reference_cell": True})
    else:
        q_trained = q_from_alpha(case, logged)
        # fidelity of the reference cell against the unmodified repository replay path
        if arm == "proj_beta":
            ref_seq = P.proj_seq(case, betas)
        else:
            ref_seq, _, _ = P.kappa_seq(case, KAPPA, betas)
        for beta_mode in BETAS:
            for problem in PROBLEMS:
                for tol in TOLS:
                    is_ref = (beta_mode == "raw" and problem == "cached"
                              and ((arm == "proj_beta" and tol == 1e-10)
                                   or (arm == "proj_beta_debt" and tol is None)))
                    a_cell, qs, fails = run_cell(case, betas, arm, beta_mode, tol, problem)
                    per_win_c, first_c = per_window_linf(logged, a_cell, case)
                    dg, dc = L.endpoints(case, a_cell)
                    fq = None
                    if arm == "proj_beta_debt":
                        for j in range(case["n"]):
                            if float(np.max(np.abs(qs[j] - q_trained[j]))) > 1e-12:
                                fq = j
                                break
                    rows.append({"ds": ds, "arm": arm, "seed": seed,
                                 "beta_input": beta_mode, "problem": problem,
                                 "tol": "default" if tol is None else ("%g" % tol),
                                 "alpha_linf_vs_trained": float(np.max(per_win_c)),
                                 "first_diverging_window": first_c,
                                 "d_group": float(dg), "d_cs": float(dc),
                                 "abs_dd_group": abs(float(dg) - float(fm["Delta_group"])),
                                 "abs_dd_cs": abs(float(dc) - float(fm["Delta_c_s"])),
                                 "solver_fails": int(fails),
                                 "first_q_diverging_window": fq,
                                 "is_reference_cell": bool(is_ref),
                                 "ref_impl_linf": (float(np.max(np.abs(a_cell - ref_seq)))
                                                   if is_ref else None)})
    gself["seconds"] = time.perf_counter() - t0
    return {"status": "ok", "rows": rows, "gself": gself}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--datasets", default="sensorscope,uair")
    ap.add_argument("--seeds", default="all")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.run:
        arms = [a for a in args.arms.split(",") if a]
        dss = [d for d in args.datasets.split(",") if d]
        seeds = SEEDS if args.seeds == "all" else [int(x) for x in args.seeds.split(",")]
        pi = {}
        for ds in dss:
            pi[ds] = W.pi_tar_for(ds)
        for ds in dss:
            for arm in arms:
                gs_rows, sens_rows, meta = [], [], []
                for seed in seeds:
                    res = process_run(ds, arm, seed, pi[ds])
                    if res["status"] != "ok":
                        meta.append(res)
                        print("SKIP %s %s %d status=%s" % (ds, arm, seed, res["status"]),
                              flush=True)
                        continue
                    gs_rows.append(res["gself"])
                    sens_rows.extend(res["rows"])
                    print("run %s %s %d alpha_linf=%.3g eg=%.3g ec=%.3g sec=%.1f"
                          % (ds, arm, seed, res["gself"]["alpha_linf"],
                             res["gself"]["err_group"], res["gself"]["err_cs"],
                             res["gself"]["seconds"]), flush=True)
                tag = "_%s_%s" % (arm, ds)
                pd.DataFrame(gs_rows).to_csv(OUT / ("A1_GSELF_part%s.csv" % tag), index=False)
                pd.DataFrame(sens_rows).to_csv(OUT / ("A1_SENS_part%s.csv" % tag), index=False)
                (OUT / ("A1_META_part%s.json" % tag)).write_text(
                    json.dumps(meta, indent=2, default=str), encoding="utf-8")
                print("part written for %s %s rows=%d" % (arm, ds, len(sens_rows)), flush=True)
    if args.merge:
        gs = sorted(OUT.glob("A1_GSELF_part_*.csv"))
        se = sorted(OUT.glob("A1_SENS_part_*.csv"))
        mt = sorted(OUT.glob("A1_META_part_*.json"))
        g = pd.concat([pd.read_csv(p) for p in gs], ignore_index=True)
        s = pd.concat([pd.read_csv(p) for p in se], ignore_index=True)
        meta = [json.loads(p.read_text(encoding="utf-8")) for p in mt]
        g.to_csv(OUT / "A1_GSELF.csv", index=False)
        s.to_csv(OUT / "A1_SENS_GRID.csv", index=False)
        # ---- tau_x per (ds, arm) and reference residual
        summ, tau = [], {}
        for (ds, arm), gg in s.groupby(["ds", "arm"]):
            sp_g = float((gg.groupby("seed")["d_group"].max()
                          - gg.groupby("seed")["d_group"].min()).max())
            sp_c = float((gg.groupby("seed")["d_cs"].max()
                          - gg.groupby("seed")["d_cs"].min()).max())
            t_x = 10.0 * max(sp_g, sp_c)
            tau[(ds, arm)] = t_x
            summ.append({"ds": ds, "arm": arm, "n_cells": int(gg.shape[0]),
                         "spread_d_group": sp_g, "spread_d_cs": sp_c,
                         "tau_x": t_x, "tau_limit_5e-6": TAU_LIMIT,
                         "tau_x_le_5e-6": bool(t_x <= TAU_LIMIT),
                         "max_alpha_linf_vs_trained": float(gg.alpha_linf_vs_trained.max()),
                         "min_alpha_linf_vs_trained": float(gg.alpha_linf_vs_trained.min()),
                         "solver_fails": int(gg.solver_fails.sum()),
                         "max_abs_dd_group": float(gg.abs_dd_group.max()),
                         "max_abs_dd_cs": float(gg.abs_dd_cs.max())})
        sm = pd.DataFrame(summ)
        sm.to_csv(OUT / "A1_SENS_SUMMARY.csv", index=False)
        # ---- gates
        gates = []
        for _, r in g.iterrows():
            obs = max(float(r.alpha_linf), float(r.err_group), float(r.err_cs))
            gates.append({"ds": r.ds, "arm": r.arm, "seed": int(r.seed), "gate": "B-G1",
                          "observed": int(r.b_g1_mismatch_windows), "tolerance": 0.0,
                          "tolerance_source": ("exact active-set identity vs "
                                               "artifacts/e3_formal_runs_r1/runs/<ds>/raven/"
                                               "seed<seed>/window_metrics.json (PREREG 2.5)"),
                          "pass": bool(int(r.b_g1_mismatch_windows) == 0)})
            gates.append({"ds": r.ds, "arm": r.arm, "seed": int(r.seed), "gate": "G-self",
                          "observed": obs, "tolerance": GSELF_TOL,
                          "tolerance_source": ("PREREG 2.2: alpha L-inf must be 0; both "
                                               "endpoints <= 1e-12 (protocol A1-G-self)"),
                          "pass": bool(r["pass"])})
        for (ds, arm), gg in s.groupby(["ds", "arm"]):
            t_x = tau[(ds, arm)]
            rstar = gg[gg.is_reference_cell.astype(bool)]
            ok_tau = bool(t_x <= TAU_LIMIT)
            for seed, sub in rstar.groupby("seed"):
                resid = float(max(sub.abs_dd_group.iloc[0], sub.abs_dd_cs.iloc[0]))
                gates.append({"ds": ds, "arm": arm, "seed": int(seed), "gate": "G-xref",
                              "observed": resid,
                              "tolerance": t_x,
                              "tolerance_source": ("PREREG 2.4 = protocol A1-G-xref: 10 x "
                                                   "largest endpoint spread across the "
                                                   "A1-sens grid (arm, dataset)"),
                              "pass": bool(resid <= t_x and ok_tau)})
        gd = pd.DataFrame(gates)
        gd.to_csv(OUT / "GATES_V5.csv", index=False)
        # ---- pass / stop summary
        fail_self = gd[(gd.gate == "G-self") & (~gd["pass"].astype(bool))]
        first_div = {}
        for _, r in fail_self.iterrows():
            key = "%s|%s" % (r.ds, r.arm)
            fd = g[(g.ds == r.ds) & (g.arm == r.arm) & (g.seed == r.seed)]
            first_div[key] = int(fd.first_diverging_window.iloc[0]) \
                if pd.notna(fd.first_diverging_window.iloc[0]) else None
        summary = {"a1_g_self_rows": int((gd.gate == "G-self").sum()),
                   "a1_g_self_pass": int(((gd.gate == "G-self") & gd["pass"].astype(bool)).sum()),
                   "a1_g_self_fail_cells": first_div,
                   "a1_g_xref_rows": int((gd.gate == "G-xref").sum()),
                   "a1_g_xref_pass": int(((gd.gate == "G-xref") & gd["pass"].astype(bool)).sum()),
                   "tau_x": {"%s|%s" % k: v for k, v in tau.items()},
                   "tau_x_le_5e-6": {"%s|%s" % k: bool(v <= TAU_LIMIT) for k, v in tau.items()},
                   "b_g1_mismatch_total": int(g.b_g1_mismatch_windows.sum()),
                   "misaligned_or_missing": meta,
                   "ref_impl_linf_max": None if s.ref_impl_linf.isna().all()
                   else float(s.ref_impl_linf.max()),
                   "n_runs_gself": int(len(g))}
        (OUT / "A1_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str),
                                             encoding="utf-8")
        print(json.dumps(summary, indent=2, default=str))
        print(sm.to_string(index=False))


if __name__ == "__main__":
    main()
