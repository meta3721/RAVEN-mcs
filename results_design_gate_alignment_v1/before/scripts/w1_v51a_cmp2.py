"""Compare the production oracle against a fresh CVXPY CLARABEL solve over many windows, for both
the projection and the debt objective (development diagnostic; writes nothing).

The O-G1 gate in the rerun is exactly this comparison restricted to 200 sampled windows.
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
KAPPA = 1000.0


def _solve(kind, K, a_bar, e_bar, v=None, M=None, Q=None, beta=None):
    import cvxpy as cp
    x = cp.Variable(K)
    if kind == "proj":
        obj = cp.sum_squares(x - np.asarray(v, dtype=float))
    else:
        obj = (-np.asarray(Q, dtype=float) @ (np.asarray(M, dtype=float) @ x)
               + (1.0 / (2.0 * KAPPA)) * cp.sum_squares(x - np.asarray(beta, dtype=float)))
    con = [cp.sum(x) == 1.0, x >= 0.0, x <= float(a_bar),
           cp.sum_squares(x) <= 1.0 / float(e_bar)]
    pr = cp.Problem(cp.Minimize(obj), con)
    pr.solve(solver=cp.CLARABEL, verbose=False)
    if x.value is None:
        return None, str(pr.status)
    return np.asarray(x.value, dtype=float), str(pr.status)


def main() -> None:
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    pi = {d: W.pi_tar_for(d) for d in ("sensorscope", "uair")}
    rows = []
    for ds in ("sensorscope", "uair"):
        for arm in ("proj_beta", "proj_beta_debt"):
            for seed in range(30001, 30001 + n_runs):
                case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
                if case is None:
                    continue
                wm = W.load_json(TRAIN / ds / arm / ("seed%d" % seed) / "window_metrics.json")
                by = {int(w["window_id"]): w for w in W.active_windows(wm)}
                betas = [np.asarray(by[int(case["wids"][k])]["beta_hat"], dtype=float)
                         for k in range(case["n"])]
                if arm == "proj_beta":
                    a_or, diag = O.oracle_proj_beta(betas, case)
                    qs = [None] * case["n"]
                else:
                    a_or, qs, diag = O.oracle_debt_seq(case, betas)
                off = 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    a = a_or[off:off + K]
                    off += K
                    hi, eb = case["a_bar"][j], case["e_bar"][j]
                    v = diag[j]["v"]
                    if arm == "proj_beta":
                        o_or = O.proj_objective(a, v)
                        x_cx, status = _solve("proj", K, hi, eb, v=v)
                        o_cx = None if x_cx is None else O.proj_objective(x_cx, v)
                        o_pb = (None if x_cx is None else
                                O.proj_objective(O.project_Cr(x_cx, hi, eb)[0], v))
                    else:
                        M, Q, beta = case["M"][j], qs[j], diag[j]["beta"]
                        o_or = O.debt_objective(a, beta, M, Q)
                        x_cx, status = _solve("debt", K, hi, eb, M=M, Q=Q, beta=beta)
                        o_cx = None if x_cx is None else O.debt_objective(x_cx, beta, M, Q)
                        o_pb = (None if x_cx is None else
                                O.debt_objective(O.project_Cr(x_cx, hi, eb)[0], beta, M, Q))
                    if x_cx is None:
                        continue
                    rows.append({"ds": ds, "arm": arm, "seed": seed, "j": j, "K": K,
                                 "kind": diag[j]["kind"], "obj_oracle": o_or, "obj_cvx": o_cx,
                                 "obj_cvx_projected": o_pb,
                                 "gap_vs_cvx_projected": o_or - o_pb,
                                 "feas_cvx": O.feasibility(x_cx, hi, eb),
                                 "feas_oracle": O.feasibility(a, hi, eb), "status": status})
    import pandas as pd
    df = pd.DataFrame(rows)
    print("windows", len(df))
    df["pass"] = df.gap_vs_cvx_projected <= 1e-12
    df["cvx_feasible"] = df.feas_cvx <= 1e-12
    print(df.groupby(["ds", "arm"])[["gap_vs_cvx_projected", "feas_oracle", "feas_cvx"]].max()
          .to_string())
    print("gate vs projected comparator: passed %d/%d" % (int(df["pass"].sum()), len(df)))
    bad = df[(~df["pass"])]
    print("failing rows: %d, of which the comparator is itself infeasible: %d"
          % (len(bad), int((~bad.cvx_feasible).sum())))
    infeas = df[~df.cvx_feasible]
    if len(infeas):
        print("max comparator violation %.3e; oracle vs raw (infeasible) comparator: max %.3e"
              % (float(infeas.feas_cvx.max()),
                 float((infeas.obj_oracle - infeas.obj_cvx).max())))
    print(df.sort_values("gap_vs_cvx_projected", ascending=False).head(8).to_string(index=False))


if __name__ == "__main__":
    main()
