"""Decide the ball-branch parametrization empirically: inner cap hi vs hi/s, measured by the
objective against a fresh CVXPY solve (development diagnostic; writes nothing)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51a_oracle as O                                                     # noqa: E402

TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"


def cvx_proj(beta, a_bar, e_bar):
    import cvxpy as cp
    K = int(np.asarray(beta).size)
    x = cp.Variable(K)
    con = [cp.sum(x) == 1.0, x >= 0.0, x <= float(a_bar),
           cp.sum_squares(x) <= 1.0 / float(e_bar)]
    pr = cp.Problem(cp.Minimize(cp.sum_squares(x - np.asarray(beta, dtype=float))), con)
    pr.solve(solver=cp.CLARABEL, verbose=False)
    return np.asarray(x.value, dtype=float), str(pr.status)


def branch(v, hi, t, cap_scaled):
    """Return (x, u, tp) for the ball-active branch with the inner cap hi or u*hi."""
    K = int(v.size)
    x1, tp1, _k = O.capped_simplex(v, hi)
    if float(x1 @ x1) <= t:
        return x1, 1.0, tp1
    u0 = 1.0 / (K * hi) * (1.0 + 16 * np.finfo(float).eps)
    lo, up = u0, 1.0
    bx, bu, bt = x1, 1.0, tp1
    for _ in range(200):
        mid = 0.5 * (lo + up)
        cap = mid * hi if cap_scaled else hi
        xm, tm, _k2 = O.capped_simplex(mid * v, cap)
        if float(xm @ xm) > t:
            up = mid
        else:
            lo = mid
            bx, bu, bt = xm, mid, tm
        if up - lo <= 1e-18 * max(1.0, up):
            break
    return bx, bu, bt


def main() -> None:
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    pi = {d: W.pi_tar_for(d) for d in ("sensorscope", "uair")}
    rows = []
    for ds in ("sensorscope", "uair"):
        for seed in range(30001, 30001 + n_runs):
            case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
            for j in range(case["n"]):
                K = len(case["clients"][j])
                if K < 3:
                    continue
                b = np.asarray(case["beta"][j], dtype=float)
                b = b / b.sum()
                hi, eb = case["a_bar"][j], case["e_bar"][j]
                t = 1.0 / eb
                x0, tp0, _k = O.capped_simplex(b, hi)
                if float(x0 @ x0) <= t:
                    continue
                xa, ua, tpa = branch(b, hi, t, False)
                xb, ub, tpb = branch(b, hi, t, True)
                a_cx, st = cvx_proj(b, hi, eb)
                rows.append({"K": K, "oa": O.proj_objective(xa, b), "ob": O.proj_objective(xb, b),
                             "oc": O.proj_objective(a_cx, b), "status": st,
                             "na": float(xa @ xa), "nb": float(xb @ xb),
                             "ua": ua, "ub": ub, "t": t})
    import pandas as pd
    df = pd.DataFrame(rows)
    print("windows", len(df))
    print("cap=hi : better than cvxpy %d/%d   max(obj_a - obj_c) = %.3e"
          % (int((df.oa <= df.oc + 1e-12).sum()), len(df), float((df.oa - df.oc).max())))
    print("cap=u*hi: better than cvxpy %d/%d   max(obj_b - obj_c) = %.3e"
          % (int((df.ob <= df.oc + 1e-12).sum()), len(df), float((df.ob - df.oc).max())))
    print(df.sort_values("oa", ascending=False).head(8).to_string(index=False))


if __name__ == "__main__":
    main()
