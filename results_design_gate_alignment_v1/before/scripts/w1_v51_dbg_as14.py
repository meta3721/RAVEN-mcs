"""Diagnostic for the interior-point solver, then finalise the oracle projection."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_v51_dbg_as13 as P                                                      # noqa: E402
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound          # noqa: E402

rng = np.random.default_rng(5)
shown = 0
for trial in range(300):
    K = int(rng.integers(2, 12))
    ab = float(alpha_bar(alpha_max=0.5, n_active=K))
    eb = float(ess_ball_bound(e_min=3.0, n_active=K))
    v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
    v = v / v.sum() * float(rng.choice([0.9, 1.0, 1.5, 4.0]))
    x, kind, mult = P.project_Cr(v, ab, eb)
    if kind != "residual":
        continue
    shown += 1
    if shown > 2:
        break
    tgt = 1.0 / eb
    print("trial=%d K=%d hi=%.4f tgt=%.6f v=%s" % (trial, K, ab, tgt, np.round(v, 6)))
    print("  x=%s sum=%.12f n2=%.12f feas=%.3e" %
          (np.round(x, 8), x.sum(), float(x @ x), P.feasibility(x, ab, tgt)))
    # where is it stuck? run the stages manually with reporting
    z = np.ones(K)
    s2 = tgt * 0.8
    disc = 1.0 - s2 * K
    eps = min(0.45, (1.0 - np.sqrt(max(disc, 0.0))) / max(K, 1))
    xx = np.clip(eps * np.ones(K) + (1.0 - K * eps) * (np.ones(K) / K), 1e-9, ab - 1e-9)
    print("  start x sum=%.12f n2=%.12f frac=%.6f" % (xx.sum(), float(xx @ xx), tgt))
