"""Debug: focused exactness + feasibility checks for the oracle (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import w1_v51_oracle as O                                                        # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound          # noqa: E402

print("--- uniform control")
worst = 0.0
for K in range(1, 65):
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    u = np.full(K, 1.0 / K)
    a, lam, act = O.project_Cr(u, ab, eb)
    d = float(np.max(np.abs(a - u)))
    worst = max(worst, d)
    if K in (1, 2, 3, 4, 5, 6, 8, 16, 32, 64) or d > 0:
        print("  K=%-3d act=%-14s maxdiff=%.3e" % (K, act, d))
print("  worst maxdiff over K=1..64:", worst)

print("--- general random vectors: feasibility + optimality vs CVXPY")
rng = np.random.default_rng(2026)
bad_feas = bad_obj = 0
n = 0
for trial in range(40):
    K = int(rng.integers(2, 12))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
    v = v / v.sum() * float(rng.choice([0.5, 1.0, 2.0]))
    a, lam, act = O.project_Cr(v, ab, eb)
    n += 1
    feas = O.feasibility(a, ab, eb)
    x_cvx, status, tier = O.cvxpy_proj(v, ab, eb, K)
    x_pb = O.project_back(x_cvx, ab, eb)
    o_or = O.proj_objective(a, v)
    o_cv = O.proj_objective(x_pb, v)
    if feas > 1e-13:
        bad_feas += 1
    if o_or > o_cv + 1e-12:
        bad_obj += 1
    if feas > 1e-13 or o_or > o_cv + 1e-12 or trial < 6:
        print("  K=%-3d act=%-10s sum=%.17g n2=%.12f feas=%.2e gap=%.3e %s" %
              (K, act, float(a.sum()), float(a @ a), feas, o_or - o_cv,
               "BAD" if (feas > 1e-13 or o_or > o_cv + 1e-12) else "ok"))
print("  feasibility failures %d/%d, optimality failures %d/%d" % (bad_feas, n, bad_obj, n))
