"""Debug: trace _proj_ball (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51_oracle as O                                                        # noqa: E402

v = np.array([0.09985557, 0.12029967, 0.00573780])
hi, eb = 0.5, 3.0
target = 1.0 / eb
x0 = O._capped_simplex(v, hi)
print("x0", x0, "sum", x0.sum(), "n2", float(x0 @ x0), "target", target)
x, lam = O._proj_ball(v, hi, target)
print("lam", lam)
print("x ", x, "sum", float(x.sum()), "n2", float(x @ x))
a, lam2, act = O.project_Cr(v, hi, eb)
print("project_Cr", a, "act", act, "sum", float(a.sum()), "feas", O.feasibility(a, hi, eb))
for lam_t in (0.0, 1e-6, 1e-3, 0.01, 0.1, 1.0, 10.0):
    tau = O._tau_for(v / (1 + 2 * lam_t), hi)
    c = O._clip((v - tau) / (1 + 2 * lam_t), hi)
    print("  lam=%-8g tau=%-12.6g x=%s sum=%.10f n2=%.10f" %
          (lam_t, tau, np.round(c, 6), c.sum(), float(c @ c)))
