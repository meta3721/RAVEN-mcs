"""T4 + T5 (round v3, EXPLORATORY): grid extension and online debt-strength sweep.

T4: L3 eps in {1,3,10,30,100,1000} (+ inf == B1), L4 lambda_v in {0,1e-3,3e-3,1e-2},
    L5 lambda_g in {0,0.1,0.3,1} with instant_calibration=False (outside the paper's legal P2 domain),
    tune seeds only.
T5: alpha_r = argmin_{C_r} -kappa Q^T M_r a + 1/2||a - beta||^2  [+ 1/2||M_r a - mu||^2 variant]
    Q_{r+1} = max(Q_r + 0.01 (mu - M_r a_r), 0), Q_0 = 0.  kappa = 0 must equal B1(raven).

Read-only: writes only results_w1_ladder/round_v3/.
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
from raven_mcs.aggregation.p2_cvxpy import solve_p2                          # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v3"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
EPS_T4 = (1.0, 3.0, 10.0, 30.0, 100.0, 1000.0)
LAMV_T4 = (0.0, 0.001, 0.003, 0.01)
LAMG_T4 = (0.0, 0.1, 0.3, 1.0)
KAPPA = (0.0, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0)
VARIANTS = ("q_only", "q_plus_group")
ETA = 0.01
_c: dict = {}


def beta_from_raven(case: dict, ds: str, seed: int):
    act = W.active_windows(json.loads((E3 / ds / "raven" / f"seed{seed}" /
                                       "window_metrics.json").read_text(encoding="utf-8")))
    by = {int(x["window_id"]): x for x in act}
    out = []
    for j in range(case["n"]):
        x = by.get(int(case["wids"][j]))
        if x is None or len(x["beta_hat"]) != len(case["clients"][j]):
            return None
        out.append(np.asarray(x["beta_hat"], dtype=float))
    return out


def p2_seq(case: dict, lam_g: float, instant: bool, debt_source: str = "zero"):
    alphas, warns = [], 0
    G = case["G"]
    for j in range(case["n"]):
        debt = (np.asarray(case["debt"][j], dtype=float) if debt_source == "recorded"
                else np.zeros(G))
        r = solve_p2(coverage_matrix=case["M"][j], mu=case["mu"],
                     beta_reference=case["beta"][j], debt=debt,
                     variance_diag=case["variance"][j], staleness=case["staleness"][j],
                     lambda_group=float(lam_g), lambda_beta=1.0, lambda_variance=0.1,
                     lambda_staleness=0.1, alpha_max=0.5, e_min=3.0,
                     max_server_learning_rate=1.0, tolerance=1e-6, backend="CLARABEL",
                     instant_calibration=instant)
        alphas.append(np.asarray(r.alpha, dtype=float))
        if r.fallback_used or r.feasibility_repair_used or r.status != "optimal":
            warns += 1
    return np.concatenate(alphas), warns


def kappa_seq(case: dict, kappa: float, variant: str, betas: list):
    """Self-consistent debt recursion; returns alphas, Q trace, warning count."""
    K_G = case["G"]
    Q = np.zeros(K_G)
    alphas, warns = [], 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        key = ("kap", K_G, K, variant)
        if key not in _c:
            Mp = cp.Parameter((K_G, K))
            bp = cp.Parameter(K)
            qp = cp.Parameter(K_G)
            kp = cp.Parameter(nonneg=True)
            abp = cp.Parameter(nonneg=True)
            ebp = cp.Parameter(nonneg=True)
            x = cp.Variable(K)
            obj = -kp * (qp @ (Mp @ x)) + 0.5 * cp.sum_squares(x - bp)
            if variant == "q_plus_group":
                obj = obj + 0.5 * cp.sum_squares(Mp @ x - case["mu"])
            pr = cp.Problem(cp.Minimize(obj), [cp.sum(x) == 1.0, x >= 0.0, x <= abp,
                                              cp.sum_squares(x) <= 1.0 / ebp])
            _c[key] = (Mp, bp, qp, kp, abp, ebp, x, pr)
        Mp, bp, qp, kp, abp, ebp, x, pr = _c[key]
        Mp.value = case["M"][j]
        bp.value = betas[j]
        qp.value = Q
        kp.value = float(kappa)
        abp.value = case["a_bar"][j]
        ebp.value = case["e_bar"][j]
        try:
            pr.solve(solver=cp.CLARABEL, verbose=False)
            a = np.asarray(x.value, dtype=float).clip(0.0, None)
        except Exception:
            a = betas[j].copy()
            warns += 1
        alphas.append(a)
        Q = np.maximum(Q + ETA * (case["mu"] - case["M"][j] @ a), 0.0)
    return np.concatenate(alphas), warns


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v3")
    args = ap.parse_args()
    global OUT
    OUT = ROOT / "results_w1_ladder" / args.round
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    star = pd.read_csv(ROOT / "results_w1_ladder/round_v2/FRONTIER.csv")
    star = star[star.ruler == "R_on"].groupby(["ds", "seed"])[
        ["d_unif_group", "d_star_group", "d_unif_cs", "d_star_cs"]].first().reset_index()
    grid_rows, debt_rows, check = [], [], []
    for ds in W.DS:
        for seed in W.SEEDS:
            case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
            if case is None:
                continue
            betas = beta_from_raven(case, ds, seed)
            if betas is None:
                continue
            case["beta"] = betas
            st = star[(star.ds == ds) & (star.seed == seed)]
            du = float(st["d_unif_group"].iloc[0]) if len(st) else np.nan
            dstar = float(st["d_star_group"].iloc[0]) if len(st) else np.nan
            du_cs = float(st["d_unif_cs"].iloc[0]) if len(st) else np.nan
            dstar_cs = float(st["d_star_cs"].iloc[0]) if len(st) else np.nan
            split = "report" if seed in W.REPORT else "tune"
            if split == "tune":                                  # T4: tune seeds only
                for eps in EPS_T4:
                    try:
                        a = L.alpha_match(case, eps=eps)
                        dg, dcs = L.endpoints(case, a)
                    except Exception:
                        continue
                    grid_rows.append({"ds": ds, "seed": seed, "family": "L3_eps", "config": eps,
                                      "d_group": dg, "d_cs": dcs})
                try:
                    bs = np.concatenate(betas)
                    a = L.project_seq(case, bs)
                    dg, dcs = L.endpoints(case, a)
                    grid_rows.append({"ds": ds, "seed": seed, "family": "L3_eps", "config": np.inf,
                                      "d_group": dg, "d_cs": dcs})
                except Exception:
                    pass
                for lv in LAMV_T4:
                    try:
                        a = L.alpha_match(case, eps=1.0, lam_v=lv)
                        dg, dcs = L.endpoints(case, a)
                    except Exception:
                        continue
                    grid_rows.append({"ds": ds, "seed": seed, "family": "L4_lam_v", "config": lv,
                                      "d_group": dg, "d_cs": dcs})
                for lg in LAMG_T4:
                    try:
                        a, _ = p2_seq(case, lg, instant=False)
                        dg, dcs = L.endpoints(case, a)
                    except Exception:
                        continue
                    grid_rows.append({"ds": ds, "seed": seed, "family": "L5_lam_g_instant_off",
                                      "config": lg, "d_group": dg, "d_cs": dcs})
            for variant in VARIANTS:                              # T5: all seeds
                for kap in KAPPA:
                    a, warns = kappa_seq(case, kap, variant, betas)
                    dg, dcs = L.endpoints(case, a)
                    blocks, off = [], 0
                    for j in range(case["n"]):
                        K = len(case["clients"][j])
                        blocks.append(a[off:off + K])
                        off += K
                    ess = [1.0 / max(float(b @ b), 1e-12) for b in blocks]
                    debt_rows.append({"ds": ds, "variant": variant, "kappa": kap, "seed": seed,
                                      "split": split, "d_group": dg, "d_cs": dcs,
                                      "tv_group_pp": 100 * dg / 2,
                                      "G_group": None if not np.isfinite(du) or du - dstar <= 0
                                      else (du - dg) / (du - dstar),
                                      "G_cs": None if dcs is None or not np.isfinite(du_cs)
                                      or du_cs - dstar_cs <= 0 else (du_cs - dcs) / (du_cs - dstar_cs),
                                      "max_alpha": float(max(float(b.max()) for b in blocks)),
                                      "min_ess": float(min(ess)), "warnings": warns})
                    if variant == "q_only" and kap == 0.0:
                        b1 = L.project_seq(case, np.concatenate(betas))
                        dg_b1, _ = L.endpoints(case, b1)
                        check.append({"ds": ds, "seed": seed, "kappa0_vs_B1_raven":
                                      abs(dg - dg_b1)})
    pd.DataFrame(grid_rows).to_csv(OUT / "GRID_EXTENSION.csv", index=False)
    dd = pd.DataFrame(debt_rows)
    dd.to_csv(OUT / "DEBT_STRENGTH.csv", index=False)
    ck = pd.DataFrame(check)
    summ = {"t4_rows": len(grid_rows), "t5_rows": len(dd),
            "kappa0_vs_B1_raven_max": float(ck["kappa0_vs_B1_raven"].max()) if len(ck) else None,
            "kappa0_pass": bool(len(ck) and ck["kappa0_vs_B1_raven"].max() <= 1e-9)}
    if len(dd):
        for variant in VARIANTS:
            g = dd[(dd.variant == variant) & (dd.split == "tune")]
            means = g.groupby("kappa")["d_group"].mean()
            summ[f"tune_best_kappa_{variant}"] = float(means.idxmin())
            summ[f"tune_curve_{variant}"] = {float(k): round(float(v), 6) for k, v in means.items()}
            r = dd[(dd.variant == variant) & (dd.split == "report")]
            best = summ[f"tune_best_kappa_{variant}"]
            sel = r[np.isclose(r["kappa"], best)]
            summ[f"report_best_{variant}"] = {
                "kappa": best, "d_group": float(sel["d_group"].mean()),
                "tv_group_pp": float(sel["tv_group_pp"].mean()),
                "G_group": float(sel["G_group"].mean()) if sel["G_group"].notna().any() else None,
                "d_cs": float(sel["d_cs"].mean())}
    (OUT / "EXPLORE_SUMMARY.json").write_text(json.dumps(summ, indent=2, default=str),
                                              encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))


if __name__ == "__main__":
    main()
