"""Debug: trace the ball-active projection branch (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51_oracle as O                                                        # noqa: E402

rng = np.random.default_rng(11)
for trial in range(60):
    K = int(rng.integers(2, 10))
    ab, eb = 0.5, 3.0
    v = rng.random(K) * rng.choice([0.2, 1.0, 5.0])
    a, lam, act = O.project_Cr(v, ab, eb)
    if act != "cap_simplex_repair":
        continue
    print("trial", trial, "K", K, "v", v)
    target = 1.0 / eb
    x0 = O._capped_simplex(v, ab)
    print("  x0", x0, "sum", x0.sum(), "n2", float(x0 @ x0), "target", target)
    lo, hi_l = 0.0, 1.0
    for it in range(200):
        n2, _ = O._norm2_capped(v, ab, hi_l)
        if n2 <= target:
            break
        hi_l *= 2.0
    print("  bracket lo=%g hi=%g  n2(lo)=%g n2(hi)=%g" %
          (lo, hi_l, O._norm2_capped(v, ab, lo)[0], O._norm2_capped(v, ab, hi_l)[0]))
    for it in range(200):
        mid = 0.5 * (lo + hi_l)
        n2, _ = O._norm2_capped(v, ab, mid)
        if n2 > target:
            lo = mid
        else:
            hi_l = mid
        if hi_l - lo <= 1e-17 * max(1.0, hi_l):
            break
    lam2 = 0.5 * (lo + hi_l)
    x = O._clip(v / (1.0 + 2.0 * lam2), ab)
    print("  lam=%g iters=%d x=%s sum=%r n2=%r" %
          (lam2, it, x, x.sum(), float(x @ x)))
    break
