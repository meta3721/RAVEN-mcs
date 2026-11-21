"""Scratch v2: robust projection onto C_r = {sum=1, 0<=x<=hi, ||x||^2<=target}."""
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


def _feas(x, hi, target):
    return max(abs(float(x.sum()) - 1.0), float(max(0.0, -x.min())),
               float(max(0.0, float(x.max()) - hi)),
               float(max(0.0, float(x @ x) - target)))


def _candidates(v, hi, target, max_kc=3):
    """Active-set candidates x = tau' + lam' v with kc capped and nz zeroed coordinates."""
    K = int(v.size)
    order = np.argsort(-v, kind="stable")
    out = []
    for kc in range(0, min(max_kc, K - 1) + 1):
        cap_idx = order[:kc]
        rest = order[kc:]
        for nz in range(0, K - kc):
            nf = K - kc - nz
            free_idx = rest[:nf]
            zero_idx = rest[nf:]
            s_f = float(v[free_idx].sum())
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
                out.append(x)
    return out


def _dykstra(v, hi, target, iters=200000):
    """Alternating projection onto the capped simplex and the closed ball, tracking the
    best FEASIBLE iterate seen (Dykstra itself does not stay feasible)."""
    x = capped_simplex(v, hi)
    if x is None:
        return None
    p = np.zeros_like(x)
    q = np.zeros_like(x)
    best = None
    for _ in range(iters):
        y = capped_simplex(x + p, hi)
        if y is None:
            break
        p = x + p - y
        z = y + q
        nrm = float(np.linalg.norm(z))
        x_new = z * min(1.0, math.sqrt(target) / nrm) if nrm > 0 else z
        q = z - x_new
        if abs(float(x_new.sum()) - 1.0) <= 1e-13 and _feas(x_new, hi, target) <= 1e-13:
            score = float(((x_new - v) ** 2).sum())
            if best is None or score < best[0]:
                best = (score, x_new.copy())
        if float(np.max(np.abs(x_new - x))) <= 1e-16:
            break
        x = x_new
    return None if best is None else best[1]


def project_Cr(v, a_bar, e_bar):
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
    cands = _candidates(v, hi, target)
    good = [x for x in cands if _feas(x, hi, target) <= 1e-11]
    if good:
        x = min(good, key=lambda a: float(((a - v) ** 2).sum()))
        return x, "ball"
    xd = _dykstra(v, hi, target)
    if xd is not None:
        return xd, "ball_dykstra"
    # last resort: the feasible point with the smallest distance found on the ball surface
    order = np.argsort(-v)
    x = np.clip(v, 0.0, None)
    x = x / x.sum()
    x = _clip(x / float(np.linalg.norm(x)) * math.sqrt(target), hi)
    return x, "fallback"


if __name__ == "__main__":
    import pathlib
    import sys
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "src"))
    from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
    rng = np.random.default_rng(2026)
    bad = 0
    n = 0
    kinds = {}
    for trial in range(600):
        K = int(rng.integers(2, 16))
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        v = rng.random(K) * rng.choice([0.05, 0.3, 1.0, 4.0])
        v = v / v.sum() * float(rng.choice([0.8, 1.0, 1.5, 3.0]))
        a, act = project_Cr(v, ab, eb)
        n += 1
        kinds[act] = kinds.get(act, 0) + 1
        feas = _feas(a, ab, 1.0 / eb)
        if feas > 1e-12:
            bad += 1
            if bad < 6:
                print("BAD K=%d act=%s feas=%.3e" % (K, act, feas))
    print("bad %d/%d kinds=%s" % (bad, n, kinds))
    worst = 0.0
    for K in range(1, 65):
        ab = float(alpha_bar(alpha_max=0.5, n_active=K))
        eb = float(ess_ball_bound(e_min=3.0, n_active=K))
        u = np.full(K, 1.0 / K)
        a, act = project_Cr(u, ab, eb)
        worst = max(worst, float(np.max(np.abs(a - u))))
    print("uniform control worst diff:", worst)
