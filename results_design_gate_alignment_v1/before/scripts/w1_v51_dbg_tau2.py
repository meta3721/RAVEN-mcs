"""Debug: trace _tau_for against the inline bisection (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51_oracle as O                                                        # noqa: E402

rng = np.random.default_rng(7)
for trial in range(200):
    K = int(rng.integers(2, 9))
    hi = 0.5
    v = rng.random(K) * rng.choice([0.5, 1.0, 3.0, 10.0])
    if hi * K <= 1.0 or float(O._clip(v, hi).sum()) < 1.0 - 1e-15:
        continue
    tau = O._tau_for(v, hi)
    x = O._clip(v - tau, hi)
    if abs(float(x.sum()) - 1.0) > 1e-12:
        print("FAIL K=%d sum=%.17f tau=%.17g" % (K, x.sum(), tau))
        print("  v =", v)
        print("  clip(v,hi) =", O._clip(v, hi), " sum=", float(O._clip(v, hi).sum()))
        # manual bracketing
        lo, hi_t = 0.0, float(np.max(v))
        for it in range(200):
            mid = 0.5 * (lo + hi_t)
            s = float(O._clip(v - mid, hi).sum())
            if s > 1.0:
                lo = mid
            else:
                hi_t = mid
            if hi_t - lo <= 1e-17 * max(1.0, abs(hi_t)):
                break
        tm = 0.5 * (lo + hi_t)
        print("  manual tau=%.17g sum=%.17f iters=%d" %
              (tm, float(O._clip(v - tm, hi).sum()), it))
        print("  tau equal?", tau == tm, " diff=", abs(tau - tm))
        break
else:
    print("no failure")
