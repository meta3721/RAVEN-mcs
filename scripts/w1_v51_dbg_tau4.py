"""Debug: trace _tau_for on one concrete vector (throwaway)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51_oracle as O                                                        # noqa: E402

v = np.array([0.09985557, 0.12029967, 0.00573780])
hi = 0.5
print("v        =", repr(v))
print("sum(v)   =", repr(float(v.sum())))
print("min- hi  =", repr(float(v.min() - hi)), " max =", repr(float(v.max())))
print("f(lo)    =", repr(float(O._clip(v - (v.min() - hi), hi).sum())))
print("f(up)    =", repr(float(O._clip(v - v.max(), hi).sum())))
print("_tau_for =", repr(O._tau_for(v, hi)))
print("_tau_exact =", repr(O._tau_exact(v, hi)))
x = O._capped_simplex(v, hi)
print("x        =", repr(x), "sum =", repr(float(x.sum())))
print("br       =", repr(np.unique(np.concatenate([v, v - hi]))))
