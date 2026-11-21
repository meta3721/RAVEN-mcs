"""Debug: reproduce a failing project_Cr call exactly (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51_oracle as O                                                        # noqa: E402

for seed in (7, 11, 23):
    rng = np.random.default_rng(seed)
    for trial in range(300):
        K = int(rng.integers(2, 9))
        ab, eb = 0.5, 3.0
        v = rng.random(K) * rng.choice([0.5, 1.0, 3.0, 10.0])
        a, lam, act = O.project_Cr(v, ab, eb)
        s = float(a.sum())
        if abs(s - 1.0) > 1e-12:
            print("REPRO seed=%d trial=%d K=%d act=%s sum=%.17g lam=%g" %
                  (seed, trial, K, act, s, lam))
            print("  v =", repr(v))
            print("  sum(v)=", v.sum(), " clip(v,hi).sum=", float(O._clip(v, ab).sum()))
            x0 = O._capped_simplex(v, ab)
            print("  x0 =", repr(x0), " sum=", x0.sum(), " n2=", float(x0 @ x0))
            print("  tau_for=", O._tau_for(v, ab))
            raise SystemExit
print("no reproduction")
