"""Test: SLSQP-based projection -- feasibility and KKT stationarity quality."""
from __future__ import annotations

import pathlib
import sys

import numpy as np
from scipy.optimize import minimize

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51_oracle as O                                                      # noqa: E402

E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"


def slsqp_project(v, hi, target):
    K = int(v.size)
    if K == 1 or hi * K <= 1.0 + 1e-15:
        return np.full(K, 1.0 / K)
    uni = np.full(K, 1.0 / K)
    if target >= float(K):
        return uni if O.feasibility(uni, hi, target) <= 1e-13 else uni
    cons = [{"type": "eq", "fun": lambda x: float(np.sum(x)) - 1.0},
            {"type": "ineq", "fun": lambda x: target - float(x @ x)}]
    bnds = [(0.0, hi)] * K
    starts = [uni, np.clip(v / max(v.sum(), 1e-300), 0.0, hi),
              O._capped_simplex(v, hi)]
    if O.feasibility(uni, hi, target) <= 1e-13:
        starts.append(uni)
    best = None
    for s in starts:
        if s is None:
            continue
        try:
            r = minimize(lambda x: float(((x - v) ** 2).sum()), np.asarray(s, dtype=float),
                         method="SLSQP", bounds=bnds, constraints=cons,
                         options={"maxiter": 1000, "ftol": 1e-16})
        except Exception:                                        # noqa: BLE001
            continue
        x = np.clip(np.asarray(r.x, dtype=float), 0.0, hi)
        x = x / x.sum()
        f = O.feasibility(x, hi, target)
        if f <= 1e-12:
            o = float(((x - v) ** 2).sum())
            if best is None or o < best[0]:
                best = (o, x)
    if best is None:
        return None
    return best[1]


def kkt_stat(x, v, hi):
    """Stationarity residual: |x - v + beta - cap + 2 mu x| with best-fit (beta, mu)."""
    free = (x > 1e-12) & (x < hi - 1e-12)
    at_hi = x >= hi - 1e-12
    if free.sum() == 0:
        return float("inf")
    A = np.stack([np.ones(int(free.sum())), 2.0 * x[free]], axis=1)
    sol, *_ = np.linalg.lstsq(A, -(x - v)[free], rcond=None)
    beta, mu = float(sol[0]), max(float(sol[1]), 0.0)
    cap = np.where(at_hi, np.maximum(x - v + beta + 2.0 * mu * x, 0.0), 0.0)
    return float(np.max(np.abs(x - v + beta - cap + 2.0 * mu * x)))


pi = {d: W.pi_tar_for(d) for d in W.DS}
worst_f = 0.0
worst_k = 0.0
n = 0
for ds in ("sensorscope", "uair"):
    for seed in W.SEEDS[:3]:
        case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
        act = W.active_windows(W.load_json(E3 / ds / "raven" / f"seed{seed}" /
                                           "window_metrics.json"))
        by = {int(x["window_id"]): x for x in act}
        Q = np.zeros(case["G"])
        for j in range(case["n"]):
            b = np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
            b = b / b.sum()
            w = b + O.KAPPA * (case["M"][j].T @ Q)
            hi, eb = case["a_bar"][j], case["e_bar"][j]
            x = slsqp_project(w, hi, 1.0 / eb)
            if x is None:
                print("NONE", ds, seed, j)
                continue
            n += 1
            worst_f = max(worst_f, O.feasibility(x, hi, 1.0 / eb))
            worst_k = max(worst_k, kkt_stat(x, w, hi))
            Q = np.maximum(Q + O.ETA_DEBT * (case["mu"] - case["M"][j] @ x), 0.0)
print("n=%d worst feasibility=%.3e worst stationarity=%.3e" % (n, worst_f, worst_k))
