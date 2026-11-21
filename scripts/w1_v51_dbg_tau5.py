"""Debug: print the exact solve_tau internals (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51_oracle as O                                                        # noqa: E402

v = np.full(3, 1.0 / 3.0)
hi = 0.5
print("v", repr(v), "hi", hi)
print("br", repr(np.unique(np.concatenate([v, v - hi]))))
print("clip(v,hi).sum", repr(float(O._clip(v, hi).sum())))
br = np.unique(np.concatenate([v, v - hi]))
for k in range(br.size - 1, -1, -1):
    a = float(br[k])
    print(" k=%d a=%r f(a)=%r" % (k, a, float(O._clip(v - a, hi).sum())))
print("solve_tau", repr(O.solve_tau(v, hi)))
lo = float(np.min(v)) - hi
up = float(np.max(v))
for k in range(br.size - 1, -1, -1):
    a = float(br[k])
    if float(O._clip(v - a, hi).sum()) >= 1.0:
        lo = a
        up = float(br[k + 1]) if k + 1 < br.size else up
        print("  chosen k=%d lo=%r up=%r" % (k, lo, up))
        break
x_lo = O._clip(v - lo, hi)
print("x_lo", repr(x_lo), "sum", repr(float(x_lo.sum())))
free = (x_lo > 0.0) & (x_lo < hi)
print("free", free, "n_free", int(free.sum()))
cap_mass = float(((v - lo) >= hi).sum()) * hi
print("cap_mass", repr(cap_mass), "mean_free", repr(float(v[free].mean())))
tau = float(v[free].mean()) - (1.0 - cap_mass) / float(free.sum())
print("tau", repr(tau), "in bracket", lo <= tau <= up)
