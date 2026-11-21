"""Debug the v5.1 projection oracle against CVXPY (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import w1_v51_oracle as O                                                        # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound          # noqa: E402

rng = np.random.default_rng(7)
bad = 0
for trial in range(40):
    K = int(rng.integers(2, 9))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.5, 1.0, 3.0, 10.0])
    a, lam, act = O.project_Cr(v, ab, eb)
    x_cvx, status = O.cvxpy_proj(v, ab, eb, K)
    print("K=%d ab=%.4f eb=%.4f act=%-16s lam=%.3e S=%.16f n2=%.16f tgt=%.16f "
          "dcvx=%.3e status=%s"
          % (K, ab, eb, act, lam, a.sum(), float(a @ a), 1.0 / eb,
             float(np.max(np.abs(a - x_cvx))), status))
    if float(np.max(np.abs(a - x_cvx))) > 1e-9:
        bad += 1
        print("   oracle:", a)
        print("   cvxpy :", x_cvx)
print("bad:", bad)
# uniform control, exact
for K in (1, 2, 3, 4, 5, 6, 8, 16, 32, 64, 128):
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    u = np.full(K, 1.0 / K)
    a, lam, act = O.project_Cr(u, ab, eb)
    print("uniform K=%-4d act=%-14s maxdiff=%.3e sum=%.17f" %
          (K, act, float(np.max(np.abs(a - u))), a.sum()))
