"""A2 + A3 (round v4): shared projection, per-dataset kappa sweep, big-eps re-solve.

proj_Cr is the single projection used by B1 and by the kappa sweep (cvxpy + CLARABEL, tol 1e-10).
A2 rule: alpha_r = argmin_{C_r} -kappa Q_r^T M_r a + 1/2||a - beta_r||^2,
         Q_{r+1} = max(Q_r + 0.01 (mu - M_r a_r), 0), Q_0 = 0, self-consistent.
A3 rule: (1/eps)*1/2||M a - mu||^2 + 1/2||a - beta||^2, eps in {10,30,100,1000}, eps=inf = proj_Cr.

Read-only: writes only results_w1_ladder/round_v4/.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import cvxpy as cp
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                       # noqa: E402
import w1_ladder as L                                                       # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v4"
V2 = ROOT / "results_w1_ladder/round_v2"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
KAPPAS = (0, 1, 3, 10, 30, 100, 300, 1000, 3000, 10_000, 30_000, 100_000)
EPS_V4 = (10.0, 30.0, 100.0, 1000.0)
ETA, TOL = 0.01, 1e-10
_p: dict = {}


def proj_Cr(beta: np.ndarray, a_bar: float, e_bar: float, K: int) -> np.ndarray:
    """Euclidean projection onto C_r (single implementation for B1 and A2/A3)."""
    key = ("proj", K)
    if key not in _p:
        par = cp.Parameter(K)
        ab = cp.Parameter(nonneg=True)
        eb = cp.Parameter(nonneg=True)
        x = cp.Variable(K)
        pr = cp.Problem(cp.Minimize(cp.sum_squares(x - par)),
                        [cp.sum(x) == 1.0, x >= 0.0, x <= ab, cp.sum_squares(x) <= 1.0 / eb])
        _p[key] = (par, ab, eb, x, pr)
    par, ab, eb, x, pr = _p[key]
    par.value = np.asarray(beta, dtype=float)
    ab.value = float(a_bar)
    eb.value = float(e_bar)
    pr.solve(solver=cp.CLARABEL, verbose=False, tol_gap_abs=TOL, tol_gap_rel=TOL,
             tol_feas=TOL)
    return np.asarray(x.value, dtype=float).clip(0.0, None)


def proj_seq(case: dict, betas: list) -> np.ndarray:
    return np.concatenate([proj_Cr(betas[j], case["a_bar"][j], case["e_bar"][j],
                                   len(case["clients"][j])) for j in range(case["n"])])


def kappa_seq(case: dict, kappa: float, betas: list):
    """kappa = 0 solves the projection objective (same function as proj_Cr effectively);
    kappa > 0 uses the algebraically equivalent rescaled form -Q^T M a + (1/(2k))||a-b||^2
    (better conditioned at large kappa).  Failures are recorded, not silently dropped."""
    Q = np.zeros(case["G"])
    alphas, diag, fails = [], [], 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        key = ("kap", case["G"], K)
        if key not in _p:
            Mp = cp.Parameter((case["G"], K))
            bp = cp.Parameter(K)
            qp = cp.Parameter(case["G"])
            kp = cp.Parameter(nonneg=True)
            ab = cp.Parameter(nonneg=True)
            eb = cp.Parameter(nonneg=True)
            x = cp.Variable(K)
            obj = cp.Minimize(-qp @ (Mp @ x) + kp * 0.5 * cp.sum_squares(x - bp))
            pr = cp.Problem(obj, [cp.sum(x) == 1.0, x >= 0.0, x <= ab,
                                  cp.sum_squares(x) <= 1.0 / eb])
            _p[key] = (Mp, bp, qp, kp, ab, eb, x, pr)
        Mp, bp, qp, kp, ab, eb, x, pr = _p[key]
        Mp.value = case["M"][j]
        bp.value = betas[j]
        qp.value = Q
        kp.value = float("inf") if kappa == 0 else 1.0 / float(kappa)
        ab.value = case["a_bar"][j]
        eb.value = case["e_bar"][j]
        a = None
        for solver in (cp.CLARABEL, cp.SCS):
            try:
                pr.solve(solver=solver, verbose=False)
                a = np.asarray(x.value, dtype=float).clip(0.0, None)
                break
            except Exception:
                a = None
        if a is None:
            fails += 1
            a = proj_Cr(betas[j], case["a_bar"][j], case["e_bar"][j], K)
        alphas.append(a)
        if K >= 2:
            diag.append({"cap_bind": bool(float(a.max()) >= case["a_bar"][j] - 1e-9),
                         "l2_bind": bool(float(a @ a) >= 1.0 / case["e_bar"][j] - 1e-9),
                         "vertex": bool(int(np.sum(a > 1e-9)) == 1)})
        Q = np.maximum(Q + ETA * (case["mu"] - case["M"][j] @ a), 0.0)
    return np.concatenate(alphas), diag, fails


def eps_seq(case: dict, eps: float, betas: list):
    """L3 with the rescaled objective (1/eps)*1/2||M a - mu||^2 + 1/2||a - beta||^2."""
    out = []
    for j in range(case["n"]):
        K = len(case["clients"][j])
        key = ("eps", case["G"], K)
        if key not in _p:
            Mp = cp.Parameter((case["G"], K))
            bp = cp.Parameter(K)
            ep = cp.Parameter(nonneg=True)
            ab = cp.Parameter(nonneg=True)
            eb = cp.Parameter(nonneg=True)
            x = cp.Variable(K)
            pr = cp.Problem(cp.Minimize((1.0 / ep) * 0.5 * cp.sum_squares(Mp @ x - case["mu"])
                                        + 0.5 * cp.sum_squares(x - bp)),
                            [cp.sum(x) == 1.0, x >= 0.0, x <= ab,
                             cp.sum_squares(x) <= 1.0 / eb])
            _p[key] = (Mp, bp, ep, ab, eb, x, pr)
        Mp, bp, ep, ab, eb, x, pr = _p[key]
        Mp.value = case["M"][j]
        bp.value = betas[j]
        ep.value = float(eps)
        ab.value = case["a_bar"][j]
        eb.value = case["e_bar"][j]
        pr.solve(solver=cp.CLARABEL, verbose=False)
        out.append(np.asarray(x.value, dtype=float).clip(0.0, None))
    return np.concatenate(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v4")
    args = ap.parse_args()
    global OUT
    OUT = ROOT / "results_w1_ladder" / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    fr = pd.read_csv(V2 / "FRONTIER.csv")
    fr = fr[fr.ruler == "R_on"].groupby(["ds", "seed"])[
        ["d_unif_group", "d_star_group", "d_unif_cs", "d_star_cs"]].first()
    debt_rows, grid_rows, gates = [], [], []
    for ds in W.DS:
        for seed in W.SEEDS:
            case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
            if case is None:
                continue
            act = W.active_windows(json.loads((E3 / ds / "raven" / f"seed{seed}" /
                                               "window_metrics.json").read_text(encoding="utf-8")))
            by = {int(x["window_id"]): x for x in act}
            betas = [np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
                     for j in range(case["n"])]
            case["beta"] = betas
            split = "report" if seed in W.REPORT else "tune"
            b1 = proj_seq(case, betas)
            dg1, dc1 = L.endpoints(case, b1)
            du = float(fr.loc[(ds, seed), "d_unif_group"])
            dst = float(fr.loc[(ds, seed), "d_star_group"])
            duc = float(fr.loc[(ds, seed), "d_unif_cs"])
            dsc = float(fr.loc[(ds, seed), "d_star_cs"])
            for kap in KAPPAS:                                   # A2
                a, diag, fails = kappa_seq(case, kap, betas)
                dg, dc = L.endpoints(case, a)
                if kap == 0:
                    gates.append({"ds": ds, "seed": seed, "kappa0_vs_B1_alpha_linf":
                                  float(np.max(np.abs(a - b1))),
                                  "kappa0_vs_B1_dgroup": abs(dg - dg1),
                                  "kappa0_vs_B1_dcs": abs(dc - dc1)})
                n2 = max(len(diag), 1)
                debt_rows.append({"ds": ds, "kappa": kap, "seed": seed, "split": split,
                                  "d_group": dg, "d_cs": dc, "tv_group_pp": 100 * dg / 2,
                                  "G_group": (du - dg) / (du - dst) if du > dst else None,
                                  "G_cs": (duc - dc) / (duc - dsc) if duc > dsc else None,
                                  "frac_cap_bind": sum(d["cap_bind"] for d in diag) / n2,
                                  "frac_l2_bind": sum(d["l2_bind"] for d in diag) / n2,
                                  "frac_vertex": sum(d["vertex"] for d in diag) / n2,
                                  "n_windows_K2plus": len(diag), "solver_fail": fails})
            for eps in EPS_V4:                                   # A3
                a = eps_seq(case, eps, betas)
                dg, dc = L.endpoints(case, a)
                grid_rows.append({"ds": ds, "seed": seed, "family": "L3_eps_rescaled",
                                  "config": eps, "d_group": dg, "d_cs": dc})
            grid_rows.append({"ds": ds, "seed": seed, "family": "L3_eps_rescaled",
                              "config": np.inf, "d_group": dg1, "d_cs": dc1})
            dd = pd.DataFrame(debt_rows)
            dd.to_csv(OUT / "DEBT_STRENGTH_V4.csv", index=False)
            pd.DataFrame(grid_rows).to_csv(OUT / "GRID_EXTENSION_V4.csv", index=False)
            print("done ds=%s seed=%d" % (ds, seed), flush=True)
    dd = pd.DataFrame(debt_rows)
    dd.to_csv(OUT / "DEBT_STRENGTH_V4.csv", index=False)
    pd.DataFrame(grid_rows).to_csv(OUT / "GRID_EXTENSION_V4.csv", index=False)
    g = pd.DataFrame(gates)
    gap = fr.reset_index().groupby("ds").apply(
        lambda x: float((x["d_unif_group"] - x["d_star_group"]).mean()), include_groups=False).to_dict()
    summ = {"projection_gate": {"max_alpha_linf": float(g["kappa0_vs_B1_alpha_linf"].max()),
                                "max_dgroup": float(g["kappa0_vs_B1_dgroup"].max()),
                                "max_dcs": float(g["kappa0_vs_B1_dcs"].max()),
                                "pass": bool(g["kappa0_vs_B1_alpha_linf"].max() <= 1e-8
                                             and max(g["kappa0_vs_B1_dgroup"].max(),
                                                     g["kappa0_vs_B1_dcs"].max()) <= 1e-9)},
            "convergence": {}, "gates_A3": {}}
    for ds in W.DS:                                              # per-dataset, never pooled
        t = dd[(dd.ds == ds) & (dd.split == "tune")]
        curve_g = t.groupby("kappa")["d_group"].mean()
        curve_c = t.groupby("kappa")["d_cs"].mean()
        last = [float(curve_g.iloc[-2]), float(curve_g.iloc[-1])]
        summ["convergence"][ds] = {
            "gap_unif_minus_star": gap.get(ds),
            "last_two_dgroup": last, "delta_vs_1pct_gap": abs(last[1] - last[0]),
            "threshold_1pct": 0.01 * float(gap.get(ds, np.nan)),
            "converged": bool(abs(last[1] - last[0]) < 0.01 * float(gap.get(ds, np.nan))),
            "best_kappa_group": float(curve_g.idxmin()), "best_kappa_cs": float(curve_c.idxmin()),
            "best_kappa_joint": float((t.groupby("kappa")[["d_group", "d_cs"]].mean().sum(axis=1)).idxmin()),
            "curve_group": {float(k): round(float(v), 6) for k, v in curve_g.items()},
            "curve_cs": {float(k): round(float(v), 6) for k, v in curve_c.items()}}
        r = dd[(dd.ds == ds) & (dd.split == "report")]
        bk = summ["convergence"][ds]["best_kappa_group"]
        sel = r[np.isclose(r.kappa, bk)]
        summ["convergence"][ds]["at_best_kappa_report"] = {
            "kappa": bk, "d_group": float(sel.d_group.mean()), "tv_group_pp": float(sel.tv_group_pp.mean()),
            "frac_vertex": float(sel.frac_vertex.mean()), "frac_cap_bind": float(sel.frac_cap_bind.mean()),
            "frac_l2_bind": float(sel.frac_l2_bind.mean())}
    gg = pd.read_csv(OUT / "GRID_EXTENSION_V4.csv")
    for ds in W.DS:
        s = gg[gg.ds == ds].groupby("config")["d_group"].mean()
        inf_v = float(s.loc[np.inf]) if np.inf in s.index else float("nan")
        e1000 = float(s.loc[1000.0]) if 1000.0 in s.index else float("nan")
        summ["gates_A3"][ds] = {"d_group_eps1000": e1000, "d_group_inf": inf_v,
                                "abs_diff": abs(e1000 - inf_v), "pass": bool(abs(e1000 - inf_v) < 1e-4)}
    (OUT / "A2A3_SUMMARY.json").write_text(json.dumps(summ, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))


if __name__ == "__main__":
    main()
