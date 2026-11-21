"""T7 (round v3): degeneracy of the per-window L1 matching on C_r.

Per active window: min ||M_r a - mu||_1 (exact, cvxpy), max (projected-gradient ascent from
random starts; the true max is attained at an extreme point, so this is a LOWER bound on the
true range and is labelled max_approx), and the tie-broken min ||M_r a - mu||_1 + 1e-6||a-beta||^2.

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

OUT = ROOT / "results_w1_ladder/round_v3"
N_STARTS, N_ITER, TIE = 40, 60, 1e-6
_qp: dict = {}


def project(a: np.ndarray, ab: float, eb: float) -> np.ndarray:
    K = len(a)
    key = ("proj", K)
    if key not in _qp:
        par = cp.Parameter(K)
        abp = cp.Parameter(nonneg=True)
        ebp = cp.Parameter(nonneg=True)
        x = cp.Variable(K)
        pr = cp.Problem(cp.Minimize(cp.sum_squares(x - par)),
                        [cp.sum(x) == 1.0, x >= 0.0, x <= abp, cp.sum_squares(x) <= 1.0 / ebp])
        _qp[key] = (par, abp, ebp, x, pr)
    par, abp, ebp, x, pr = _qp[key]
    par.value = a
    abp.value = ab
    ebp.value = eb
    pr.solve(solver=cp.CLARABEL, verbose=False)
    return np.asarray(x.value, dtype=float).clip(0.0, 1.0)


def solve_min(case: dict, j: int, beta: np.ndarray, tie: bool):
    M, K = case["M"][j], len(case["clients"][j])
    key = ("min", case["G"], K, tie)
    if key not in _qp:
        Mp = cp.Parameter((case["G"], K))
        bp = cp.Parameter(K)
        x = cp.Variable(K)
        abp = cp.Parameter(nonneg=True)
        ebp = cp.Parameter(nonneg=True)
        obj = cp.norm1(Mp @ x - case["mu"])
        if tie:
            obj = obj + TIE * cp.sum_squares(x - bp)
        pr = cp.Problem(cp.Minimize(obj), [cp.sum(x) == 1.0, x >= 0.0, x <= abp,
                                          cp.sum_squares(x) <= 1.0 / ebp])
        _qp[key] = (Mp, bp, abp, ebp, x, pr)
    Mp, bp, abp, ebp, x, pr = _qp[key]
    Mp.value = M
    bp.value = beta
    abp.value = case["a_bar"][j]
    ebp.value = case["e_bar"][j]
    pr.solve(solver=cp.CLARABEL, verbose=False)
    a = np.asarray(x.value, dtype=float).clip(0.0, None)
    return a, float(np.abs(M @ a - case["mu"]).sum())


def solve_max(case: dict, j: int, rng) -> float:
    """Lower bound on max ||M a - mu||_1: best of uniform and, for each client, the
    ball-boundary point in that client's direction (feasible by construction)."""
    M, K = case["M"][j], len(case["clients"][j])
    ab, eb = case["a_bar"][j], case["e_bar"][j]
    lim = 1.0 / eb
    cands = [np.full(K, 1.0 / K)]

    def ball_norm(lam: float) -> float:
        return ((1.0 - lam) ** 2 + 2.0 * lam * (1.0 - lam)) / K + lam ** 2

    for i in range(K):
        if ball_norm(1.0) <= lim:
            lam = 1.0
        else:
            lo, hi = 0.0, 1.0
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if ball_norm(mid) <= lim:
                    lo = mid
                else:
                    hi = mid
            lam = lo
        a = np.full(K, (1.0 - lam) / K)
        a[i] += lam
        a = np.minimum(a, ab)
        a = a / a.sum()
        if float(a @ a) > lim + 1e-12:
            a = project(a, ab, eb)
        cands.append(a)
    return max(float(np.abs(M @ a - case["mu"]).sum()) for a in cands)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v3")
    ap.add_argument("--seeds", type=int, default=20)
    args = ap.parse_args()
    global OUT
    OUT = ROOT / "results_w1_ladder" / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    rng = np.random.default_rng(20261002)
    rows, per_seed = [], []
    for ds in W.DS:
        for seed in W.SEEDS[:args.seeds]:
            case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
            if case is None:
                continue
            myo, myo_tb, unif, ranges = [], [], [], []
            for j in range(case["n"]):
                beta = np.asarray(case["beta"][j], dtype=float)
                a_min, v_min = solve_min(case, j, beta, tie=False)
                a_tb, v_tb = solve_min(case, j, beta, tie=True)
                v_max = solve_max(case, j, rng)
                K = len(case["clients"][j])
                unif.append(1.0 / K)
                myo.append(a_min)
                myo_tb.append(a_tb)
                ranges.append({"ds": ds, "seed": seed, "window": int(case["wids"][j]),
                               "K": K, "min_l1": v_min, "max_approx": v_max,
                               "range": v_max - v_min, "tie_min_l1": v_tb})
            rows.extend(ranges)

            def seq(blocks):
                return L.endpoints(case, np.concatenate(blocks))

            g_myo, c_myo = seq(myo)
            g_tb, c_tb = seq(myo_tb)
            g_un, c_un = seq([np.full(len(c), 1.0 / len(c)) for c in case["clients"]])
            per_seed.append({"ds": ds, "seed": seed, "d_myo": g_myo, "d_myo_cs": c_myo,
                             "d_myo_tb": g_tb, "d_myo_tb_cs": c_tb, "d_unif": g_un,
                             "d_unif_cs": c_un, "range_median": float(np.median([r["range"] for r in ranges])),
                             "range_p90": float(np.percentile([r["range"] for r in ranges], 90))})
    wr = pd.DataFrame(rows)
    wr.to_csv(OUT / "MYOPIC_WINDOWS.csv", index=False)
    ps = pd.DataFrame(per_seed)
    ps.to_csv(OUT / "MYOPIC_DIAG.csv", index=False)
    q = wr["range"].quantile([0.05, 0.25, 0.5, 0.75, 0.95]).round(6).to_dict()
    summ = {"n_windows": int(len(wr)), "range_quantiles": q,
            "range_median": float(wr["range"].median()),
            "min_l1_median": float(wr["min_l1"].median()),
            "max_approx_median": float(wr["max_approx"].median()),
            "degenerate_below_1e-3": bool(float(wr["range"].median()) < 1e-3),
            "per_ds_median_range": wr.groupby("ds")["range"].median().round(6).to_dict(),
            "d_myo_vs_unif": {"d_myo": float(ps.d_myo.mean()), "d_myo_tb": float(ps.d_myo_tb.mean()),
                              "d_unif": float(ps.d_unif.mean()),
                              "max_abs_diff_myo_vs_unif": float((ps.d_myo - ps.d_unif).abs().max()),
                              "max_abs_diff_tb_vs_unif": float((ps.d_myo_tb - ps.d_unif).abs().max())}}
    (OUT / "MYOPIC_DIAG.json").write_text(json.dumps(summ, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))


if __name__ == "__main__":
    main()
