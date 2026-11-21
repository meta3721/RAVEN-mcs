"""Debug: oracle validation on the vector class the oracle is defined for (sum >= 1)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import w1_v51_oracle as O                                                        # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound          # noqa: E402

rng = np.random.default_rng(2026)
bad_feas = bad_obj = 0
n = 0
worst_feas = 0.0
worst_gap = -np.inf
for trial in range(60):
    K = int(rng.integers(2, 14))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
    v = v / v.sum() * float(rng.choice([1.0, 1.5, 3.0]))
    a, lam, act = O.project_Cr(v, ab, eb)
    n += 1
    feas = O.feasibility(a, ab, eb)
    worst_feas = max(worst_feas, feas)
    x_cvx, status, tier = O.cvxpy_proj(v, ab, eb, K)
    x_pb = O.project_back(x_cvx, ab, eb)
    o_or = O.proj_objective(a, v)
    o_cv = O.proj_objective(x_pb, v)
    gap = o_or - o_cv
    worst_gap = max(worst_gap, gap)
    if feas > 1e-13:
        bad_feas += 1
    if gap > 1e-12:
        bad_obj += 1
    if feas > 1e-13 or gap > 1e-12 or trial < 8:
        print("  K=%-3d act=%-10s sum=%.17g n2=%.12f feas=%.2e gap=%.3e %s" %
              (K, act, float(a.sum()), float(a @ a), feas, gap,
               "BAD" if (feas > 1e-13 or gap > 1e-12) else "ok"))
print("  feasibility failures %d/%d (worst %.2e), optimality failures %d/%d (worst gap %.2e)"
      % (bad_feas, n, worst_feas, bad_obj, n, worst_gap))

# debt-style inputs: v = beta/kappa-sum + kappa * M^T Q with realistic scale
bad2 = 0
for trial in range(20):
    K = int(rng.integers(2, 9))
    G = 8
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    b = rng.random(K)
    b = b / b.sum()
    M = rng.random((G, K))
    M = M / M.sum(axis=1, keepdims=True)
    Q = np.abs(rng.normal(size=G)) * 0.05
    v = b + 1000.0 * (M.T @ Q)
    a, lam, act = O.project_Cr(v, ab, eb)
    feas = O.feasibility(a, ab, eb)
    x_cvx, status, tier = O.cvxpy_debt(b, M, Q, ab, eb)
    x_pb = O.project_back(x_cvx, ab, eb)
    o_or = O.debt_objective(a, b, M, Q)
    o_cv = O.debt_objective(x_pb, b, M, Q)
    gap = o_or - o_cv
    if feas > 1e-13 or gap > 1e-12:
        bad2 += 1
        print("  DEBT K=%-3d feas=%.2e gap=%.3e act=%s tier=%d status=%s" %
              (K, feas, gap, act, tier, status))
print("  debt-objective failures %d/20" % bad2)
