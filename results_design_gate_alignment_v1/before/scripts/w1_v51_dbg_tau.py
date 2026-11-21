"""Debug the capped-simplex tau solve (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from w1_v51_oracle import _clip                                                      # noqa: E402

rng = np.random.default_rng(7)
fails = 0
for trial in range(200):
    K = int(rng.integers(2, 9))
    hi = 0.5
    v = rng.random(K) * rng.choice([0.5, 1.0, 3.0, 10.0])
    if hi * K <= 1.0 or float(_clip(v, hi).sum()) < 1.0 - 1e-15:
        continue
    lo, hi_t = 0.0, float(np.max(v))
    for _ in range(200):
        mid = 0.5 * (lo + hi_t)
        s = float(_clip(v - mid, hi).sum())
        if s > 1.0:
            lo = mid
        else:
            hi_t = mid
        if hi_t - lo <= 1e-17 * max(1.0, abs(hi_t)):
            break
    tau = 0.5 * (lo + hi_t)
    x = _clip(v - tau, hi)
    if abs(float(x.sum()) - 1.0) > 1e-12:
        fails += 1
        if fails < 6:
            print("FAIL K=%d sum=%.17f tau=%.17g lo=%.17g hi_t=%.17g" %
                  (K, x.sum(), tau, lo, hi_t))
            print("  v=", v)
            print("  s(lo)=%.17f s(hi_t)=%.17f maxv=%.17g" %
                  (float(_clip(v - lo, hi).sum()), float(_clip(v - hi_t, hi).sum()), np.max(v)))
            # is the true root at a cap plateau?
            print("  clip(v,hi).sum=", float(_clip(v, hi).sum()))
print("fails:", fails)
