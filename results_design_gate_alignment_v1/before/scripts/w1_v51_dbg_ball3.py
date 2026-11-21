"""Debug: instrument _proj_ball (throwaway)."""
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
for trial in range(80):
    K = int(rng.integers(2, 14))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
    v = v / v.sum() * float(rng.choice([1.0, 1.5, 3.0]))
    a, lam, act = O.project_Cr(v, ab, eb)
    if act != "cap_simplex_fallback":
        continue
    target = 1.0 / eb
    print("trial %d K=%d ab=%.4f eb=%.4f target=%.6f" % (trial, K, ab, eb, target))
    print("  v=", v, " S_pos=", float(np.maximum(v, 0).sum()))
    lam_ceil = 0.5 * (float(np.maximum(v, 0).sum()) - 1.0)
    print("  lam_ceil=%.6g" % lam_ceil)
    for lam_t in (0.0, 0.1 * lam_ceil, 0.5 * lam_ceil, 0.9 * lam_ceil, lam_ceil,
                  float(np.nextafter(lam_ceil, 0.0))):
        w = v / (1 + 2 * lam_t)
        cs = O._clip_sum(w, ab)
        x = O._capped_simplex(w, ab)
        print("    lam=%-12.6g clip_sum=%.10f x=%s n2=%s" %
              (lam_t, cs, "None" if x is None else np.round(x, 8),
               "None" if x is None else "%.10f" % float(x @ x)))
    break
