"""Isolate the capped-simplex breakpoint bug (development diagnostic; writes nothing)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51a_oracle as O                                                     # noqa: E402

np.set_printoptions(precision=18, linewidth=200)

v = np.array([4.411735987872421, 1.4097715207533623, 2.146234426858083])
hi = 0.5
order = np.argsort(-v, kind="stable")
vs = v[order]
F = np.concatenate([np.cumsum(vs[::-1])[::-1], np.zeros(1)])
print("v ", v)
print("vs", vs, "order", order)
print("F ", F)
K = v.size
for m in range(0, K):
    n = K - m
    tau = (float(F[m]) - 1.0) / float(n)
    m_ok = (m == 0) or (float(vs[m - 1]) >= tau)
    zero_ok = (m == K - 1) or (float(vs[m + 1]) <= tau)
    print("m=%d n=%d tau=%.18g m_ok=%s zero_ok=%s" % (m, n, tau, m_ok, zero_ok))
x, tau, kind = O.capped_simplex(v, hi)
print("capped_simplex ->", x, tau, kind)
xb, taub, kb = O._capped_simplex_bisect(v, hi)
print("bisect        ->", xb, taub, kb)
