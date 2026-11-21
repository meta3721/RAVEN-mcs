"""Compare the v5.1a oracle against a fresh CVXPY CLARABEL solve on failing windows
(development diagnostic; writes nothing).  Reports objective gap and feasibility of both.
"""
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


def cvx_proj(beta, a_bar, e_bar, tol=1e-12):
    import cvxpy as cp
    K = int(np.asarray(beta).size)
    x = cp.Variable(K)
    con = [cp.sum(x) == 1.0, x >= 0.0, x <= float(a_bar),
           cp.sum_squares(x) <= 1.0 / float(e_bar)]
    pr = cp.Problem(cp.Minimize(cp.sum_squares(x - np.asarray(beta, dtype=float))), con)
    pr.solve(solver=cp.CLARABEL, verbose=False, tol_gap_abs=tol, tol_gap_rel=tol,
             tol_feas=tol)
    return np.asarray(x.value, dtype=float), str(pr.status)


def main() -> None:
    cases = []
    for ds, arm, seed, js in (("sensorscope", "proj_beta", 30002, [10, 4, 32]),
                              ("uair", "proj_beta", 30001, [52, 39, 24])):
        case = W.build_case(ds, "R_on", "raven_wo_use", seed, W.pi_tar_for(ds))
        wm = W.load_json(TRAIN / ds / arm / ("seed%d" % seed) / "window_metrics.json")
        by = {int(w["window_id"]): w for w in W.active_windows(wm)}
        for j in js:
            b = np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
            b = b / b.sum()
            ab, eb = case["a_bar"][j], case["e_bar"][j]
            a_or, kind, mult = O.project_Cr(b, ab, eb)
            a_cx, status = cvx_proj(b, ab, eb)
            o_or = O.proj_objective(a_or, b)
            o_cx = O.proj_objective(a_cx, b)
            a_pb, _k2, _m2 = O.project_Cr(a_cx, ab, eb)
            o_pb = O.proj_objective(a_pb, b)
            cases.append({"ds": ds, "seed": seed, "j": j, "K": b.size, "kind": kind,
                          "obj_oracle": o_or, "obj_cvx": o_cx, "obj_cvx_proj": o_pb,
                          "gap_vs_cvx": o_or - o_cx, "gap_vs_cvx_projected": o_or - o_pb,
                          "status": status, "feas_cvx": O.feasibility(a_cx, ab, eb),
                          "feas_oracle": O.feasibility(a_or, ab, eb),
                          "u": mult["u"], "tau_s": mult["tau_scaled"],
                          "lam_s": mult["lam_scaled"]})
    import pandas as pd
    df = pd.DataFrame(cases)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
