"""Scratch: verified active-set projection onto C_r (to be pasted into w1_v51_oracle.py)."""
from __future__ import annotations

import math

import numpy as np


def _clip(x, hi):
    return np.minimum(np.maximum(x, 0.0), hi)


def _clip_sum(v, hi):
    v = np.asarray(v, dtype=float)
    return float(np.maximum(v, 0.0).sum()) - float(np.maximum(v - hi, 0.0).sum())


def solve_tau(v, hi, tol=1e-12):
    v = np.asarray(v, dtype=float)
    if _clip_sum(v, hi) < 1.0 - tol:
        return None
    lo = float(np.min(v)) - hi
    up = float(np.max(v))
    for _ in range(200):
        mid = 0.5 * (lo + up)
        if _clip_sum(v - mid, hi) > 1.0:
            lo = mid
        else:
            up = mid
        if up - lo <= 1e-17 * max(1.0, abs(up)):
            break
    return 0.5 * (lo + up)


def capped_simplex(v, hi):
    v = np.asarray(v, dtype=float)
    tau = solve_tau(v, hi)
    if tau is None:
        return None
    return _clip(v - tau, hi)


def project_Cr(v, a_bar, e_bar):
    """Exact Euclidean projection onto {sum x = 1, 0 <= x <= a_bar, ||x||^2 <= 1/e_bar}."""
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    target = 1.0 / float(e_bar)
    if K == 1 or hi * K <= 1.0 + 1e-15 or target >= float(K):
        return np.full(K, 1.0 / K), "degenerate"
    x0 = capped_simplex(v, hi)
    if x0 is None:
        return np.full(K, 1.0 / K), "degenerate_infeasible"
    if float(x0 @ x0) <= target:
        return x0, "cap_simplex"
    order = np.argsort(-v, kind="stable")
    best = None
    for kc in (0, 1):
        if kc > K:
            continue
        cap_idx = order[:kc]
        rest = order[kc:]
        rhs = target - kc * hi * hi
        if rhs <= 0.0:
            continue
        for nz in range(0, K - kc + 1):
            nf = K - kc - nz
            if nf < 1:
                continue
            free_idx = rest[:nf]
            zero_idx = rest[nf:]
            s_f = float(v[free_idx].sum())
            q_f = float((v[free_idx] ** 2).sum())
            bb = 1.0 - kc * hi
            disc = bb * bb + 4.0 * nf * (target - kc * hi * hi)
            if disc < 0.0:
                continue
            root = math.sqrt(disc)
            for lam_p in ((bb + root) / (2.0 * nf), (bb - root) / (2.0 * nf)):
                if lam_p < -1e-12:
                    continue
                tau_p = (1.0 - lam_p * s_f) / float(nf)
                x = np.empty(K)
                x[free_idx] = tau_p + lam_p * v[free_idx]
                x[cap_idx] = hi
                x[zero_idx] = 0.0
                if zero_idx.size and float(np.max(v[zero_idx])) > tau_p + 1e-12:
                    continue
                if cap_idx.size and float(np.min(v[cap_idx])) < tau_p + 2.0 * lam_p * hi - 1e-12:
                    continue
                if np.any(x[free_idx] < -1e-12) or np.any(x[free_idx] > hi + 1e-12):
                    continue
                if abs(float(x.sum()) - 1.0) > 1e-13:
                    continue
                if float(x @ x) > target + 1e-10:
                    continue
                score = float(((x - v) ** 2).sum())
                if best is None or score < best[0]:
                    best = (score, x)
    if best is None:
        return None, "no_candidate"
    return best[1], "ball"


if __name__ == "__main__":
    rng = np.random.default_rng(2026)
    from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
    import sys
    sys.path.insert(0, "src")
    bad = 0
    n = 0
    for trial in range(200):
        K = int(rng.integers(2, 14))
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
        v = v / v.sum() * float(rng.choice([1.0, 1.5, 3.0]))
        a, act = project_Cr(v, ab, eb)
        n += 1
        feas = max(abs(float(a.sum()) - 1.0), float(max(0.0, -a.min())),
                   float(max(0.0, a.max() - ab)),
                   float(max(0.0, float(a @ a) - 1.0 / eb)))
        if feas > 1e-13 or act in ("no_candidate", "cap_simplex_fallback"):
            bad += 1
            print("BAD K=%d act=%s feas=%.3e a=%s" % (K, act, feas, np.round(a, 8)))
    print("bad %d/%d" % (bad, n))
    for K in range(1, 40):
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        u = np.full(K, 1.0 / K)
        a, act = project_Cr(u, ab, eb)
        d = float(np.max(np.abs(a - u)))
        if d > 0:
            print("uniform K=%d d=%.3e act=%s" % (K, d, act))
    print("uniform control done")
