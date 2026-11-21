"""Debug: validate project_Cr on general vectors (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import w1_v51_oracle as O                                                        # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound          # noqa: E402

rng = np.random.default_rng(11)
bad = 0
n = 0
for trial in range(60):
    K = int(rng.integers(2, 10))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.2, 1.0, 5.0])
    a, lam, act = O.project_Cr(v, ab, eb)
    n += 1
    s = float(a.sum())
    n2 = float(a @ a)
    feas = O.feasibility(a, ab, eb)
    x_cvx, status, tier = O.cvxpy_proj(v, ab, eb, K)
    x_pb = O.project_back(x_cvx, ab, eb)
    o_or = O.proj_objective(a, v)
    o_cv = O.proj_objective(x_pb, v)
    flag = (abs(s - 1.0) > 1e-14) or feas > 1e-13 or (o_or > o_cv + 1e-12)
    if flag:
        bad += 1
    print("K=%-3d act=%-18s sum=%.17f n2=%.10f feas=%.2e obj_or=%.10f obj_cv=%.10f "
          "gap=%.2e tier=%d %s"
          % (K, act, s, n2, feas, o_or, o_cv, o_or - o_cv, tier, "BAD" if flag else "ok"))
    if bad >= 4:
        print("  v=", v, " lam=", lam)
        break
print("bad %d / %d" % (bad, n))
print("--- uniform control detail")
for K in (1, 2, 3, 4, 5, 6, 8, 16, 32, 64):
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    u = np.full(K, 1.0 / K)
    a, lam, act = O.project_Cr(u, ab, eb)
    print("K=%-4d act=%-16s tau=%.17g maxdiff=%.3e" %
          (K, act, O._tau_for(u, ab), float(np.max(np.abs(a - u)))))
