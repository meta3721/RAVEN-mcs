"""Debug: final oracle validation (throwaway)."""
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
bad_feas = bad_obj = n = 0
worst_feas = 0.0
worst_gap = -np.inf
for trial in range(80):
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
    gap = O.proj_objective(a, v) - O.proj_objective(x_pb, v)
    worst_gap = max(worst_gap, gap)
    bad_feas += feas > 1e-13
    bad_obj += gap > 1e-12
    if feas > 1e-13 or gap > 1e-12:
        print("  BAD K=%-3d act=%-10s feas=%.2e gap=%.3e" % (K, act, feas, gap))
print("proj: feas fail %d/%d (worst %.2e), obj fail %d/%d (worst gap %.2e)"
      % (bad_feas, n, worst_feas, bad_obj, n, worst_gap))

bad2 = n2 = 0
wf2 = 0.0
for trial in range(40):
    K = int(rng.integers(2, 9))
    G = 8
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    b = rng.random(K)
    b = b / b.sum()
    M = rng.random((G, K))
    M = M / M.sum(axis=1, keepdims=True)
    Q = np.abs(rng.normal(size=G)) * float(rng.choice([0.01, 0.05, 0.3]))
    v = b + 1000.0 * (M.T @ Q)
    a, lam, act = O.project_Cr(v, ab, eb)
    n2 += 1
    feas = O.feasibility(a, ab, eb)
    wf2 = max(wf2, feas)
    x_cvx, status, tier = O.cvxpy_debt(b, M, Q, ab, eb)
    x_pb = O.project_back(x_cvx, ab, eb)
    gap = O.debt_objective(a, b, M, Q) - O.debt_objective(x_pb, b, M, Q)
    if feas > 1e-13 or gap > 1e-12:
        bad2 += 1
        print("  DEBT BAD K=%-3d feas=%.2e gap=%.3e act=%s" % (K, feas, gap, act))
print("debt: fail %d/%d (worst feas %.2e)" % (bad2, n2, wf2))
