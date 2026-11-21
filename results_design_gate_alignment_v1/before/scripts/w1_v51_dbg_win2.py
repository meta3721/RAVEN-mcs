"""Minimal: what IS the projection of beta/ at window 2?"""
from __future__ import annotations

import sys

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")
import w1_v51_oracle as O                                                      # noqa: E402

v = np.array([0.60251761, 0.18532680, 0.21215559])
hi, target = 0.5, 1.0 / 3.0


def obj(x):
    return float(((x - v) ** 2).sum())


cons = [{"type": "eq", "fun": lambda x: float(np.sum(x)) - 1.0},
        {"type": "ineq", "fun": lambda x: target - float(x @ x)}]
best = None
for s in (np.full(3, 1 / 3), np.clip(v, 0, hi), np.array([0.4, 0.3, 0.3])):
    r = minimize(obj, s, method="SLSQP", bounds=[(0.0, hi)] * 3, constraints=cons,
                 options={"maxiter": 800, "ftol": 1e-18})
    f = O.feasibility(r.x, hi, target)
    print("  start=%s -> x=%s obj=%.12f feas=%.2e" % (np.round(s, 4), np.round(r.x, 8),
                                                      obj(r.x), f))
    if f <= 1e-12 and (best is None or obj(r.x) < best[0]):
        best = (obj(r.x), r.x.copy())
uni = np.full(3, 1 / 3)
print("uniform obj=%.12f feas=%.2e" % (obj(uni), O.feasibility(uni, hi, target)))
o, kind, mult = O.project_Cr(v, hi, 3.0)
print("oracle  x=%s obj=%.12f kind=%s feas=%.2e" % (np.round(o, 8), obj(o), kind,
                                                    O.feasibility(o, hi, target)))
print("SLSQP best: %s obj=%.12f" % (np.round(best[1], 8), best[0]))
